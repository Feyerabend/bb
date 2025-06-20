
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
new features--e.g., extracting "day of week" from a date like 2025-04-28.

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
Rather than cover everything, we've selected a few representative techniques to provide a foundational
understanding, illustrate key ideas, and encourage deeper exploration.

You can [begin](./START.md) from your conventional programming experience, to understand the machine
learning way of lettting machines do the work.


### A General Observation

In traditional programming, the relationship between code and data is clear: a programmer writes fixed
instructions to process data. The control flow--rules, conditions, and logic--is predefined. The program
determines what happens to the data.

In contrast, machine learning inverts this relationship. Here, data shapes the program. Instead of
specifying behaviour explicitly, we provide data to a learning algorithm that infers a model--effectively
creating a program based on observed patterns. This model is dynamic; it evolves with new data and can
be updated or retrained without modifying the original code.

This leads to a fundamental shift in mindset:

> Traditional programming encodes logic to manipulate data.
> Machine learning uses data to induce logic.

This change redefines how we think about software: from static, rule-based systems to adaptive, data-driven
behaviours. These learned systems may be less transparent, but they are often more flexible and better suited
to real-world complexity.


### A Selection of Algorithms

> [!WARNING]  
> Running Python in the context of machine learning often involves the use of external libraries and execution within a virtual environment (venv). Tools like TensorFlow and similar packages are commonly used. These environments evolve rapidly, and versions can become obsolete quickly. Consequently, the examples provided reflect the current state at the time of writing and may require adjustments to work with future versions.


As machine learning evolves, some early algorithms may seem outdated. However, they remain valuable, not for
their state-of-the-art performance, but because they highlight the essential shift from explicit programming
to data-driven inference. These methods help build intuition about how learning systems operate differently
from traditional code and provide a strong conceptual starting point for further study.

| *Algorithm* | *Type* | *Typical Use Cases* | *Key Properties* |
|---|---|---|---|
| [Linear Regression](./linear/) | Supervised | Predicting continuous values | Simple, interpretable, assumes linearity |
| [Logistic Regression](./logistic/) | Supervised | Binary classification | Probabilistic outputs, interpretable, linear decision boundary |
| [Decision Trees](./dtree/) | Supervised | Classification and regression | Interpretable, handles non-linear data, prone to overfitting |
| Random Forest              | Supervised         | General-purpose                  | Ensemble of trees, reduces overfitting, less interpretable      |
| [Support Vector Machine](./svm/) | Supervised | High-dimensional classification | Margin maximisation, kernel trick for non-linearity |
| [K-Nearest Neighbours](./knn/) (KNN) | Supervised | Classification, regression | Instance-based, simple, no training phase |
| [Naive Bayes](./bayes/) | Supervised | Text classification, spam filtering | Probabilistic, strong independence assumptions |
| Gradient Boosting (XGBoost, LightGBM) | Supervised | Structured data             | High accuracy, can overfit, less interpretable                    |
| [K-Means](./kmeans/) | Unsupervised | Clustering, segmentation | Simple, assumes spherical clusters, sensitive to initialisation |
| DBSCAN                     | Unsupervised       | Clustering with noise            | Handles arbitrary shapes, density-based                         |
| [PCA](./pca/) (Principal Component Analysis) | Unsupervised | Dimensionality reduction | Linear transformation, unsupervised, captures variance |
| [t-SNE](./tsne/) / [UMAP](./umap/) | Unsupervised | Visualisation, clustering | Non-linear, preserves local structure, non-parametric |
| [Apriori](./apriori/) / [FP-Growth](./apriori/) | Unsupervised | Market basket analysis | Association rule mining |
| [Neural Networks](./mlp/) (MLP) | Supervised | General-purpose | Flexible, powerful, requires large data |
| [CNN](./cnn/) (Convolutional NN) | Supervised | Image data | Exploits spatial structure, translation invariance |
| [RNN](./rnn/) / [LSTM](./rnn/) / [GRU](./rnn/) | Supervised | Sequence data (text, time-series) | Captures temporal dependencies, vanishing gradient challenges |
| [GANs](./gan/) (Generative Adversarial Networks) | Unsupervised | Data generation | Adversarial training, high-quality synthetic data |
| [Reinforcement Learning](./rl/) | Reinforcement | Game AI, robotics, control  | Trial-and-error learning, reward signal |


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


