This `SimpleWord2Vec` code implements a basic Skip-gram model with Negative Sampling, which is a common and efficient way to train word embeddings. Here are the essential concepts illustrated in the code:

* *Word Embeddings*: The core idea is to represent words as dense numerical vectors (`self.W1` and `self.W2` matrices). These vectors aim to capture semantic relationships between words, where words with similar meanings are located close to each other in the vector space.
* *Skip-gram Model*: This architecture is designed to predict the surrounding context words given a target (center) word. In the `generate_training_data` method, for each `center_word_idx`, it iterates through a `window_size` to select `context_word_idx` pairs.
* *Negative Sampling*: Instead of predicting all words in the vocabulary (which would be computationally expensive), Negative Sampling optimizes the model by training it to distinguish between the actual context words and a small number of randomly sampled "negative" (non-context) words.
    * For a given `(center_word_idx, context_word_idx)` pair, the model updates weights to increase the probability of `context_word_idx` being a "true" neighbor.
    * Simultaneously, it samples `negative_samples` (e.g., 10 in this code) random words from the vocabulary and updates weights to decrease their probability of being "true" neighbors. This is evident in the `train` method where `np.random.choice` is used to pick `negative_indices`.
* *Vocabulary Building (`build_vocabulary`)*:
    * The code preprocesses the text by lowercasing and tokenizing words.
    * It counts word frequencies and filters out words that appear less than `min_count` (set to 5) and common stopwords, creating a `word_to_idx` and `idx_to_word` mapping.
* *Training Process (`train`)*:
    * *Initialization*: The word embedding matrices (`self.W1` and `self.W2`) are initialized with small random values. `W1` represents the input word embeddings, and `W2` represents the output word embeddings (or context embeddings).
    * *Loss Function (Implicit)*: The code uses a form of binary cross-entropy loss, where it tries to maximize the sigmoid of the dot product for positive pairs and minimize it for negative pairs.
        * `loss = -np.log(y_pred_pos + 1e-10)` for positive samples.
        * `loss -= np.log(1 - y_pred_neg + 1e-10)` for negative samples.
    * *Gradient Descent*: The `W1` and `W2` matrices are updated iteratively using stochastic gradient descent (SGD). The learning rate `lr` decays over epochs.
    * *Normalization*: After training, the word vectors in `self.W1` are normalized to unit length, which can improve the quality of similarity calculations.
* *Similarity Calculation (`most_similar`)*: This method calculates the cosine similarity between word vectors to find words that are semantically similar. Cosine similarity is calculated as the dot product of two vectors divided by the product of their magnitudes.
