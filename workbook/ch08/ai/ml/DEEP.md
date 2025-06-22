
## Deep Learning

Deep learning is a highly impactful subset of machine learning, which itself is a branch of artificial
intelligence (AI). While traditional AI systems ([GOFAI](./../gofai/)) often rely on rule-based logic
or symbolic reasoning, deep learning distinguishes itself by focusing on learning intricate patterns
directly from vast amounts of data using specialised structures called *artificial neural networks* (ANN).
This approach has been a primary driver of significant advancements in various AI domains, including
computer vision, natural language processing (NLP), and reinforcement learning, making AI systems more
autonomous and capable of generalising from experience.

Unlike traditional machine learning methods that frequently depend on *feature engineering*--where humans
manually select, transform, or create input variables to improve model performance--deep learning models
inherently automate much of this process. Built from multi-layered neural networks, they learn hierarchical
representations directly from raw data through multiple layers of abstraction. This capability makes deep
learning exceptionally effective for complex tasks such as image recognition, speech processing, and
natural language understanding, often achieving state-of-the-art results where traditional methods struggle.

However, it's important to note that deep learning, in its current form, is still considered a type of
*narrow AI*. This means it excels remarkably at specific, defined tasks but lacks the broader, general
intelligence (AGI) that allows humans to apply knowledge across diverse domains. Current research actively
explores combining deep learning with other AI paradigms, such as symbolic reasoning, causal inference,
and self-supervised learning, to move closer to more generalised AI capabilities.


### Neural Networks and Architectures

At the core of deep learning are artificial neural networks (ANNs), computational models inspired by the
structure and function of the human brain. These networks consist of layers of interconnected nodes, often
referred to as "neurons," where each connection has an associated weight. During the training process,
these weights are iteratively adjusted to minimise a loss function, allowing the network to learn from data.

The simplest type of neural network is the *feedforward neural network (FNN)*, also known as a multilayer
perceptron (MLP). In FNNs, information flows in one direction only--from the input layer, through one or more
hidden layers, and finally to the output layer. While MLPs are general-purpose function approximators capable
of learning complex non-linear relationships, their effectiveness can be limited for specific data types
like images or sequences.

| *Algorithm* | *Type* | *Typical Use Cases* | *Key Properties* |
|---|---|---|---|
| [Neural Networks](./mlp/) (MLP) | Supervised | General-purpose | Flexible, powerful, requires large data |
| [CNN](./cnn/) (Convolutional NN) | Supervised | Image data | Exploits spatial structure, translation invariance |
| [RNN](./rnn/) / [LSTM](./rnn/) / [GRU](./rnn/) | Supervised | Sequence data (text, time-series) | Captures temporal dependencies, vanishing gradient challenges |
| [GANs](./gan/) (Generative Adversarial Networks) | Unsupervised | Data generation | Adversarial training, high-quality synthetic data |

For different types of data and tasks, more specialised architectures have been developed:

#### Convolutional Neural Networks (CNNs)

CNNs are particularly powerful for processing data with a known grid-like topology, such as *images* and
*video*. Instead of relying solely on fully connected layers, CNNs primarily use *convolutional layers*,
which apply learnable filters (or kernels) across the input data. These filters are designed to automatically
detect spatial features like edges, textures, and more complex patterns at various levels of abstraction
within the image.

Key components of CNNs include:
* *Convolutional Layers*: These layers perform the core operation of applying filters to input to extract
  hierarchical features.
* *Pooling Layers*: Typically, pooling layers (such as max pooling) follow convolutional layers and serve
  to reduce the spatial dimensions of the feature maps, which helps in reducing computational cost and
  making the detected features more robust to small shifts or distortions.
* *Fully Connected Layers*: After several convolutional and pooling layers, the high-level features are
  flattened and fed into traditional fully connected layers for final classification or regression.

CNNs, exemplified by architectures like AlexNet, VGG, ResNet, and EfficientNet, have revolutionized computer
vision tasks, achieving state-of-the-art performance in areas like image recognition, object detection,
and medical imaging.

#### Recurrent Neural Networks (RNNs), LSTMs, GRUs

