
## Machine Learning

Machine Learning (ML) is an expanding field within AI, concerned with building systems that learn
from data and improve their performance without being explicitly programmed for every task. Instead
of hard-coding rules (like we did in the 80s), ML models extract patterns from examples and use
these to make predictions or decisions.

Traditional ML methods, such as decision trees, support vector machines, and logistic regression,
typically operate on structured data and require significant human effort in "feature engineering."
Feature engineering is deciding which parts of the data that are important.[^feature]

[^feature]: Feature engineering is the process of selecting, transforming, or creating input
variables (features) that make machine learning models more accurate and efficient. It often
involves identifying important properties in the data, scaling or normalizing values, combining
existing features, and encoding categorical information into numerical form.
E.g., from a date like 2025-04-28, you can create new features, abstractions, like "day of week"
or "month" to help a model find patterns more easily.

[Deep Learning (DL)](./DEEP.md), a newer branch of ML, reduces the need for manual feature
engineering by *automatically* discovering high-level representations within data. Deep learning
models, built with layered neural networks, have proven especially effective for complex tasks
like image recognition, speech processing, and natural language understanding.

In simple projects, like MNIST digit recognition, traditional ML and deep learning can both be
applied effectively. In more complex tasks, such as training language models to generate human-like
text, deep learning is essential.

Thus, ML provides the practical means by which AI systems can be made adaptive and intelligent,
and DL pushes the frontier further by enabling machines to learn directly from raw data.

However, in the context of providing code first for your learning, most of deep learning exceeds
the practical limits of this book. Deep models require large datasets, specialised architectures,
and significant compute, making them less suited for compact, self-contained examples. Instead,
we focus on classical machine learning--models you can fully understand, implement, and
analyze--building a foundation that scales naturally toward more advanced techniques.


| *Algorithm*                | *Type*             | *Typical Use Cases*              | *Key Properties*                                                |
|----------------------------|--------------------|----------------------------------|-----------------------------------------------------------------|
| [Linear Regression](./linear/)     | Supervised | Predicting continuous values     | Simple, interpretable, assumes linearity                        |
| [Logistic Regression](./logistic/) | Supervised | Binary classification            | Probabilistic outputs, interpretable, linear decision boundary  |
| Decision Trees             | Supervised         | Classification and regression    | Interpretable, handles non-linear data, prone to overfitting    |
| Random Forest              | Supervised         | General-purpose                  | Ensemble of trees, reduces overfitting, less interpretable      |
| Support Vector Machine     | Supervised         | High-dimensional classification  | Margin maximisation, kernel trick for non-linearity             |
| K-Nearest Neighbours (KNN) | Supervised         | Classification, regression       | Instance-based, simple, no training phase                       |
| [Naive Bayes](./bayes/)  | Supervised | Text classification, spam filtering | Probabilistic, strong independence assumptions |
| Gradient Boosting (XGBoost, LightGBM) | Supervised | Structured data             | High accuracy, can overfit, less interpretable                    |
| K-Means                    | Unsupervised       | Clustering, segmentation         | Simple, assumes spherical clusters, sensitive to initialisation |
| DBSCAN                     | Unsupervised       | Clustering with noise            | Handles arbitrary shapes, density-based                         |
| PCA (Principal Component Analysis) | Unsupervised | Dimensionality reduction     | Linear transformation, unsupervised, captures variance            |
| t-SNE / UMAP               | Unsupervised       | Visualisation, clustering        | Non-linear, preserves local structure, non-parametric           |
| Apriori / FP-Growth        | Unsupervised       | Market basket analysis           | Association rule mining                                         |
| Neural Networks (MLP)      | Supervised         | General-purpose                  | Flexible, powerful, requires large data                         |
| [CNN (Convolutional NN)](./mnist/cnn.py) | Supervised   | Image data               | Exploits spatial structure, translation invariance              |
| RNN / LSTM / GRU           | Supervised         | Sequence data (text, time-series)| Captures temporal dependencies, vanishing gradient challenges   |
| GANs (Generative Adversarial Networks) | Unsupervised | Data generation          | Adversarial training, high-quality synthetic data                 |
| [Reinforcement Learning](./../../../ch03/tictactoe/README.md) | Reinforcement | Game AI, robotics, control  | Trial-and-error learning, reward signal  |


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

Machine Learning is a subset of *Artificial Intelligence* (AI) focused on building systems that learn from
data rather than being explicitly programmed. When we code ML models, we are implementing the "learning"
part of AI. When we code DL models, we are implementing more powerful *learners* (deep neural networks).
Coding AI means writing the logic for learning, decision-making, and sometimes even perception, planning,
or reasoning, often by assembling ML and DL techniques.

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