### Reflection: Why are they mostly about Classification and Clustering?

When you first begin learning about machine learning, the scope of the field can appear quite limited.
At first glance, tasks like classification and clustering may seem “simple.” However, as your understanding
deepens, it becomes clear that their perceived simplicity lies not in a lack of complexity, but in
their foundational role.

Classification and clustering are not simple because they are easy--they are simple because they represent
core, universally applicable ideas. They enable machines to categorise and organise vast amounts of
information with a speed and scale that far surpass human capability. The simplicity of their task
definitions masks the sophisticated statistical and computational techniques required to solve them
effectively, especially when applied to complex, real-world data.

1. *Fundamental Building Blocks:* Classification and clustering are often the *entry points*
   into machine learning because they represent core cognitive tasks that humans perform instinctively.
    * *Classification:* "Is this X or Y?" "What category does this belong to?" This is how we organise
      and understand the world.
    * *Clustering:* "What groups exist within this data?" "Are there natural segments?" This is how
      we identify patterns and structures without prior labels.

2. *Ubiquitous Problems:* Despite seeming simple in a way, these tasks are incredibly common
   and valuable across almost every industry:
    * *Business:* Customer segmentation (clustering), fraud detection (classification), lead
      scoring (classification), product recommendation (can involve both).
    * *Healthcare:* Disease diagnosis (classification), patient subgrouping (clustering).
    * *Science:* Classifying celestial objects, identifying gene expression patterns, grouping species.
    * *Everyday Life:* Spam filtering, facial recognition, news categorization.

3. *Data Availability and Definition:*
    * *Classification:* Requires *labeled data*, meaning you need examples where the correct
      category is already known. This kind of data is relatively common (e.g., historical
      records of transactions, medical diagnoses).
    * *Clustering:* Is *unsupervised*, meaning it doesn't require pre-labeled data. This makes
      it powerful for exploratory data analysis when you don't know what patterns to look for.

4. *Stepping Stones to Complexity:* While the *tasks* themselves might appear simple,
   the *data* they operate on is often incredibly complex, high-dimensional, and noisy.
    * For example, classifying an image as a "cat" or "dog" is a simple human task, but
      for a computer, it involves processing millions of pixels and learning intricate features.
    * Clustering millions of customer transactions to find meaningful segments is by no means simple.

5. *Benchmarking and Interpretability:*
    * Simple classification and clustering tasks often serve as excellent benchmarks for new
      algorithms. Can your new model accurately classify handwritten digits?
    * Many of the simpler algorithms (Linear Regression, Logistic Regression, Decision Trees,
      K-Means, KNN) are also highly *interpretable*. This is crucial in many real-world
      applications where you need to understand *why* a decision was made (e.g., credit scoring,
      medical diagnosis). This can be contrasted to deep learning, which at present is not
      interpretable at any higher level.

6. *Foundation for Advanced Tasks:* Classification and clustering are often components of much more complex systems.
    * Object detection (where an image contains multiple objects to be identified and localised)
      involves repeated classification of regions within an image.
    * Natural Language Processing often relies on classifying words or sentences.
    * Recommendation systems use clustering to group similar users or items, and then
      classification/regression to predict preferences.


### Historical Remarks

Machine learning is, at its heart, applied statistics. Many of these algorithms can be understood
as sophisticated statistical models designed to find patterns and make predictions from data.

*Linear Regression*

The method of least squares, foundational to linear regression, has roots stretching back to the
early 19th century with contributions from Legendre (1805) and Gauss (1809), who developed it to
predict planetary orbits. While the underlying mathematical principles were established then, its
widespread application as a statistical modelling tool, particularly in fields like economics and
social sciences, solidified in the 20th century as computational power made fitting complex linear
models more feasible and its simplicity and interpretability became highly valued.

