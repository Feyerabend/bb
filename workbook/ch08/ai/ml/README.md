
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

- *[MNIST](./mnist/)*: A simple yet powerful dataset for introducing classification tasks, MNIST consists
of handwritten digits and serves as a benchmark for models that perform supervised learning. It's often
used to demonstrate the effectiveness of simple ML models like logistic regression, decision trees,
or neural networks.

- *[Language Models, LMs](./lm/)*: These models, though often more complex, focus on understanding and
predicting sequences of text. A simple LM can be trained to predict the next word in a sentence or even
generate coherent text. Unlike image-based models, LMs handle textual data and showcase concepts
such as tokenisation, embeddings, and sequential learning.

Machine Learning is a subset of Artificial Intelligence (AI) focused on building systems that learn from
data rather than being explicitly programmed. Deep Learning (DL) is, in turn, a specialised area *within*
Machine Learning that uses large neural networks to learn complex patterns, often from unstructured data
like images, text, or audio.

When we code ML models, we are implementing the "learning" part of AI. When we code DL models, we are
implementing more powerful *learners* (deep neural networks). Coding AI means writing the logic for
learning, decision-making, and sometimes even perception, planning, or reasoning, often by assembling
ML and DL techniques.

Thus: AI is the goal. ML is a method. DL is a specific technique within ML. The code we write builds
the systems that realise them.

Examples
```
Artificial Intelligence (AI)
└── Machine Learning (ML)
    ├── Traditional ML
    │   ├── Decision Trees
    │   ├── Logistic Regression
    │   └── Support Vector Machines
    └── Deep Learning (DL)
        ├── Convolutional Neural Networks (CNNs) [such as MNIST]
        ├── Recurrent Neural Networks (RNNs)
        └── Transformers [for example Language Models]
```



### References

- Mitchell, T. M. (1997). Machine Learning. McGraw-Hill.
- Bishop, C. M. (2006). Pattern Recognition and Machine Learning. Springer.
- Géron, A. (2019). Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow. O’Reilly Media.
- Murphy, K. P. (2012). Machine Learning: A Probabilistic Perspective. MIT Press.
-- REPLACE REFs
100 ..
Deep Learning ..
