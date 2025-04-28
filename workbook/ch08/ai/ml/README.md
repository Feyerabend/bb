
## Machine Learning

| *Algorithm*                | *Type*             | *Typical Use Cases*              | *Key Properties*                                                |
|----------------------------|--------------------|----------------------------------|-----------------------------------------------------------------|
| [Linear Regression](./linear/)     | Supervised | Predicting continuous values     | Simple, interpretable, assumes linearity                        |
| [Logistic Regression](./logistic/) | Supervised | Binary classification            | Probabilistic outputs, interpretable, linear decision boundary  |
| Decision Trees             | Supervised         | Classification and regression    | Interpretable, handles non-linear data, prone to overfitting    |
| Random Forest              | Supervised         | General-purpose                  | Ensemble of trees, reduces overfitting, less interpretable      |
| Support Vector Machine     | Supervised         | High-dimensional classification  | Margin maximisation, kernel trick for non-linearity             |
| K-Nearest Neighbours (KNN) | Supervised         | Classification, regression       | Instance-based, simple, no training phase                       |
| Naive Bayes                | Supervised         | Text classification, spam filtering | Probabilistic, strong independence assumptions               |
| Gradient Boosting (XGBoost, LightGBM) | Supervised | Structured data             | High accuracy, can overfit, less interpretable                    |
| K-Means                    | Unsupervised       | Clustering, segmentation         | Simple, assumes spherical clusters, sensitive to initialisation |
| DBSCAN                     | Unsupervised       | Clustering with noise            | Handles arbitrary shapes, density-based                         |
| PCA (Principal Component Analysis) | Unsupervised | Dimensionality reduction     | Linear transformation, unsupervised, captures variance            |
| t-SNE / UMAP               | Unsupervised       | Visualisation, clustering        | Non-linear, preserves local structure, non-parametric           |
| Apriori / FP-Growth        | Unsupervised       | Market basket analysis           | Association rule mining                                         |
| Neural Networks (MLP)      | Supervised         | General-purpose                  | Flexible, powerful, requires large data                         |
| CNN (Convolutional NN)     | Supervised         | Image data                       | Exploits spatial structure, translation invariance              |
| RNN / LSTM / GRU           | Supervised         | Sequence data (text, time-series)| Captures temporal dependencies, vanishing gradient challenges   |
| GANs (Generative Adversarial Networks) | Unsupervised | Data generation          | Adversarial training, high-quality synthetic data                 |
| Reinforcement Learning     | Reinforcement      | Game AI, robotics, control       | Trial-and-error learning, reward signal                         |



### Language Models and Conventional Machine Learning Models

Machine learning (ML) encompasses a broad range of applications, from image recognition to natural
language processing (NLP). While conventional models like those trained on the MNIST dataset focus
on visual tasks (e.g., digit recognition), more advanced models, such as language models, specialise
in understanding and generating human language.

- [MNIST](./mnist/): A simple yet powerful dataset for introducing classification tasks, MNIST consists
of handwritten digits and serves as a benchmark for models that perform supervised learning. It's often
used to demonstrate the effectiveness of simple ML models like logistic regression, decision trees,
or neural networks.

- Language Models ([LM](./lm/)): These models, though often more complex, focus on understanding and
predicting sequences of text. A simple LM can be trained to predict the next word in a sentence or even
generate coherent text. Unlike image-based models, LMs handle textual data and showcase concepts
such as tokenisation, embeddings, and sequential learning.


### References

- Mitchell, T. M. (1997). Machine Learning. McGraw-Hill.
- Bishop, C. M. (2006). Pattern Recognition and Machine Learning. Springer.
- Géron, A. (2019). Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow. O’Reilly Media.
- Murphy, K. P. (2012). Machine Learning: A Probabilistic Perspective. MIT Press.
-- REPLACE REFs