* *Linear Regression:*
    * *Statistical Relation:* This is a fundamental statistical method. It's about finding the
      best-fitting straight line (or hyperplane in higher dimensions) to describe the relationship
      between a dependent variable and one or more independent variables. It relies on the statistical
      concept of minimizing the sum of squared errors (least squares).
    * *Problems Solved:* Predicting continuous outcomes. Examples: predicting house prices based
      on size and location, sales forecasting based on advertising spend, student performance based
      on study hours.
    * *Why ML Benefits:* While a basic statistical technique, ML frameworks allow for efficient
      computation on large datasets, handling of multiple features, and integration into complex pipelines.


*Logistic Regression*

Developed by statistician David Cox in 1958, Logistic Regression emerged as a powerful statistical
model for binary classification, specifically designed to model the probability of a binary outcome.
It gained prominence as researchers sought methods to predict qualitative outcomes based on quantitative
predictors, offering a more robust alternative to directly fitting linear models to binary responses,
which could yield probabilities outside the meaningful 0-1 range. Its clear probabilistic interpretation
and connections to generalised linear models cemented its place as a fundamental classification algorithm.

* *Logistic Regression:*
    * *Statistical Relation:* Also a statistical model, specifically a generalized linear model. It
      uses the logistic function to model the probability of a binary outcome. It's based on maximum
      likelihood estimation.
    * *Problems Solved:* Binary classification. Examples: predicting whether a customer will churn,
      classifying an email as spam or not, diagnosing a disease (present/absent).
    * *Why ML Benefits:* Similar to linear regression, ML provides the tools for scaling, regularisation,
      and integration into production systems.


*Decision Trees*

The concept of using hierarchical, tree-like structures for decision-making dates back to earlier statistical
methods, but the modern era of Decision Trees truly began with the development of the ID3 algorithm by J.
Ross Quinlan in the late 1970s, followed by its more robust successor, C4.5, in the 1990s. Simultaneously,
CART was popularised by the 1984 book *Classification and Regression Trees* by Breiman, Friedman,
Olshen & Stone, its algorithmic foundation dates back to circa 1977, when the team at Berkeley and Stanford
began development. These algorithms formalised how to recursively partition data based on features to
create interpretable rules, becoming popular for their clarity and ability to handle non-linear relationships.

* *Decision Trees:*
    * *Statistical Relation:* Can be seen as a non-parametric statistical method. They partition the feature
      space into a set of rectangular regions. The splits are determined by statistical measures like Gini
      impurity or information gain (entropy), which quantify the homogeneity of the data within each node.
    * *Problems Solved:* Classification and regression. Examples: customer segmentation, loan default
      prediction, medical diagnosis.
    * *Why ML Benefits:* Their ability to capture non-linear relationships and their interpretability
      make them valuable. ML provides the algorithms to efficiently construct and prune these trees.


*Random Forest*

Building upon the concept of Decision Trees, Random Forest was formalised by Leo Breiman in 2001 (built on
Tin Kam Ho, 1995, Amit & Geman in 1997, Salzberg & Heath, 1993). Its innovation lay in combining multiple
decorrelated decision trees, each trained on a random subset of the data and features, and then aggregating
their predictions (bagging). This ensemble approach was a significant step forward, addressing the inherent
overfitting tendencies of individual decision trees and leading to substantial improvements in predictive
accuracy, making it a highly effective and widely adopted general-purpose machine learning algorithm.

* *Random Forest:*
    * *Statistical Relation:* An ensemble method built upon decision trees. It uses bootstrapping (sampling
      with replacement) and random feature selection, both core statistical sampling techniques, to create
      multiple trees. The final prediction is often an average (regression) or majority vote (classification),
      reducing variance.
    * *Problems Solved:* General-purpose classification and regression. Examples: fraud detection, predicting
      stock prices, image classification.
    * *Why ML Benefits:* Addresses the overfitting issue of individual decision trees by leveraging the
      "wisdom of crowds" concept. ML frameworks are essential for managing and training hundreds or
      thousands of trees efficiently.