Recurrent Neural Networks (RNNs) are specifically designed to handle *sequential data*, such as time series,
speech, and natural language. Unlike feedforward networks, RNNs possess internal loops that allow information
to persist across time steps, enabling them to capture temporal dependencies within the data. This "memory"
makes them suitable for tasks where the order of information is crucial.

However, traditional or "vanilla" RNNs often suffer from practical limitations, most notably the
*vanishing gradient problem*. This issue makes it difficult for them to learn and retain information
over long sequences, hindering their effectiveness for long-term dependencies. To address this, more
advanced architectures were developed:

* *Long Short-Term Memory (LSTM) networks*: Introduced by Sepp Hochreiter and Jürgen Schmidhuber in 1997,
  LSTMs overcome the vanishing gradient problem by incorporating sophisticated "gating mechanisms" (input,
  forget, and output gates). These gates regulate the flow of information into and out of a memory cell,
  allowing LSTMs to selectively retain or discard information over extended sequences.
* *Gated Recurrent Units (GRUs)*: Developed by Kyunghyun Cho and collaborators in 2014, GRUs are a slightly
  simplified variant of LSTMs. They achieve similar performance to LSTMs but with fewer parameters, making
  them computationally more efficient in some cases.

While RNNs, LSTMs, and GRUs were widely used for sequence processing, particularly in Natural Language
Processing (NLP) tasks like machine translation and text generation, they have been largely superseded
by *Transformers* in recent years.


### Transformers and NLP

Transformers represent a revolutionary deep learning architecture, fundamentally changing the landscape
of Natural Language Processing (NLP) and extending their influence to other domains. Models like BERT,
GPT, and T5 are built upon the Transformer architecture. A key innovation of Transformers is their ability
to process data non-sequentially, which allows for much greater parallelisation during training compared
to RNNs, leading to significant efficiency gains.

The core mechanism enabling this parallel processing and improved understanding of relationships within
sequences is the *self-attention mechanism*. This mechanism allows the model to weigh the importance of
different words (or tokens) in an input sequence relative to each other, regardless of their position.
For example, when processing a sentence, a Transformer can simultaneously consider how each word relates
to every other word, capturing long-range dependencies effectively.

Other important components of the Transformer architecture include:
* *Positional Encodings*: Since Transformers do not process sequences sequentially, positional encodings
  are added to the input embeddings to inject information about the relative or absolute position of tokens
  in the sequence.
* *Multi-head Attention*: This extension of self-attention allows the model to jointly attend to information
  from different representation subspaces at different positions. Essentially, it enables the model to
  capture various aspects of relationships between words simultaneously.

Transformer models typically come in different architectural flavours based on their use of the encoder
and decoder components:
* *GPT (Generative Pre-trained Transformer) models*: Such as ChatGPT, primarily use a *decoder-only*
  transformer architecture. They are adept at generative tasks, like producing coherent and contextually
  relevant text by predicting the next word in a sequence.
* *BERT (Bidirectional Encoder Representations from Transformers)*: Utilises an *encoder-only* architecture
  and is designed for tasks requiring a deep, bidirectional understanding of context, such as text
  classification, question answering, and named entity recognition.


### Generative Adversarial Networks (GANs)

Generative Adversarial Networks (GANs), introduced by Ian Goodfellow and colleagues in 2014, represent a
groundbreaking class of deep learning models designed for *generative tasks*. These tasks involve creating
new data instances that resemble a given training dataset. GANs have found remarkable success in applications
such as image synthesis, style transfer, and even the creation of highly realistic "deepfake" media.

A GAN operates based on an innovative adversarial training framework involving two competing neural networks:
* *Generator (G)*: This network's role is to produce synthetic data (e.g., fake images) that are as realistic
  as possible, attempting to mimic the statistical properties of the real data.
* *Discriminator (D)*: This network acts as a critic; its job is to distinguish between real data samples
  (from the training set) and the synthetic data generated by the Generator.

During the training process, the Generator and Discriminator engage in a continuous "game." The Generator
constantly tries to improve its ability to create more convincing fakes, while the Discriminator simultaneously
improves its ability to detect these fakes. This competitive dynamic drives both networks to improve, until
ideally, the Generator produces data so realistic that the Discriminator can no longer reliably differentiate
it from real data.

