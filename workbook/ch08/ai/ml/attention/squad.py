# pip install tensorflow tensorflow_datasets
import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow.keras.layers import Dense, Input, Layer, Embedding, Dropout, LayerNormalization
from tensorflow.keras.models import Model
import numpy as np
import re
import os
import json

# Load the SQuAD dataset
def load_squad_dataset(split='train'):
    dataset, info = tfds.load('squad', split=split, with_info=True, as_supervised=False)
    return dataset, info

# Improved tokenization with better preprocessing
def simple_tokenize(text):
    """Simple whitespace tokenization with basic punctuation handling"""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()
    return [token for token in tokens if token.strip()]

# Build vocabulary from dataset
def build_vocab(dataset, vocab_size=15000):  # Increased vocab size
    vocab = {"<pad>": 0, "<unk>": 1, "<sep>": 2, "<cls>": 3}
    word_counts = {}
    
    # Count words in a larger sample
    for i, example in enumerate(dataset.take(10000)):  # Increased sample size
        if i >= 10000:
            break
        context = example['context'].numpy().decode('utf-8')
        question = example['question'].numpy().decode('utf-8')
        
        context_tokens = simple_tokenize(context)
        question_tokens = simple_tokenize(question)
        
        for word in context_tokens + question_tokens:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Add most frequent words to vocab
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    for word, _ in sorted_words[:vocab_size-len(vocab)]:
        vocab[word] = len(vocab)
    
    return vocab

# Improved preprocessing with better answer alignment
def preprocess_data(dataset, vocab, max_length=512, num_examples=5000):  # Increased context length
    def find_answer_positions(context_tokens, answer_tokens, context_start_idx):
        if not answer_tokens:
            return context_start_idx, context_start_idx
            
        # Try exact match first
        for i in range(context_start_idx, len(context_tokens) - len(answer_tokens) + 1):
            match = True
            for j, ans_token in enumerate(answer_tokens):
                if i + j >= len(context_tokens) or context_tokens[i + j] != ans_token:
                    match = False
                    break
            if match:
                return i, i + len(answer_tokens) - 1
        
        # Fallback to partial match
        best_start = context_start_idx
        best_score = 0
        for i in range(context_start_idx, min(len(context_tokens), context_start_idx + 50)):
            score = 0
            for j, ans_token in enumerate(answer_tokens):
                if i + j < len(context_tokens) and context_tokens[i + j] == ans_token:
                    score += 1
                else:
                    break
            if score > best_score:
                best_score = score
                best_start = i
        
        return best_start, min(best_start + len(answer_tokens) - 1, len(context_tokens) - 1)
    
    def _preprocess(example):
        context = example['context'].numpy().decode('utf-8')
        question = example['question'].numpy().decode('utf-8')
        
        answers = example['answers']
        if len(answers['text']) == 0:
            return None
            
        answer_text = answers['text'].numpy()[0].decode('utf-8')
        
        question_tokens = simple_tokenize(question)
        context_tokens = simple_tokenize(context)
        answer_tokens = simple_tokenize(answer_text)
        
        # Create input sequence: [CLS] question [SEP] context
        input_tokens = ["<cls>"] + question_tokens + ["<sep>"] + context_tokens
        input_ids = [vocab.get(token, vocab["<unk>"]) for token in input_tokens]
        
        # Truncate if too long
        if len(input_ids) > max_length:
            # Try to keep the question and truncate context intelligently
            question_sep_len = len(question_tokens) + 2  # [CLS] + question + [SEP]
            available_context_len = max_length - question_sep_len
            if available_context_len > 50:  # Keep at least 50 tokens of context
                input_ids = input_ids[:question_sep_len] + input_ids[question_sep_len:question_sep_len + available_context_len]
                input_tokens = input_tokens[:question_sep_len] + input_tokens[question_sep_len:question_sep_len + available_context_len]
            else:
                input_ids = input_ids[:max_length]
                input_tokens = input_tokens[:max_length]
        
        # Pad to max_length
        padding_length = max_length - len(input_ids)
        input_ids.extend([vocab["<pad>"]] * padding_length)
        
        # Create attention mask
        attention_mask = [1] * len(input_tokens) + [0] * padding_length
        
        # Find answer positions
        context_start_idx = len(question_tokens) + 2
        start_pos, end_pos = find_answer_positions(input_tokens, answer_tokens, context_start_idx)
        
        # Ensure positions are within bounds
        start_pos = min(max(start_pos, 0), len(input_tokens) - 1)
        end_pos = min(max(end_pos, start_pos), len(input_tokens) - 1)
        
        return (
            np.array(input_ids, dtype=np.int32),
            np.array(attention_mask, dtype=np.int32),
            int(start_pos),
            int(end_pos)
        )
    
    # Process dataset
    processed_data = []
    valid_examples = 0
    
    for example in dataset.take(num_examples * 2):  # Take more to filter out invalid ones
        result = _preprocess(example)
        if result is not None:
            processed_data.append(result)
            valid_examples += 1
            if valid_examples >= num_examples:
                break
    
    if not processed_data:
        raise ValueError("No valid examples found in dataset")
    
    print(f"Processed {len(processed_data)} valid examples")
    
    # Convert to tf.data.Dataset
    input_ids = tf.constant([item[0] for item in processed_data], dtype=tf.int32)
    attention_masks = tf.constant([item[1] for item in processed_data], dtype=tf.int32)
    start_positions = tf.constant([item[2] for item in processed_data], dtype=tf.int32)
    end_positions = tf.constant([item[3] for item in processed_data], dtype=tf.int32)
    
    dataset = tf.data.Dataset.from_tensor_slices((
        {'input_ids': input_ids, 'attention_mask': attention_masks},
        {'start_logits': start_positions, 'end_logits': end_positions}
    ))
    
    return dataset

