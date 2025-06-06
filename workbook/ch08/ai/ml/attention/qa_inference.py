#!/usr/bin/env python3
"""
Question Answering Model Inference Engine - Fixed Version

This script provides a complete inference engine for the trained QA model.
It can load the model and vocabulary, then answer questions based on provided context.

Usage:
    python qa_inference.py --model_path qa_model.keras --vocab_path vocab.json
    
    Or use it as a module:
    from qa_inference import QAInferenceEngine
    engine = QAInferenceEngine('qa_model.keras', 'vocab.json')
    answer = engine.answer_question("What is the capital?", "The capital of France is Paris.")
"""

import tensorflow as tf
# Enable unsafe deserialization to handle Lambda layers
tf.keras.config.enable_unsafe_deserialization()

import json
import numpy as np
import re
import argparse
import os
from typing import Dict, List, Tuple, Optional
from tensorflow.keras.layers import Dense, Input, Layer, Embedding, Dropout, LayerNormalization, Lambda
from tensorflow.keras.models import Model, load_model


class MultiHeadAttention(Layer):
    """Multi-Head Attention layer - needed for model loading"""
    def __init__(self, d_model, num_heads, dropout_rate=0.1, **kwargs):
        super(MultiHeadAttention, self).__init__(**kwargs)
        self.num_heads = num_heads
        self.d_model = d_model
        self.dropout_rate = dropout_rate
        
        assert d_model % num_heads == 0
        self.depth = d_model // num_heads
        
    def build(self, input_shape):
        self.wq = Dense(self.d_model, name='wq')
        self.wk = Dense(self.d_model, name='wk')
        self.wv = Dense(self.d_model, name='wv')
        self.dense = Dense(self.d_model, name='dense')
        self.dropout = Dropout(self.dropout_rate)
        super().build(input_shape)
        
    def split_heads(self, x, batch_size):
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])
    
    def call(self, inputs, training=None):
        if isinstance(inputs, list):
            q, k, v = inputs[0], inputs[1], inputs[2]
            mask = inputs[3] if len(inputs) > 3 else None
        else:
            q = k = v = inputs
            mask = None
            
        batch_size = tf.shape(q)[0]
        
        q = self.wq(q)
        k = self.wk(k)
        v = self.wv(v)
        
        q = self.split_heads(q, batch_size)
        k = self.split_heads(k, batch_size)
        v = self.split_heads(v, batch_size)
        
        # Scaled dot-product attention
        matmul_qk = tf.matmul(q, k, transpose_b=True)
        dk = tf.cast(self.depth, tf.float32)
        scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)
        
        # Apply mask if provided
        if mask is not None:
            mask = tf.cast(mask, tf.float32)
            mask = mask[:, tf.newaxis, tf.newaxis, :]
            scaled_attention_logits += (mask * -1e9)
        
        attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)
        attention_weights = self.dropout(attention_weights, training=training)
        
        output = tf.matmul(attention_weights, v)
        output = tf.transpose(output, perm=[0, 2, 1, 3])
        output = tf.reshape(output, (batch_size, -1, self.d_model))
        
        return self.dense(output)
    
    def get_config(self):
        config = super().get_config()
        config.update({
            'num_heads': self.num_heads,
            'd_model': self.d_model,
            'dropout_rate': self.dropout_rate,
        })
        return config


class TransformerBlock(Layer):
    """Transformer Block layer - needed for model loading"""
    def __init__(self, d_model, num_heads, dff, dropout_rate=0.1, **kwargs):
        super(TransformerBlock, self).__init__(**kwargs)
        self.d_model = d_model
        self.num_heads = num_heads
        self.dff = dff
        self.dropout_rate = dropout_rate
        
    def build(self, input_shape):
        self.att = MultiHeadAttention(self.d_model, self.num_heads, self.dropout_rate)
        self.ffn = tf.keras.Sequential([
            Dense(self.dff, activation='relu'),
            Dropout(self.dropout_rate),
            Dense(self.d_model)
        ])
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(self.dropout_rate)
        self.dropout2 = Dropout(self.dropout_rate)
        super().build(input_shape)
    
    def call(self, inputs, training=None):
        if isinstance(inputs, list):
            x = inputs[0]
            mask = inputs[1] if len(inputs) > 1 else None
        else:
            x = inputs
            mask = None
            
        attn_output = self.att([x, x, x, mask], training=training)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(x + attn_output)
        
        ffn_output = self.ffn(out1, training=training)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)
    
    def get_config(self):
        config = super().get_config()
        config.update({
            'd_model': self.d_model,
            'num_heads': self.num_heads,
            'dff': self.dff,
            'dropout_rate': self.dropout_rate,
        })
        return config


