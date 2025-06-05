# pip install tensorflow tensorflow_datasets

import tensorflow as tf
import tensorflow_datasets as tfds

# Load the dataset
examples, metadata = tfds.load('spa_eng', with_info=True, as_supervised=True)
train_examples, val_examples = examples['train'], examples['validation']

# Tokenizer setup
tokenizer_en = tfds.deprecated.text.SubwordTextEncoder.build_from_corpus(
    (en.numpy() for en, _ in train_examples), target_vocab_size=2**13)
tokenizer_es = tfds.deprecated.text.SubwordTextEncoder.build_from_corpus(
    (es.numpy() for _, es in train_examples), target_vocab_size=2**13)

# Encode function
def encode(en_t, es_t):
    en = [tokenizer_en.vocab_size] + tokenizer_en.encode(en_t.numpy()) + [tokenizer_en.vocab_size + 1]
    es = [tokenizer_es.vocab_size] + tokenizer_es.encode(es_t.numpy()) + [tokenizer_es.vocab_size + 1]
    return en, es

def tf_encode(en, es):
    result_en, result_es = tf.py_function(encode, [en, es], [tf.int64, tf.int64])
    result_en.set_shape([None])
    result_es.set_shape([None])
    return result_en, result_es

# Prepare the dataset
BUFFER_SIZE = 20000
BATCH_SIZE = 64

train_dataset = (train_examples
    .map(tf_encode)
    .filter(lambda x, y: tf.logical_and(tf.size(x) > 0, tf.size(y) > 0))
    .cache()
    .shuffle(BUFFER_SIZE)
    .padded_batch(BATCH_SIZE, padded_shapes=([None], [None]))
    .prefetch(tf.data.AUTOTUNE))


def encode(es, en):
    es = tokenizer_es.encode(es.numpy())[:MAX_LENGTH]
    en = tokenizer_en.encode(en.numpy())[:MAX_LENGTH]
    return es, en

def tf_encode(es, en):
    result_es, result_en = tf.py_function(encode, [es, en], [tf.int64, tf.int64])
    result_es.set_shape([None])
    result_en.set_shape([None])
    return result_es, result_en

train_dataset = (train_examples
    .map(tf_encode)
    .filter(lambda x, y: tf.logical_and(tf.size(x) > 0, tf.size(y) > 0))
    .cache()
    .shuffle(BUFFER_SIZE)
    .padded_batch(BATCH_SIZE, padded_shapes=([None], [None]))
    .prefetch(tf.data.AUTOTUNE))

# Simple Encoder
class Encoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, enc_units):
        super().__init__()
        self.enc_units = enc_units
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(enc_units, return_sequences=True, return_state=True)

    def call(self, x):
        x = self.embedding(x)
        output, state = self.gru(x)
        return output, state

# Bahdanau Attention
class BahdanauAttention(tf.keras.layers.Layer):
    def __init__(self, units):
        super().__init__()
        self.W1 = tf.keras.layers.Dense(units)
        self.W2 = tf.keras.layers.Dense(units)
        self.V = tf.keras.layers.Dense(1)

    def call(self, query, values):
        query_with_time_axis = tf.expand_dims(query, 1)
        score = self.V(tf.nn.tanh(self.W1(values) + self.W2(query_with_time_axis)))
        attention_weights = tf.nn.softmax(score, axis=1)
        context_vector = attention_weights * values
        context_vector = tf.reduce_sum(context_vector, axis=1)
        return context_vector, attention_weights

# Decoder with attention
class Decoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, dec_units):
        super().__init__()
        self.dec_units = dec_units
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(dec_units, return_sequences=True, return_state=True)
        self.fc = tf.keras.layers.Dense(vocab_size)

        self.attention = BahdanauAttention(dec_units)

    def call(self, x, hidden, enc_output):
        context_vector, attention_weights = self.attention(hidden, enc_output)
        x = self.embedding(x)
        x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)
        output, state = self.gru(x)
        output = tf.reshape(output, (-1, output.shape[2]))
        return self.fc(output), state, attention_weights

# Hyperparameters
embedding_dim = 256
units = 1024
vocab_inp_size = tokenizer_es.vocab_size
vocab_tar_size = tokenizer_en.vocab_size

# Instantiate models
encoder = Encoder(vocab_inp_size, embedding_dim, units)
decoder = Decoder(vocab_tar_size, embedding_dim, units)

# Sample training step (for illustration)
optimizer = tf.keras.optimizers.Adam()

@tf.function
def train_step(inp, targ):
    loss = 0
    with tf.GradientTape() as tape:
        enc_output, enc_hidden = encoder(inp)
        dec_hidden = enc_hidden
        dec_input = tf.expand_dims([tokenizer_en.vocab_size] * BATCH_SIZE, 1)  # Start token

        for t in range(1, targ.shape[1]):
            predictions, dec_hidden, _ = decoder(dec_input, dec_hidden, enc_output)
            loss += tf.keras.losses.sparse_categorical_crossentropy(
                targ[:, t], predictions, from_logits=True)
            dec_input = tf.expand_dims(targ[:, t], 1)

    batch_loss = loss / int(targ.shape[1])
    variables = encoder.trainable_variables + decoder.trainable_variables
    gradients = tape.gradient(loss, variables)
    optimizer.apply_gradients(zip(gradients, variables))
    return batch_loss

# Run 1 training step (can be repeated in a loop)
for inp_batch, targ_batch in train_dataset.take(1):
    loss = train_step(inp_batch, targ_batch)
    print(f"Sample training step loss: {loss.numpy():.4f}")