# Multi-Head Attention layer
class MultiHeadAttention(Layer):
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

# Transformer Block
class TransformerBlock(Layer):
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

# Custom layers
class MaskLayer(Layer):
    def __init__(self, **kwargs):
        super(MaskLayer, self).__init__(**kwargs)
    
    def call(self, inputs):
        attention_mask = inputs
        mask = tf.cast(tf.equal(attention_mask, 0), tf.float32)
        return mask

class PositionalEncodingLayer(Layer):
    def __init__(self, max_length, d_model, **kwargs):
        super(PositionalEncodingLayer, self).__init__(**kwargs)
        self.max_length = max_length
        self.d_model = d_model
        
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
    
    def call(self, inputs):
        seq_len = tf.shape(inputs)[1]
        return inputs + self.pos_encoding[:, :seq_len, :]
    
    def get_config(self):
        config = super().get_config()
        config.update({
            'max_length': self.max_length,
            'd_model': self.d_model,
        })
        return config

class MaskLogitsLayer(Layer):
    def __init__(self, **kwargs):
        super(MaskLogitsLayer, self).__init__(**kwargs)
    
    def call(self, inputs):
        logits, mask = inputs
        return logits + mask * -1e9

# Create improved model
def create_model(vocab_size, max_length=512, d_model=256, num_heads=8, num_layers=4, dff=1024, dropout_rate=0.1):
    input_ids = Input(shape=(max_length,), dtype=tf.int32, name='input_ids')
    attention_mask = Input(shape=(max_length,), dtype=tf.int32, name='attention_mask')
    
    # Create padding mask
    mask = MaskLayer()(attention_mask)
    
    # Embedding layer with larger dimension
    embedding = Embedding(vocab_size, d_model, mask_zero=True)(input_ids)
    embedding = Dropout(dropout_rate)(embedding)
    
    # Add positional encoding
    x = PositionalEncodingLayer(max_length, d_model)(embedding)
    
    # Multiple transformer blocks
    for _ in range(num_layers):
        x = TransformerBlock(d_model, num_heads, dff, dropout_rate)([x, mask])
    
    # Add another layer before output for better representations
    x = Dense(d_model // 2, activation='relu')(x)
    x = Dropout(dropout_rate)(x)
    
    # Output layers for start and end positions
    start_logits = Dense(1, name='start_dense')(x)
    end_logits = Dense(1, name='end_dense')(x)
    
    # Squeeze to remove last dimension
    start_logits = tf.keras.layers.Lambda(lambda x: tf.squeeze(x, -1))(start_logits)
    end_logits = tf.keras.layers.Lambda(lambda x: tf.squeeze(x, -1))(end_logits)
    
    # Apply mask to logits
    start_logits = MaskLogitsLayer(name='start_logits')([start_logits, mask])
    end_logits = MaskLogitsLayer(name='end_logits')([end_logits, mask])
    
    model = Model(inputs=[input_ids, attention_mask], outputs=[start_logits, end_logits])
    return model

# Training function with better settings
def train_model(model, dataset, epochs=10, batch_size=8):  # Increased epochs and batch size
    """Train the model with better monitoring"""
    
    # Split dataset
    dataset_size = sum(1 for _ in dataset)
    train_size = int(0.85 * dataset_size)  # Use more data for training
    
    train_dataset = dataset.take(train_size).shuffle(1000).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    val_dataset = dataset.skip(train_size).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    
    # Improved callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', 
            patience=3, 
            restore_best_weights=True, 
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5, 
            patience=2, 
            min_lr=1e-7,
            verbose=1
        ),
        tf.keras.callbacks.ModelCheckpoint(
            'best_model.h5',
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]
    
    # Train the model
    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=epochs,
        callbacks=callbacks,
        verbose=1
    )
    
    return history