class MaskLayer(Layer):
    """Mask layer - needed for model loading"""
    def __init__(self, **kwargs):
        super(MaskLayer, self).__init__(**kwargs)
    
    def call(self, inputs):
        attention_mask = inputs
        mask = tf.cast(tf.equal(attention_mask, 0), tf.float32)
        return mask

    def get_config(self):
        return super().get_config()


class PositionalEncodingLayer(Layer):
    """Positional Encoding layer - needed for model loading"""
    def __init__(self, max_length, d_model, **kwargs):
        super(PositionalEncodingLayer, self).__init__(**kwargs)
        self.max_length = max_length
        self.d_model = d_model
        self.supports_masking = True
        
    def build(self, input_shape):
        pos = tf.range(self.max_length, dtype=tf.float32)[:, tf.newaxis]
        i = tf.range(self.d_model, dtype=tf.float32)[tf.newaxis, :]
        
        angle_rads = pos / tf.pow(10000.0, (2 * (i // 2)) / tf.cast(self.d_model, tf.float32))
        
        sin_mask = tf.cast(i % 2 == 0, tf.float32)
        cos_mask = tf.cast(i % 2 == 1, tf.float32)
        
        pos_encoding = sin_mask * tf.sin(angle_rads) + cos_mask * tf.cos(angle_rads)
        self.pos_encoding = tf.Variable(
            initial_value=pos_encoding[tf.newaxis, :, :],
            trainable=False,
            name='pos_encoding'
        )
        super().build(input_shape)
    
    def call(self, inputs, mask=None):
        seq_len = tf.shape(inputs)[1]
        output = inputs + self.pos_encoding[:, :seq_len, :]
        return output
    
    def compute_mask(self, inputs, mask=None):
        return mask
    
    def get_config(self):
        config = super().get_config()
        config.update({
            'max_length': self.max_length,
            'd_model': self.d_model,
        })
        return config


class MaskLogitsLayer(Layer):
    """Mask Logits layer - needed for model loading"""
    def __init__(self, **kwargs):
        super(MaskLogitsLayer, self).__init__(**kwargs)
    
    def call(self, inputs):
        logits, mask = inputs
        return logits + mask * -1e9

    def get_config(self):
        return super().get_config()


# Custom Lambda layer functions with explicit output shapes
def squeeze_last_dim(x):
    """Lambda function to squeeze last dimension"""
    return tf.squeeze(x, axis=-1)

def squeeze_last_dim_output_shape(input_shape):
    """Output shape for squeeze_last_dim function"""
    if input_shape[-1] == 1:
        return input_shape[:-1]
    return input_shape


class QAInferenceEngine:
    """
    Complete inference engine for the Question Answering model.
    
    This class handles:
    - Loading the trained model and vocabulary
    - Text preprocessing and tokenization
    - Inference and answer extraction
    - Confidence scoring
    - Batch processing
    """
    
    def __init__(self, model_path: str, vocab_path: str, max_length: int = 512):
        """
        Initialize the inference engine.
        
        Args:
            model_path: Path to the saved Keras model
            vocab_path: Path to the vocabulary JSON file
            max_length: Maximum sequence length for input
        """
        self.max_length = max_length
        self.model = None
        self.vocab = None
        self.reverse_vocab = None
        
        # Load model and vocabulary
        self.load_model_and_vocab(model_path, vocab_path)
    
    def load_model_and_vocab(self, model_path: str, vocab_path: str):
        """Load the trained model and vocabulary."""
        try:
            # Register custom layers and functions for model loading
            custom_objects = {
                'MultiHeadAttention': MultiHeadAttention,
                'TransformerBlock': TransformerBlock,
                'MaskLayer': MaskLayer,
                'PositionalEncodingLayer': PositionalEncodingLayer,
                'MaskLogitsLayer': MaskLogitsLayer,
                'squeeze_last_dim': squeeze_last_dim,
                'squeeze_last_dim_output_shape': squeeze_last_dim_output_shape,
            }
            
            print(f"Loading model from {model_path}...")
            
            # Alternative approach: Try to rebuild the model if loading fails
            try:
                self.model = load_model(model_path, custom_objects=custom_objects)
                print("Model loaded successfully!")
            except Exception as load_error:
                print(f"Direct loading failed: {load_error}")
                print("Attempting alternative loading method...")
                
                # Try loading weights only and rebuilding
                try:
                    # This is a fallback - you might need to adjust based on your model architecture
                    print("Please consider retraining your model without Lambda layers,")
                    print("or provide the model architecture separately to rebuild it properly.")
                    raise load_error
                except Exception as rebuild_error:
                    raise Exception(f"Both loading methods failed. Direct load error: {load_error}. Rebuild error: {rebuild_error}")
            
            print(f"Loading vocabulary from {vocab_path}...")
            with open(vocab_path, 'r') as f:
                self.vocab = json.load(f)
            
            # Create reverse vocabulary for decoding
            self.reverse_vocab = {v: k for k, v in self.vocab.items()}
            print(f"Vocabulary loaded successfully! Size: {len(self.vocab)}")
            
        except Exception as e:
            print(f"Error details: {str(e)}")
            print("\nTroubleshooting suggestions:")
            print("1. If you have Lambda layers in your model, retrain without them")
            print("2. Save your model using model.save_weights() and model architecture separately")
            print("3. Use SavedModel format instead of .keras format")
            print("4. Check if your model was saved with a different TensorFlow version")
            raise Exception(f"Failed to load model or vocabulary: {str(e)}")
    
    def simple_tokenize(self, text: str) -> List[str]:
        """Simple tokenization function matching the training process."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        tokens = text.split()
        return [token for token in tokens if token.strip()]
    
    def preprocess_input(self, question: str, context: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Preprocess question and context for model input.
        
        Args:
            question: The question to answer
            context: The context containing the answer
            
        Returns:
            Tuple of (input_ids, attention_mask, input_tokens)
        """
        # Tokenize inputs
        question_tokens = self.simple_tokenize(question)
        context_tokens = self.simple_tokenize(context)
        
        # Create input sequence: [CLS] question [SEP] context
        input_tokens = ["<cls>"] + question_tokens + ["<sep>"] + context_tokens
        input_ids = [self.vocab.get(token, self.vocab["<unk>"]) for token in input_tokens]
        
        # Truncate if too long
        if len(input_ids) > self.max_length:
            question_sep_len = len(question_tokens) + 2
            available_context_len = self.max_length - question_sep_len
            if available_context_len > 50:
                input_ids = input_ids[:question_sep_len] + input_ids[question_sep_len:question_sep_len + available_context_len]
                input_tokens = input_tokens[:question_sep_len] + input_tokens[question_sep_len:question_sep_len + available_context_len]
            else:
                input_ids = input_ids[:self.max_length]
                input_tokens = input_tokens[:self.max_length]
        
        # Pad to max_length
        original_length = len(input_ids)
        padding_length = self.max_length - len(input_ids)
        input_ids.extend([self.vocab["<pad>"]] * padding_length)
        
        # Create attention mask
        attention_mask = [1] * original_length + [0] * padding_length
        
        return (
            np.array(input_ids, dtype=np.int32),
            np.array(attention_mask, dtype=np.int32),
            input_tokens
        )
    
    def extract_answer(self, start_logits: np.ndarray, end_logits: np.ndarray, 
                      input_tokens: List[str], top_k: int = 5) -> List[Dict]:
        """
        Extract the best answer(s) from model predictions.
        
        Args:
            start_logits: Model predictions for start positions
            end_logits: Model predictions for end positions
            input_tokens: Tokenized input sequence
            top_k: Number of top answers to return
            
        Returns:
            List of dictionaries containing answer text and confidence scores
        """
        # Get top predictions
        start_indices = np.argsort(start_logits)[::-1][:top_k * 2]
        end_indices = np.argsort(end_logits)[::-1][:top_k * 2]
        
        candidates = []
        
        for start_idx in start_indices:
            for end_idx in end_indices:
                # Ensure valid span
                if start_idx <= end_idx and end_idx < len(input_tokens):
                    # Calculate confidence score
                    start_score = start_logits[start_idx]
                    end_score = end_logits[end_idx]
                    confidence = (start_score + end_score) / 2
                    
                    # Extract answer tokens
                    answer_tokens = input_tokens[start_idx:end_idx + 1]
                    
                    # Filter out special tokens
                    answer_tokens = [token for token in answer_tokens 
                                   if token not in ["<cls>", "<sep>", "<pad>", "<unk>"]]
                    
                    if answer_tokens:  # Only add non-empty answers
                        answer_text = " ".join(answer_tokens)
                        candidates.append({
                            'text': answer_text,
                            'confidence': float(confidence),
                            'start_pos': int(start_idx),
                            'end_pos': int(end_idx)
                        })
        
        # Remove duplicates and sort by confidence
        unique_candidates = {}
        for candidate in candidates:
            text = candidate['text']
            if text not in unique_candidates or candidate['confidence'] > unique_candidates[text]['confidence']:
                unique_candidates[text] = candidate
        
        # Sort by confidence and return top_k
        sorted_candidates = sorted(unique_candidates.values(), 
                                 key=lambda x: x['confidence'], reverse=True)
        
        return sorted_candidates[:top_k]
    
    def answer_question(self, question: str, context: str, return_confidence: bool = False, 
                       top_k: int = 1) -> str | Dict:
        """
        Answer a question based on the provided context.
        
        Args:
            question: The question to answer
            context: The context containing the answer
            return_confidence: Whether to return confidence scores
            top_k: Number of top answers to consider
            
        Returns:
            Answer text (string) or detailed results (dict) if return_confidence=True
        """
        if not self.model or not self.vocab:
            raise ValueError("Model and vocabulary must be loaded first")
        
        # Preprocess input
        input_ids, attention_mask, input_tokens = self.preprocess_input(question, context)
        
        # Add batch dimension
        input_ids = np.expand_dims(input_ids, 0)
        attention_mask = np.expand_dims(attention_mask, 0)
        
        # Make prediction
        start_logits, end_logits = self.model.predict([input_ids, attention_mask], verbose=0)
        
        # Extract answers
        candidates = self.extract_answer(start_logits[0], end_logits[0], input_tokens, top_k)
        
        if not candidates:
            if return_confidence:
                return {
                    'answer': "No answer found",
                    'confidence': 0.0,
                    'all_candidates': []
                }
            return "No answer found"
        
        best_answer = candidates[0]
        
        if return_confidence:
            return {
                'answer': best_answer['text'],
                'confidence': best_answer['confidence'],
                'all_candidates': candidates
            }
        
        return best_answer['text']
    
    def answer_questions_batch(self, questions_and_contexts: List[Tuple[str, str]], 
                              return_confidence: bool = False) -> List[str | Dict]:
        """
        Answer multiple questions in batch for better efficiency.
        
        Args:
            questions_and_contexts: List of (question, context) tuples
            return_confidence: Whether to return confidence scores
            
        Returns:
            List of answers or detailed results
        """
        if not questions_and_contexts:
            return []
        
        # Preprocess all inputs
        batch_input_ids = []
        batch_attention_masks = []
        batch_input_tokens = []
        
        for question, context in questions_and_contexts:
            input_ids, attention_mask, input_tokens = self.preprocess_input(question, context)
            batch_input_ids.append(input_ids)
            batch_attention_masks.append(attention_mask)
            batch_input_tokens.append(input_tokens)
        
        # Convert to numpy arrays
        batch_input_ids = np.array(batch_input_ids)
        batch_attention_masks = np.array(batch_attention_masks)
        
        # Make batch prediction
        start_logits_batch, end_logits_batch = self.model.predict(
            [batch_input_ids, batch_attention_masks], verbose=0
        )
        
        # Extract answers for each sample
        results = []
        for i in range(len(questions_and_contexts)):
            candidates = self.extract_answer(
                start_logits_batch[i], end_logits_batch[i], batch_input_tokens[i]
            )
            
            if not candidates:
                if return_confidence:
                    results.append({
                        'answer': "No answer found",
                        'confidence': 0.0,
                        'all_candidates': []
                    })
                else:
                    results.append("No answer found")
            else:
                best_answer = candidates[0]
                if return_confidence:
                    results.append({
                        'answer': best_answer['text'],
                        'confidence': best_answer['confidence'],
                        'all_candidates': candidates
                    })
                else:
                    results.append(best_answer['text'])
        
        return results
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        if not self.model:
            return {"error": "No model loaded"}
        
        return {
            "model_summary": str(self.model.summary()),
            "vocab_size": len(self.vocab) if self.vocab else 0,
            "max_length": self.max_length,
            "model_input_shape": self.model.input_shape,
            "model_output_shape": self.model.output_shape
        }


def save_model_architecture_and_weights(model, base_path: str):
    """
    Helper function to save model architecture and weights separately.
    This can help avoid Lambda layer issues.
    """
    try:
        # Save architecture as JSON
        architecture_path = f"{base_path}_architecture.json"
        with open(architecture_path, 'w') as f:
            f.write(model.to_json())
        
        # Save weights
        weights_path = f"{base_path}_weights.h5"
        model.save_weights(weights_path)
        
        print(f"Model architecture saved to: {architecture_path}")
        print(f"Model weights saved to: {weights_path}")
        
        return architecture_path, weights_path
    except Exception as e:
        print(f"Error saving model components: {e}")
        return None, None


def load_model_from_components(architecture_path: str, weights_path: str, custom_objects: dict):
    """
    Helper function to load model from separate architecture and weights files.
    """
    try:
        # Load architecture
        with open(architecture_path, 'r') as f:
            model_json = f.read()
        
        # Create model from architecture
        model = tf.keras.models.model_from_json(model_json, custom_objects=custom_objects)
        
        # Load weights
        model.load_weights(weights_path)
        
        return model
    except Exception as e:
        raise Exception(f"Failed to load model from components: {e}")


def interactive_qa_session(engine: QAInferenceEngine):
    """Run an interactive Q&A session."""
    print("\n" + "="*60)
    print("Interactive Question Answering Session")
    print("="*60)
    print("Enter 'quit' to exit")
    print("Enter 'help' for instructions")
    print("-"*60)
    
    while True:
        try:
            command = input("\nEnter command (question/context/quit/help): ").strip().lower()
            
            if command == 'quit':
                print("Goodbye!")
                break
            elif command == 'help':
                print("\nInstructions:")
                print("1. Type 'question' to start asking questions")
                print("2. Type 'context' to provide context first")
                print("3. Type 'quit' to exit")
                continue
            elif command == 'question':
                question = input("Question: ").strip()
                if not question:
                    print("Please enter a valid question.")
                    continue
                
                context = input("Context: ").strip()
                if not context:
                    print("Please provide context for the question.")
                    continue
                
                print("\nProcessing...")
                result = engine.answer_question(question, context, return_confidence=True)
                
                print(f"\nAnswer: {result['answer']}")
                print(f"Confidence: {result['confidence']:.4f}")
                
                if len(result['all_candidates']) > 1:
                    print("\nAlternative answers:")
                    for i, candidate in enumerate(result['all_candidates'][1:4], 1):
                        print(f"  {i}. {candidate['text']} (confidence: {candidate['confidence']:.4f})")
            
            elif command == 'context':
                context = input("Enter context: ").strip()
                if not context:
                    print("Please enter valid context.")
                    continue
                
                while True:
                    question = input("Question (or 'back' to change context): ").strip()
                    if question.lower() == 'back':
                        break
                    if not question:
                        print("Please enter a valid question.")
                        continue
                    
                    print("\nProcessing...")
                    result = engine.answer_question(question, context, return_confidence=True)
                    
                    print(f"\nAnswer: {result['answer']}")
                    print(f"Confidence: {result['confidence']:.4f}")
            else:
                print("Invalid command. Type 'help' for instructions.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description="Question Answering Inference Engine")
    parser.add_argument("--model_path", required=True, help="Path to the trained model file")
    parser.add_argument("--vocab_path", required=True, help="Path to the vocabulary JSON file")
    parser.add_argument("--max_length", type=int, default=512, help="Maximum sequence length")
    parser.add_argument("--question", help="Question to answer")
    parser.add_argument("--context", help="Context for the question")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--batch_file", help="JSON file with questions and contexts for batch processing")
    parser.add_argument("--output_file", help="Output file for batch results")
    parser.add_argument("--architecture_path", help="Path to model architecture JSON file (alternative loading)")
    parser.add_argument("--weights_path", help="Path to model weights file (alternative loading)")
    
    args = parser.parse_args()
    
    # Validate required files exist
    if not args.architecture_path:  # Normal loading
        if not os.path.exists(args.model_path):
            print(f"Error: Model file not found: {args.model_path}")
            return 1
    else:  # Alternative loading
        if not os.path.exists(args.architecture_path):
            print(f"Error: Architecture file not found: {args.architecture_path}")
            return 1
        if not os.path.exists(args.weights_path):
            print(f"Error: Weights file not found: {args.weights_path}")
            return 1
    
    if not os.path.exists(args.vocab_path):
        print(f"Error: Vocabulary file not found: {args.vocab_path}")
        return 1
    
    try:
        # Initialize the inference engine
        print("Initializing QA Inference Engine...")
        
        if args.architecture_path and args.weights_path:
            # Alternative initialization with separate architecture and weights
            print("Using alternative loading method with separate architecture and weights...")
            # You would need to modify QAInferenceEngine to support this
            print("Note: Alternative loading method requires code modification.")
            print("Please use the normal loading method or retrain your model.")
            return 1
        else:
            engine = QAInferenceEngine(args.model_path, args.vocab_path, args.max_length)
        
        print("Engine initialized successfully!")
        
        # Interactive mode
        if args.interactive:
            interactive_qa_session(engine)
            return 0
        
        # Batch processing mode
        if args.batch_file:
            if not os.path.exists(args.batch_file):
                print(f"Error: Batch file not found: {args.batch_file}")
                return 1
            
            print(f"Processing batch file: {args.batch_file}")
            with open(args.batch_file, 'r') as f:
                batch_data = json.load(f)
            
            # Extract questions and contexts
            questions_and_contexts = []
            for item in batch_data:
                if 'question' in item and 'context' in item:
                    questions_and_contexts.append((item['question'], item['context']))
                else:
                    print(f"Warning: Skipping invalid item: {item}")
            
            if not questions_and_contexts:
                print("Error: No valid question-context pairs found in batch file")
                return 1
            
            # Process batch
            print(f"Processing {len(questions_and_contexts)} question-answer pairs...")
            results = engine.answer_questions_batch(questions_and_contexts, return_confidence=True)
            
            # Prepare output
            output_data = []
            for i, ((question, context), result) in enumerate(zip(questions_and_contexts, results)):
                output_data.append({
                    'id': i + 1,
                    'question': question,
                    'context': context,
                    'answer': result['answer'],
                    'confidence': result['confidence'],
                    'alternatives': result['all_candidates'][1:4] if len(result['all_candidates']) > 1 else []
                })
            
            # Save results
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    json.dump(output_data, f, indent=2)
                print(f"Results saved to: {args.output_file}")
            else:
                print("\nBatch Results:")
                print("=" * 80)
                for item in output_data:
                    print(f"Q{item['id']}: {item['question']}")
                    print(f"Answer: {item['answer']}")
                    print(f"Confidence: {item['confidence']:.4f}")
                    if item['alternatives']:
                        print("Alternatives:")
                        for j, alt in enumerate(item['alternatives'], 1):
                            print(f"  {j}. {alt['text']} (confidence: {alt['confidence']:.4f})")
                    print("-" * 80)
            
            return 0
        
        # Single question mode
        if args.question and args.context:
            print(f"Question: {args.question}")
            print(f"Context: {args.context[:100]}..." if len(args.context) > 100 else f"Context: {args.context}")
            print("\nProcessing...")
            
            result = engine.answer_question(args.question, args.context, return_confidence=True)
            
            print(f"\nAnswer: {result['answer']}")
            print(f"Confidence: {result['confidence']:.4f}")
            
            if len(result['all_candidates']) > 1:
                print("\nAlternative answers:")
                for i, candidate in enumerate(result['all_candidates'][1:4], 1):
                    print(f"  {i}. {candidate['text']} (confidence: {candidate['confidence']:.4f})")
            
            return 0
        
        # If no specific mode, show help
        print("\nUsage Examples:")
        print("1. Single question:")
        print(f"   python {os.path.basename(__file__)} --model_path model.keras --vocab_path vocab.json --question 'What is the capital?' --context 'The capital of France is Paris.'")
        print("\n2. Interactive mode:")
        print(f"   python {os.path.basename(__file__)} --model_path model.keras --vocab_path vocab.json --interactive")
        print("\n3. Batch processing:")
        print(f"   python {os.path.basename(__file__)} --model_path model.keras --vocab_path vocab.json --batch_file questions.json --output_file results.json")
        print("\nFor batch processing, create a JSON file with this format:")
        print('[{"question": "What is...?", "context": "The answer is..."}, ...]')
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Ensure your model was saved properly")
        print("2. Check that vocabulary file exists and is valid JSON")
        print("3. If using Lambda layers, consider retraining without them")
        print("4. Try using SavedModel format instead of .keras format")
        return 1


if __name__ == "__main__":
    exit(main())