GANs have led to significant breakthroughs in areas such as high-quality image generation (e.g., StyleGAN,
BigGAN), super-resolution (enhancing image detail), and domain adaptation (transforming images from one domain
to another while retaining content).


### Deep Reinforcement Learning

Reinforcement Learning (RL) is a paradigm where an *agent* learns to make optimal decisions by interacting
with an *environment* to maximise a cumulative *reward signal*. While traditional RL methods involve statistical
decision theory, Markov Decision Processes (MDPs), and dynamic programming, *Deep Reinforcement Learning (Deep RL)*
integrates deep neural networks into this framework. This integration allows RL agents to process raw,
high-dimensional inputs (like pixel data from video games) and learn complex policies without explicit
programming.

Key concepts and algorithms in Deep RL include:
* *Q-learning*: A fundamental RL algorithm where an agent learns an optimal policy by learning the value of
  taking a certain action in a certain state (Q-values).
* *Deep Q-Networks (DQN)*: To handle environments with vast state spaces (like those involving images),
  DQN uses a deep neural network to approximate the Q-values, allowing the agent to learn directly from
  high-dimensional inputs.
* *Policy Gradient Methods*: These methods directly optimise the agent's policy (the mapping from states
  to actions) to maximise the expected cumulative reward, often using algorithms like Proximal Policy
  Optimisation (PPO) or Asynchronous Advantage Actor-Critic (A2C).

Deep RL has achieved remarkable successes in various applications, notably:
* *Game AI*: Exemplified by DeepMind's AlphaGo, which mastered the complex game of Go, and OpenAI Five, which excelled in Dota 2.
* *Robotics*: Training robots to perform complex manipulation tasks and navigate environments.
* *Autonomous Driving*: Developing control systems for self-driving vehicles.

Deep RL allows agents to learn optimal behaviours in complex, dynamic environments without explicit programming,
with machine learning providing the necessary algorithms and computational power for large-scale simulations and learning.


### Optimisation Techniques in Deep Learning

Training deep learning models involves iteratively adjusting the network's weights and biases to minimise a predefined *loss
function*. This process is essentially an optimisation problem, and it heavily relies on various optimisation techniques:

* *Gradient Descent*: This is the foundational optimisation algorithm in neural networks. It works by iteratively moving in
  the direction opposite to the gradient of the loss function with respect to the model's parameters. The gradient indicates
  the direction of the steepest ascent, so moving in the opposite direction leads to the minimum of the loss function.
* *SGD (Stochastic Gradient Descent)*: While standard gradient descent computes the gradient over the entire dataset, SGD
  updates the weights using only a small *batch* of randomly selected training examples in each iteration. This makes the
  training process much faster and can help escape shallow local minima, although the updates are noisier.
* *Adam (Adaptive Moment Estimation)*: Adam is one of the most widely used and effective adaptive optimisation methods in
  deep learning. It combines the benefits of two other extensions of SGD: AdaGrad (which adapts learning rates based on the
  square of past gradients) and RMSProp (which uses a moving average of squared gradients). Adam computes adaptive learning
  rates for each parameter, making it suitable for a wide range of problems and often converging faster.

Beyond core optimisation algorithms, *regularisation techniques* are crucial for preventing *overfitting*--a phenomenon where
a model learns the training data too well, leading to poor performance on unseen data. Common regularisation techniques include:
* *Dropout*: During training, dropout randomly sets a fraction of neuron activations to zero in each layer. This prevents
  neurons from co-adapting too much and forces the network to learn more robust features.
* *Batch Normalisation*: This technique normalises the input features for each layer within a mini-batch. It helps stabilise
  and speed up the training process by reducing internal covariate shift, allowing for higher learning rates.
* *Weight Decay (L2 Regularisation)*: This technique adds a penalty to the loss function proportional to the square of the
  weights. This discourages large weights, effectively simplifying the model and reducing its tendency to overfit.

These optimisation and regularisation techniques are vital for efficiently training deep learning models and ensuring their
good generalisation performance on new data.


### Self-Supervised Learning and Beyond