*Support Vector Machine (SVM)*

The foundational ideas behind Support Vector Machines originated from Vladimir Vapnik and Alexey Chervonenkis's
work on statistical learning theory in the 1960s, particularly the concept of Vapnik-Chervonenkis (VC) dimension.
However, the modern form of SVM, including the crucial "kernel trick" for handling non-linear data, was largely
developed by Vapnik and his colleagues (notably Corinna Cortes and Vapnik) in the 1990s. Its ability to effectively
classify high-dimensional data by finding the optimal hyperplane with the largest margin, coupled with the kernel
trick, quickly established SVM as a powerful and theoretically well-grounded algorithm.

* *Support Vector Machine (SVM):*
    * *Statistical Relation:* A discriminative classifier that finds an optimal hyperplane that maximally separates
      data points of different classes. It has strong theoretical foundations in statistical learning theory
      (VC). The "kernel trick" allows it to implicitly map data into higher-dimensional spaces, enabling non-linear
      separation.
    * *Problems Solved:* High-dimensional classification. Examples: image recognition, text categorisation,
      bioinformatics.
    * *Why ML Benefits:* Powerful for complex, high-dimensional data where a clear separation boundary exists
      or can be learned. ML provides efficient solvers for the quadratic programming problems involved.


*K-Nearest Neighbours (KNN)*

One of the oldest and simplest non-parametric classification algorithms, the K-Nearest Neighbours rule dates back
to the early 1950s, with fundamental work often attributed to Evelyn Fix and Joseph Hodges in 1951, and later
expanded upon by Thomas Cover and Peter Hart in 1967. Its intuitive principle—classifying a data point based on
the majority class among its closest neighbours—made it a straightforward choice for pattern recognition tasks,
requiring no explicit training phase but relying entirely on the stored training data at prediction time.

* *K-Nearest Neighbors (KNN):*
    * *Statistical Relation:* A non-parametric, instance-based method. Its statistical foundation lies in the
      idea that similar data points are likely to belong to the same class or have similar values. It relies
      on distance metrics (e.g., Euclidean distance), a fundamental statistical concept.
    * *Problems Solved:* Classification and regression. Examples: recommendation systems, anomaly detection,
      handwriting recognition.
    * *Why ML Benefits:* Simplicity and effectiveness for certain datasets. ML frameworks handle efficient
      neighbor searches, especially for large datasets.


*Naive Bayes*

Based on Bayes' Theorem (formulated by Thomas Bayes in the 18th century), the "Naive Bayes" classifier gained
prominence in the machine learning community in the latter half of the 20th century, particularly with the rise
of text classification and information retrieval. Its "naive" assumption of conditional independence between
features, given the class, drastically simplifies computation, making it remarkably efficient and surprisingly
effective for tasks like spam filtering and document categorisation, despite its seemingly oversimplified
probabilistic model.

* *Naive Bayes:*
    * *Statistical Relation:* Based on Bayes' theorem of conditional probability, assuming strong (naive)
      independence between features given the class. This is a probabilistic statistical model.
    * *Problems Solved:* Text classification, spam filtering. Examples: email spam detection, sentiment
      analysis, document categorisation.
    * *Why ML Benefits:* Very efficient and performs well even with limited data due to its strong assumptions.
      ML provides the tools to estimate the probabilities from the data.


*Gradient Boosting (XGBoost, LightGBM)*

Gradient Boosting, as a general framework for building powerful ensemble models, was formally introduced by
Leo Breiman in 1997 and further developed by Jerome Friedman in 1999. It revolutionised supervised learning
by sequentially building weak learners (typically decision trees), with each new learner correcting the errors
of its predecessors by focusing on the residuals. More recent iterations like XGBoost (developed by Tianqi Chen
and Carlos Guestrin, open-sourced in 2014) and LightGBM (developed by Microsoft, open-sourced in 2016)
significantly optimised the original concept for speed and performance, pushing the boundaries of accuracy
on structured data.

