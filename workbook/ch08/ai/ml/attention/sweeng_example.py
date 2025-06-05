# pip install tensorflow tensorflow_datasets
import tensorflow as tf
from tensorflow.keras.layers import Embedding, GRU, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

# Sample dataset
eng_sentences = [
    "hello", "how are you", "i am fine", "what is your name", "nice to meet you"
]
spa_sentences = [
    "hola", "cómo estás", "estoy bien", "cuál es tu nombre", "encantado de conocerte"
]

# Tokenization
def tokenize(texts, num_words=1000):
    tokenizer = Tokenizer(num_words=num_words, filters='')
    tokenizer.fit_on_texts(texts)
    tensor = tokenizer.texts_to_sequences(texts)
    tensor = pad_sequences(tensor, padding='post')
    return tensor, tokenizer

input_tensor, inp_tokenizer = tokenize(eng_sentences)
target_tensor, targ_tokenizer = tokenize(spa_sentences)

# Vocabulary sizes
inp_vocab_size = len(inp_tokenizer.word_index) + 1
targ_vocab_size = len(targ_tokenizer.word_index) + 1

# Model parameters
embedding_dim = 64
units = 128
BATCH_SIZE = 2
steps_per_epoch = len(eng_sentences) // BATCH_SIZE

# Dataset
dataset = tf.data.Dataset.from_tensor_slices((input_tensor, target_tensor)).shuffle(100)
dataset = dataset.batch(BATCH_SIZE, drop_remainder=True)

# Encoder
class Encoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, enc_units):
        super().__init__()
        self.enc_units = enc_units
        self.embedding = Embedding(vocab_size, embedding_dim)
        self.gru = GRU(enc_units, return_sequences=True, return_state=True)

    def call(self, x):
        x = self.embedding(x)
        output, state = self.gru(x)
        return output, state

# Attention
class BahdanauAttention(tf.keras.layers.Layer):
    def __init__(self, units):
        super().__init__()
        self.W1 = Dense(units)
        self.W2 = Dense(units)
        self.V = Dense(1)

    def call(self, query, values):
        query_with_time_axis = tf.expand_dims(query, 1)
        score = self.V(tf.nn.tanh(self.W1(values) + self.W2(query_with_time_axis)))
        attention_weights = tf.nn.softmax(score, axis=1)
        context_vector = attention_weights * values
        context_vector = tf.reduce_sum(context_vector, axis=1)
        return context_vector, attention_weights

# Decoder
class Decoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, dec_units):
        super().__init__()
        self.dec_units = dec_units
        self.embedding = Embedding(vocab_size, embedding_dim)
        self.gru = GRU(dec_units, return_sequences=True, return_state=True)
        self.fc = Dense(vocab_size)

        self.attention = BahdanauAttention(dec_units)

    def call(self, x, hidden, enc_output):
        context_vector, _ = self.attention(hidden, enc_output)
        x = self.embedding(x)
        x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)
        output, state = self.gru(x)
        output = tf.reshape(output, (-1, output.shape[2]))
        return self.fc(output), state

# Init models
encoder = Encoder(inp_vocab_size, embedding_dim, units)
decoder = Decoder(targ_vocab_size, embedding_dim, units)

# Optimizer and loss
optimizer = tf.keras.optimizers.Adam()
loss_object = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

# Training step
@tf.function
def train_step(inp, targ):
    loss = 0
    with tf.GradientTape() as tape:
        enc_output, enc_hidden = encoder(inp)
        dec_hidden = enc_hidden
        dec_input = tf.expand_dims([targ_tokenizer.word_index['<start>']] * BATCH_SIZE, 1)

        for t in range(1, targ.shape[1]):
            predictions, dec_hidden = decoder(dec_input, dec_hidden, enc_output)
            loss += loss_object(targ[:, t], predictions)
            dec_input = tf.expand_dims(targ[:, t], 1)

    batch_loss = loss / int(targ.shape[1])
    variables = encoder.trainable_variables + decoder.trainable_variables
    gradients = tape.gradient(loss, variables)
    optimizer.apply_gradients(zip(gradients, variables))
    return batch_loss

# Add start/end tokens
spa_sentences = ["<start> " + sent + " <end>" for sent in spa_sentences]
target_tensor, targ_tokenizer = tokenize(spa_sentences)

# Train
EPOCHS = 10
for epoch in range(EPOCHS):
    total_loss = 0
    for (batch, (inp, targ)) in enumerate(dataset):
        batch_loss = train_step(inp, targ)
        total_loss += batch_loss
    print(f'Epoch {epoch + 1}, Loss {total_loss / steps_per_epoch:.4f}')

# Inference
def translate(sentence):
    sentence = inp_tokenizer.texts_to_sequences([sentence])
    sentence = pad_sequences(sentence, maxlen=input_tensor.shape[1], padding='post')
    enc_out, enc_hidden = encoder(tf.constant(sentence))
    dec_hidden = enc_hidden
    dec_input = tf.expand_dims([targ_tokenizer.word_index['<start>']], 0)
    result = ''

    for _ in range(10):
        predictions, dec_hidden = decoder(dec_input, dec_hidden, enc_out)
        predicted_id = tf.argmax(predictions[0]).numpy()
        if targ_tokenizer.index_word[predicted_id] == '<end>':
            break
        result += targ_tokenizer.index_word[predicted_id] + ' '
        dec_input = tf.expand_dims([predicted_id], 0)
    return result.strip()

# Test
print(translate("hello"))
print(translate("how are you"))
print(translate("what is your name"))
