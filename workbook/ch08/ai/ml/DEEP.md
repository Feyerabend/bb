
## Deep Learning

Deep learning is a subset of machine learning, which itself is a branch of
artificial intelligence (AI). While traditional AI includes rule-based systems
and symbolic reasoning, deep learning focuses on learning patterns from data
using neural networks. It has driven advances in computer vision, natural language
processing, and reinforcement learning, making AI systems more autonomous and
capable of generalising from experience.

However, deep learning is still a form of narrow AI--it excels at specific tasks
but lacks true general intelligence (AGI). Current research explores combining
deep learning with symbolic reasoning, causal inference, and self-supervised
learning to move toward more general AI capabilities.

Deep learning is thus a subfield of machine learning that focuses on using
*artificial neural networks* (ANN) to model and solve complex problems. Unlike
traditional machine learning methods that often rely on manually engineered
features, deep learning automatically discovers patterns and representations
from raw data through multiple layers of abstraction.

At the core of deep learning are artificial neural networks, which are inspired
by the structure and function of the human brain. These networks consist of layers of
interconnected nodes (neurons), where each connection has an associated weight that is
adjusted during training. The most common type of neural network used in deep learning
is the feedforward neural network, but more advanced architectures, such as convolutional
neural networks (CNNs) and recurrent neural networks (RNNs), are specifically designed
for tasks like image recognition and sequence processing.

Training a deep learning model typically involves backpropagation, an algorithm that
adjusts the weights of the network by computing gradients of a loss function with respect
to the model’s parameters. This process is optimised using variants of gradient descent,
such as stochastic gradient descent (SGD) or adaptive methods like Adam.

Deep learning has been successful in various applications, including image and speech
recognition, natural language processing (NLP), reinforcement learning, and even
generative models like GANs (Generative Adversarial Networks) and transformers (such as GPT).
Its effectiveness is largely attributed to the availability of large datasets, powerful
computing resources (especially GPUs and TPUs), and improved training techniques.



### 1. Neural Networks and Architectures

Deep learning is built upon artificial neural networks, which consist of *layers* of
interconnected nodes (neurons). The simplest type is the *feedforward* neural network,
where information moves in one direction, from input to output. However, specialized
architectures have been developed for different tasks.

#### 1.1 Convolutional Neural Networks (CNNs)

CNNs are particularly effective for *image* and *video* processing. Instead of fully connected
layers, they use convolutional layers, which apply filters (kernels) to detect spatial
features like edges and textures.
Key components:
- Convolutional layers: Extract hierarchical features.
- Pooling layers: Reduce spatial dimensions (such as max pooling).
- Fully connected layers: Make final predictions.

CNNs, such as AlexNet, VGG, ResNet, and EfficientNet, have driven state-of-the-art
performance in computer vision tasks.

#### 1.2 Recurrent Neural Networks (RNNs)

RNNs are designed for *sequential* data, such as time series and natural language processing
(NLP). Unlike feedforward networks, RNNs have loops that allow information to persist
across time steps. However, vanilla RNNs suffer from vanishing gradients, making them
ineffective for long sequences.
- LSTMs (Long Short-Term Memory): Introduce gating mechanisms to retain important
  information over long sequences.
- GRUs (Gated Recurrent Units): A simpler alternative to LSTMs with fewer parameters.

Although RNNs were widely used in NLP, they have now been largely replaced by *transformers*.



### 2. Transformers and NLP

Transformers revolutionised deep learning for NLP and are now widely used in models
like BERT, GPT, and T5. Unlike RNNs, they do not process data sequentially, making
them more parallelisable and efficient.
- Self-attention mechanism: Allows the model to focus on important words in a sequence,
  regardless of their position.
- Positional encodings: Compensate for the lack of recurrence by injecting order
  information into inputs.
- Multi-head attention: Enables the model to capture different aspects of
 relationships between words.

GPT models (such as ChatGPT) use a decoder-only transformer architecture,
while BERT uses an encoder-only architecture for bidirectional understanding.


### 3. Generative Adversarial Networks (GANs)

GANs are a class of deep learning models used for generative tasks, such as image synthesis,
style transfer, and deepfake generation. A GAN consists of two competing neural networks:
- Generator (G): Tries to create realistic data (e.g. fake images).
- Discriminator (D): Tries to distinguish between real and generated data.

During training, the generator improves until the discriminator can no longer differentiate
between real and fake data. GANs have led to breakthroughs in image generation (StyleGAN,
BigGAN), super-resolution, and domain adaptation.


### 4. Reinforcement Learning (RL)

Reinforcement learning (RL) is another key area of deep learning, where an agent learns
to make decisions by interacting with an environment. Unlike supervised learning, RL is
based on rewards and penalties.
- Q-learning: A fundamental RL algorithm where an agent learns a Q-table mapping states to actions.
- Deep Q-Networks (DQN): Uses deep learning to approximate Q-values for high-dimensional inputs like images.
- Policy gradient methods: Directly optimise the policy (e.g., PPO, A2C).

Deep RL has been used in robotics, game playing (e.g., AlphaGo, OpenAI Five), and autonomous driving.



### 5. Optimisation Techniques in Deep Learning

Deep learning models require efficient optimisation strategies:
- Gradient Descent: The foundation of learning in neural networks.
- SGD (Stochastic Gradient Descent): Updates weights using small batches.
- Adam: A more adaptive optimisation method, commonly used in practice.

Regularisation techniques like dropout, batch normalisation, and weight decay help prevent overfitting.



### 6. Self-Supervised Learning and Beyond

Self-supervised learning is an emerging paradigm where models learn from data without explicit labels.
This has been key to training large-scale models like BERT, GPT, and SimCLR (for vision).
- Contrastive Learning: Learns representations by distinguishing between similar and dissimilar data points.
- Masked Language Models (MLMs): Pre-train transformers by predicting missing words (e.g. BERT).



### Conclusion

Deep learning has transformed AI, enabling breakthroughs in vision, language, and autonomous decision-making.
CNNs dominate image tasks, transformers rule NLP, GANs enable synthetic media, and RL powers intelligent
agents. As compute power and datasets continue to grow, deep learning will keep pushing the boundaries
of artificial intelligence.