* *Gradient Boosting (XGBoost, LightGBM):*
    * *Statistical Relation:* An ensemble technique that builds trees sequentially, with each new tree trying
      to correct the errors of the previous ones. It leverages the concept of gradient descent, a core
      optimisation algorithm in statistics and mathematics, to minimise a loss function.
    * *Problems Solved:* Structured data with high accuracy. Examples: Kaggle competitions, predictive
      maintenance, financial modeling.
    * *Why ML Benefits:* Achieves state-of-the-art results on many tabular datasets by iteratively
      improving predictions. ML frameworks provide highly optimised implementations.


*K-Means*

The K-Means clustering algorithm has a somewhat diffused history, with precursors appearing in the late 1950s
(e.g., Stuart Lloyd's work at Bell Labs in 1957, though published much later). It was formally popularised by
J.B. MacQueen in 1967, and also independently by others like Forgy (1965). Its enduring appeal stems from its
simplicity, efficiency, and effectiveness in partitioning data into a predefined number of spherical clusters,
making it a cornerstone algorithm for unsupervised learning tasks like data segmentation.

* *K-Means:*
    * *Statistical Relation:* A centroid-based clustering algorithm. It aims to partition data into K clusters
      such that each data point belongs to the cluster with the nearest mean. It relies on minimising
      within-cluster variance (sum of squared distances), a statistical measure of spread.
    * *Problems Solved:* Clustering, segmentation. Examples: customer segmentation, image compression,
      document clustering.
    * *Why ML Benefits:* Simple, efficient for large datasets. ML provides implementations that scale and
      handle various data types.


*DBSCAN*

DBSCAN (Density-Based Spatial Clustering of Applications with Noise) was introduced by Martin Ester, Hans-Peter
Kriegel, Jörg Sander, and Xiaowei Xu in 1996. It offered a significant advancement over partition-based clustering
methods like K-Means by its ability to discover clusters of arbitrary shapes and to identify noise points (outliers)
within the data. Its density-based approach, which defines clusters as areas of high density separated by areas
of lower density, filled a crucial gap in clustering algorithms.

* *DBSCAN:*
    * *Statistical Relation:* A density-based clustering algorithm. It identifies clusters as high-density
      regions separated by low-density regions. It doesn't assume spherical clusters and can find arbitrarily
      shaped clusters, and can identify outliers. It uses the statistical concept of local density.
    * *Problems Solved:* Clustering with noise. Examples: anomaly detection, geographical data analysis,
      identifying clusters in scientific data.
    * *Why ML Benefits:* More robust than K-Means for non-spherical clusters and noisy data. ML provides
      efficient spatial querying algorithms.


*PCA (Principal Component Analysis)*

The mathematical underpinnings of Principal Component Analysis can be traced back to Karl Pearson's work in 1901,
where he introduced the method to find lines and planes of best fit to a system of points. It was then independently
developed and named by Harold Hotelling in 1933, who applied it to analyse component analysis in psychology. PCA
became a fundamental statistical tool for dimensionality reduction by transforming data into a new coordinate
system where variance is maximised along orthogonal principal components, finding widespread use in various
scientific and engineering disciplines.

* *PCA (Principal Component Analysis):*
    * *Statistical Relation:* A linear dimensionality reduction technique. It finds orthogonal principal
      components that capture the maximum variance in the data. This involves eigenvalue decomposition
      of the covariance matrix, a core concept in multivariate statistics.
    * *Problems Solved:* Dimensionality reduction, noise reduction, data visualisation. Examples:
      reducing features for a machine learning model, visualising high-dimensional data, compressing images.
    * *Why ML Benefits:* Crucial for managing high-dimensional datasets and improving model performance
      by removing redundant information. ML libraries provide optimized implementations for large matrices.


*t-SNE / UMAP*

The t-Distributed Stochastic Neighbour Embedding (t-SNE) algorithm was developed by Laurens van der Maaten and
Geoffrey Hinton and published in 2008, revolutionising the visualisation of high-dimensional data. Building on
earlier "Stochastic Neighbour Embedding" (SNE), t-SNE improved its ability to preserve local and global data
structures for clearer visualisation. More recently, Uniform Manifold Approximation and Projection (UMAP),
introduced by Leland McInnes, John Healy, and James Melville in 2018, emerged as a faster and often more
scalable alternative to t-SNE, offering similar or better visualisation quality and improved preservation
of global structure for dimensionality reduction and clustering.

* *t-SNE / UMAP:*
    * *Statistical Relation:* Non-linear dimensionality reduction techniques that focus on preserving local
      and global structures in the data, respectively. While more recent and computationally intensive than
      PCA, their underlying principles still relate to manifold learning and preserving relationships
      (distances or similarities) between data points in a lower-dimensional space, which has statistical
      implications for data representation.
    * *Problems Solved:* Visualisation, clustering. Examples: visualising high-dimensional genomic data,
      understanding complex data relationships.
    * *Why ML Benefits:* Essential for making sense of complex, high-dimensional data and gaining insights.
      ML provides the sophisticated optimisation algorithms required.


*Apriori / FP-Growth*

The Apriori algorithm, a seminal algorithm for mining frequent item sets and association rules from transactional
databases (like market basket data), was introduced by Rakesh Agrawal and Ramakrishnan Srikant in 1994. Its
development was a breakthrough for discovering relationships between items. Following Apriori, the FP-Growth
(Frequent Pattern Growth) algorithm, introduced by Jiawei Han, Jian Pei, and Yiwen Yin in 2000, emerged as a
more efficient alternative that avoids the candidate generation step, significantly speeding up the frequent
item-set mining process by using a compact tree structure (FP-tree).

* *Apriori / FP-Growth:*
    * *Statistical Relation:* Algorithms for discovering association rules in transactional datasets.
      They identify frequently occurring itemsets and then generate rules based on statistical measures
      like support, confidence, and lift.
    * *Problems Solved:* Market basket analysis. Examples: "Customers who buy milk and bread also buy eggs,"
      product recommendations.
    * *Why ML Benefits:* Enable the discovery of hidden patterns in large transactional datasets, which
      is commercially valuable. ML provides the frameworks to efficiently search for these patterns.


*Neural Networks (Multilayer Perceptrons - MLP)*

The concept of artificial neural networks dates back to the McCulloch-Pitts neuron model in the 1940s and Frank
Rosenblatt's perceptron in the 1950s. However, the "multilayer perceptron" with backpropagation, the crucial
algorithm for training these deep structures, was popularised in the mid-1980s by a resurgence of interest in
connectionism, particularly through the work of David Rumelhart, Geoffrey Hinton, and Ronald Williams. This
breakthrough allowed for the training of networks with hidden layers, enabling them to learn complex non-linear
relationships, marking a significant step towards modern deep learning.

* *Neural Networks (MLP, CNN, RNN/LSTM/GRU):*
    * *Statistical Relation:* Deep learning models, while often framed differently, are essentially highly
      flexible statistical function approximators. They learn complex non-linear relationships by adjusting
      weights and biases through optimisation algorithms like stochastic gradient descent, which is a
      statistical optimisation technique.
        * *MLP:* General function approximation.
        * *CNN:* Exploits spatial correlations, drawing parallels to local feature detectors and
          convolutions used in signal processing (which has statistical applications).
        * *RNN/LSTM/GRU:* Designed for sequential data, modeling temporal dependencies.
          They can be seen as highly complex time-series models, a field rich in statistics.
    * *Problems Solved:*
        * *MLP:* General-purpose, e.g., tabular data prediction, basic classification.
        * *CNN:* Image recognition, object detection, medical imaging.
        * *RNN/LSTM/GRU:* Natural language processing (translation, text generation), speech recognition,
          time-series forecasting.
    * *Why ML Benefits:* Their power lies in their ability to learn extremely complex, hierarchical
      representations from raw data, often outperforming traditional methods on unstructured data.
      This requires vast computational resources and specialized ML frameworks (TensorFlow, PyTorch).


*CNN (Convolutional Neural Networks)*

While early ideas related to convolutional processing in neural networks (like the Neocognitron by Kunihiko
Fukushima in the early 1980s) existed, Convolutional Neural Networks (CNNs) truly rose to prominence with the
work of Yann LeCun and his colleagues in the late 1980s and early 1990s, particularly for tasks like optical
character recognition (e.g., LeNet-5 for digit recognition). Their ability to exploit spatial hierarchies and
achieve translation invariance through shared weights and pooling layers made them exceptionally effective for
image recognition, laying the groundwork for the deep learning revolution in computer vision of the 2010s.


*RNN / LSTM / GRU*

Recurrent Neural Networks (RNNs) were developed in the 1980s to process sequential data, but their practical
application was limited by the "vanishing gradient" problem, making it difficult for them to learn long-term
dependencies. This challenge was largely addressed by the invention of the Long Short-Term Memory (LSTM) network
by Sepp Hochreiter and Jürgen Schmidhuber in 1997, which introduced gates to control information flow. The Gated
Recurrent Unit (GRU), a slightly simplified variant of LSTM, was introduced by Kyunghyun Cho and collaborators
in 2014. These advancements made RNNs, LSTMs, and GRUs indispensable for tasks involving sequences like natural
language processing, speech recognition, and time-series analysis.


*GANs (Generative Adversarial Networks)*

Generative Adversarial Networks (GANs) were introduced by Ian Goodfellow and his colleagues in 2014, representing
a groundbreaking development in unsupervised learning for generative modelling. Their innovative architecture
involves two competing neural networks—a generator and a discriminator—locked in an adversarial training process.
This competitive dynamic allows GANs to learn to produce highly realistic and novel synthetic data (e.g., images,
audio, text) that can be remarkably difficult to distinguish from real data, opening new frontiers in creative
AI applications.

* *GANs (Generative Adversarial Networks):*
    * *Statistical Relation:* A generative model that learns the underlying probability distribution of a dataset
      to generate new, similar data. The "adversarial" training process involves a generator and a discriminator
      network, which are essentially trying to outsmart each other by learning to approximate the real data
      distribution and distinguish real from fake, respectively. This is a very advanced form of statistical
      modeling of distributions.
    * *Problems Solved:* Data generation, image synthesis, style transfer. Examples: generating realistic
      faces, creating art, data augmentation.
    * *Why ML Benefits:* Pushed the boundaries of what's possible in generative modeling, leading to highly
      realistic synthetic data. ML provides the infrastructure for complex adversarial training.


*Reinforcement Learning*

The field of Reinforcement Learning (RL) has deep roots stretching back to early work in cybernetics, control
theory, and animal learning psychology in the mid-20th century. Key theoretical advancements in the 1980s and
1990s, notably Richard Sutton and Andrew Barto's foundational book "Reinforcement Learning: An Introduction"
(1998) and the development of algorithms like Q-learning, solidified it as a distinct paradigm. However, RL
experienced a dramatic resurgence in the 2010s with the advent of deep reinforcement learning, exemplified by
DeepMind's successes in training agents to master complex games like Go and Atari, showcasing its power in
areas like robotics and autonomous control.

* *Reinforcement Learning:*
    * *Statistical Relation:* Involves an agent learning to make decisions by interacting with an environment
      to maximise a cumulative reward signal. While distinct from supervised/unsupervised learning, it's
      deeply rooted in statistical decision theory, Markov Decision Processes (MDPs), and dynamic programming.
      The agent estimates state-action values or policies based on observed rewards, a statistical estimation problem.
    * *Problems Solved:* Game AI, robotics, control systems. Examples: AlphaGo, self-driving cars,
      personalised recommendations (as a control problem).
    * *Why ML Benefits:* Allows agents to learn optimal behaviours in complex, dynamic environments without
      explicit programming. ML provides the algorithms (e.g., Q-learning, policy gradients) and computational
      power for large-scale simulations and learning.