# Save model and vocab
def save_model_and_vocab(model, vocab, model_path='qa_model.keras', vocab_path='vocab.json'):
    """Save the trained model and vocabulary"""
    model.save(model_path)
    
    with open(vocab_path, 'w') as f:
        json.dump(vocab, f)
    
    print(f"Model saved to {model_path}")
    print(f"Vocabulary saved to {vocab_path}")

# alt .h5 format
def save_model_and_vocab_h5(model, vocab, model_path='qa_model.h5', vocab_path='vocab.json'):
    """Save the trained model and vocabulary in H5 format"""
    model.save(model_path)
    
    with open(vocab_path, 'w') as f:
        json.dump(vocab, f)
    
    print(f"Model saved to {model_path}")
    print(f"Vocabulary saved to {vocab_path}")


# Main execution
def main():
    print("Loading dataset...")
    train_dataset, info = load_squad_dataset()
    
    print("Building vocabulary...")
    vocab = build_vocab(train_dataset, vocab_size=15000)
    vocab_size = len(vocab)
    print(f"Vocabulary size: {vocab_size}")
    
    print("Preprocessing data...")
    processed_dataset = preprocess_data(train_dataset, vocab, max_length=512, num_examples=8000)
    
    print("Creating model...")
    model = create_model(vocab_size, max_length=512, d_model=256, num_layers=4)
    
    # Compile model with improved settings
    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=2e-4,  # Slightly higher learning rate
            clipnorm=1.0,
            beta_1=0.9,
            beta_2=0.999
        ),
        loss={
            'start_logits': tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            'end_logits': tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        },
        metrics={
            'start_logits': ['accuracy'],
            'end_logits': ['accuracy']
        }
    )
    
    # Show model summary
    print("\nModel Summary:")
    model.summary()
    
    print("\nTraining model...")
    history = train_model(model, processed_dataset, epochs=15, batch_size=8)  # More epochs
    
    # Save the model and vocabulary
    save_model_and_vocab(model, vocab)
    
    return model, vocab

if __name__ == "__main__":
    try:
        model, vocab = main()
        print("Training completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()