Self-supervised learning (SSL) is an emerging and rapidly advancing paradigm in machine learning where models
learn valuable representations from data *without explicit human-provided labels*. Instead, the data itself
provides the supervision. This is achieved by designing "pretext tasks" where part of the data is used to predict
another part, generating supervisory signals automatically. This approach has been instrumental in training 
large-scale models, particularly in natural language processing and computer vision, like BERT, GPT, and SimCLR.

Two prominent examples of self-supervised learning techniques are:
* *Contrastive Learning*: In this approach, the model learns representations by distinguishing between similar
  and dissimilar data points. For instance, in computer vision, different augmented views of the same image are
  considered positive pairs (similar), while augmented views of different images are negative pairs (dissimilar).
  The model is trained to bring positive pairs closer in the embedding space and push negative pairs further apart.
* *Masked Language Models (MLMs)*: Predominantly used for pre-training Transformer models like BERT, MLMs learn
  contextual word representations by predicting words that have been "masked" (hidden) in a sentence. By forcing
  the model to reconstruct missing information based on its surrounding context, it develops a rich understanding
  of language semantics and syntax.

Self-supervised learning significantly reduces the reliance on expensive, manually labeled datasets, making it
possible to leverage massive amounts of unlabelled data for pre-training. The representations learned through SSL
can then be fine-tuned on smaller labeled datasets for specific downstream tasks, often achieving performance
comparable to or even surpassing fully supervised methods.


### Deep Learning Applications

Deep learning has profoundly impacted various fields, leading to breakthroughs and transforming
how AI systems solve complex problems:

* *Computer Vision*: Deep learning, particularly CNNs, has revolutionised computer vision.
  Applications include:
    * *Image Recognition and Classification*: Identifying objects, scenes, or people in images
      (e.g., classifying a cat or dog).
    * *Object Detection*: Locating and identifying multiple objects within an image.
    * *Image Segmentation*: Dividing an image into regions of pixels that belong to certain classes.
    * *Medical Imaging*: Aiding in disease diagnosis from X-rays, MRIs, and CT scans.
    * *Facial Recognition*: Identifying individuals based on their faces.

* *Natural Language Processing (NLP)*: Transformers and earlier RNN-based architectures have driven
  immense progress in NLP. Applications include:
    * *Machine Translation*: Translating text from one language to another (e.g., Google Translate).
    * *Text Generation*: Creating human-like text for chatbots, content creation, and summarisation.
    * *Sentiment Analysis*: Determining the emotional tone of text (e.g., positive, negative, neutral).
    * *Speech Recognition*: Converting spoken language into text.
    * *Question Answering*: Providing direct answers to questions based on given text.

* *Deep Reinforcement Learning*: By combining deep learning with reinforcement learning, agents can
  learn to perform complex tasks in dynamic environments. Applications include:
    * *Game AI*: Developing agents that can master complex games (e.g., AlphaGo mastering Go,
      OpenAI Five in Dota 2).
    * *Robotics*: Training robots for navigation, manipulation, and control in real-world settings.
    * *Autonomous Driving*: Enabling self-driving vehicles to perceive their environment, make
      decisions, and control the vehicle.

* *Generative Models*: GANs and other generative architectures are used to create new, synthetic
  data. Applications include:
    * *Image Synthesis*: Generating realistic images of faces, landscapes, or objects that don't exist.
    * *Style Transfer*: Applying the artistic style of one image to the content of another.
    * *Data Augmentation*: Creating additional training data to improve model robustness.

* *Language Models (LMs)*: A significant application area within NLP, LMs specialise in
  understanding and generating human language. While simpler LMs predict the next word
  in a sentence, advanced deep learning-based LMs (like GPT) can generate coherent articles,
  converse naturally, and perform a wide array of language-related tasks.

Deep learning's effectiveness across these diverse applications is largely attributed to the
availability of large datasets, powerful computing resources (especially GPUs and TPUs), and
continuous improvements in training techniques. As computational power and datasets continue
to expand, deep learning is expected to further push the boundaries of artificial intelligence.


*Continue read about the [challenges](./CHALLENGE.md) of ML and deep learning ..*
