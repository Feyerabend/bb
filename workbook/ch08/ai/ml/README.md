

## Machine Learning

Machine Learning (ML) is a rapidly growing subfield of AI focused on building systems that learn from data
and improve performance over time--without being explicitly programmed for every task. Instead of writing
hardcoded rules (as was common in earlier software development), ML models identify patterns from examples
and use these patterns to make predictions or decisions.

Traditional ML algorithms--such as decision trees, support vector machines, and logistic regression--typically
work with structured data and rely heavily on feature engineering, where humans decide which parts of the
data are most informative.[^feature]

[^feature]: Feature engineering involves selecting, transforming, or creating input variables (features) to
improve model performance. This may include scaling values, encoding categories numerically, or abstracting
new features--e.g., extracting “day of week” from a date like 2025-04-28.

[Deep Learning](./DEEP.md) (DL), a more recent and powerful branch of ML, automates much of this process.
Deep learning models, built from multi-layered neural networks, learn hierarchical representations directly
from raw data. This approach has proven especially effective for complex tasks like image recognition,
speech processing, and natural language understanding.

For simpler tasks like digit recognition (e.g., MNIST), both traditional ML and deep learning can be
effective. For more sophisticated challenges--such as generating human-like text--deep learning is
today essential.

Thus, ML offers the practical means for creating adaptive, intelligent systems, while DL extends these
capabilities to domains that were previously out of reach.



### Study

While deep learning is a central part of modern AI, its full power requires large datasets, specialised
architectures, and significant computational resources--often beyond the practical scope of this book.
Instead, we focus on classical machine learning: models that are easier to implement, understand, and
reason about, making them well-suited for compact, code-first examples.

As interest and investment in AI grow, so does the abundance of tutorials and educational resources.
Rather than cover everything, we’ve selected a few representative techniques to provide a foundational
understanding, illustrate key ideas, and encourage deeper exploration.



### A General Observation

In traditional programming, the relationship between code and data is clear: a programmer writes fixed
instructions to process data. The control flow—rules, conditions, and logic—is predefined. The program
determines what happens to the data.

In contrast, machine learning inverts this relationship. Here, data shapes the program. Instead of
specifying behaviour explicitly, we provide data to a learning algorithm that infers a model—effectively
creating a program based on observed patterns. This model is dynamic; it evolves with new data and can
be updated or retrained without modifying the original code.

This leads to a fundamental shift in mindset:

> Traditional programming encodes logic to manipulate data.
> Machine learning uses data to induce logic.

This change redefines how we think about software: from static, rule-based systems to adaptive, data-driven
behaviors. These learned systems may be less transparent, but they are often more flexible and better suited
to real-world complexity.


### A Selection of Algorithms

As machine learning evolves, some early algorithms may seem outdated. However, they remain valuable, not for
their state-of-the-art performance, but because they highlight the essential shift from explicit programming
to data-driven inference. These methods help build intuition about how learning systems operate differently
from traditional code and provide a strong conceptual starting point for further study.

| *Algorithm* | *Type* | *Typical Use Cases* | *Key Properties* |
|---|---|---|---|
| [Linear Regression](./linear/) | Supervised | Predicting continuous values | Simple, interpretable, assumes linearity |
| [Logistic Regression](./logistic/) | Supervised | Binary classification | Probabilistic outputs, interpretable, linear decision boundary |
| Decision Trees             | Supervised         | Classification and regression    | Interpretable, handles non-linear data, prone to overfitting    |
| Random Forest              | Supervised         | General-purpose                  | Ensemble of trees, reduces overfitting, less interpretable      |
| Support Vector Machine     | Supervised         | High-dimensional classification  | Margin maximisation, kernel trick for non-linearity             |
| K-Nearest Neighbours (KNN) | Supervised         | Classification, regression       | Instance-based, simple, no training phase                       |
| [Naive Bayes](./bayes/) | Supervised | Text classification, spam filtering | Probabilistic, strong independence assumptions |
| Gradient Boosting (XGBoost, LightGBM) | Supervised | Structured data             | High accuracy, can overfit, less interpretable                    |
| K-Means                    | Unsupervised       | Clustering, segmentation         | Simple, assumes spherical clusters, sensitive to initialisation |
| DBSCAN                     | Unsupervised       | Clustering with noise            | Handles arbitrary shapes, density-based                         |
| PCA (Principal Component Analysis) | Unsupervised | Dimensionality reduction     | Linear transformation, unsupervised, captures variance            |
| t-SNE / UMAP               | Unsupervised       | Visualisation, clustering        | Non-linear, preserves local structure, non-parametric           |
| Apriori / FP-Growth        | Unsupervised       | Market basket analysis           | Association rule mining                                         |
| Neural Networks (MLP)      | Supervised         | General-purpose                  | Flexible, powerful, requires large data                         |
| [CNN](./mnist/cnn.py) (Convolutional NN) | Supervised | Image data | Exploits spatial structure, translation invariance |
| [RNN](./rnn/) / [LSTM](./rnn/) / [GRU](./rnn/) | Supervised | Sequence data (text, time-series) | Captures temporal dependencies, vanishing gradient challenges |
| [GANs](./gan/) (Generative Adversarial Networks) | Unsupervised | Data generation | Adversarial training, high-quality synthetic data |
| [Reinforcement Learning](./../../../ch03/tictactoe/README.md) | Reinforcement | Game AI, robotics, control  | Trial-and-error learning, reward signal |


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

Thus: *AI is the goal. ML is a method. DL is a specific technique within ML. The code we write builds
the systems that realise them.*

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

