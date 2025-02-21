
## Projects on MNIST ..

As you might have noticed by running the included code, it hasn't got very good accuracy.
This is one things of which you might improve further.


### Project 1: Building a Simple Neural Network from Scratch

You will develop a simple feedforward neural network with one hidden layer, using only
Python's built-in libraries. The network will be trained using the MNIST dataset and will
classify digits (0-9). The project introduces key machine learning concepts such as data
preprocessing, forward propagation, backpropagation, gradient descent, and activation functions.

Objective: Implement a basic neural network from scratch to recognise handwritten digits
from the MNIST dataset.


Key Learning Points:
- Understanding how neural networks work internally
- Implementing forward and backward propagation without external libraries
- Training a network on real-world data
- Evaluating model accuracy

Extensions & Challenges:
- Add another hidden layer to increase network complexity
- Experiment with different activation functions (e.g., ReLU instead of Sigmoid)
- Implement batch training instead of single-image updates


### Project 2: Neural Networks Without Libraries: Why Optimisation Matters

While the provided neural network works, it lacks efficiency and advanced optimisation techniques.
In this project, students will analyse the bottlenecks in the implementation and improve the model's
accuracy and training speed.

Objective: Understand the efficiency of neural networks by implementing optimisations.


Key Learning Points:
- Identifying inefficiencies in a neural network
- Implementing weight initialisation strategies (Xavier or He initialisation)
- Experimenting with learning rate schedules
- Introducing momentum-based optimisation (e.g., using a basic version of Adam or RMSProp)

Extensions & Challenges:
- Implement mini-batch gradient descent for faster convergence
- Compare results with a NumPy-based version of the model
- Reduce memory consumption by optimising data structures


### Project 3: Understanding Backpropagation with Visualization

Backpropagation is the backbone of modern neural networks. You will modify the existing
code to visualise weight updates and loss values over time. They will use simple plots
to track how the neural network learns over multiple epochs.

Objective: Gain a deeper understanding of how backpropagation updates weights.


Key Learning Points:
- Visualising the learning process of a neural network
- Understanding how gradients affect weight updates
- Debugging training issues using loss graphs

Extensions & Challenges:
- Use Matplotlib to visualise loss over time
- Create an interactive dashboard to track model performance
- Experiment with different hyperparameters and plot their effects


### Project 4: Neural Networks on a Budget: Training on Limited Data

This project challenges students to achieve reasonable accuracy using fewer training examples.
The focus is on improving generalisation with limited data, by implementing techniques such
as data augmentation, weight regularisation, and dropout.

Objective: Train a neural network using only a subset of MNIST data and analyse performance.


Key Learning Points:
- Training models with limited data
- Preventing overfitting using dropout and weight decay
- Understanding bias-variance tradeoffs

Extensions & Challenges:
- Implement L2 regularisation (weight decay)
- Apply simple data augmentation techniques (flipping, noise injection)
- Compare performance with a full dataset training


### Project 5: Rebuilding This Model with NumPy for Speed

This project challenges students to rewrite the current neural network using NumPy, replacing
Python's inefficient loops with vectorised operations. This will improve training speed and
provide insights into why optimised libraries like TensorFlow or PyTorch are necessary.

Objective: Replace the existing Python loops with efficient NumPy operations.


Key Learning Points:
- Using NumPy for efficient numerical computation
- Understanding vectorised operations for neural networks
- Comparing execution time and accuracy before and after optimisation

Extensions & Challenges:
- Implement NumPy-based batch processing for training
- Compare execution time with the original implementation
- Add support for different activation functions


### Project 6: From Fully Connected to Convolutional Networks

The current model processes images as 1D vectors, which discards spatial relationships.
This project involves modifying the neural network to use convolutional layers, preserving
spatial structure for better performance.

A prebuilt script which you can start with, can be seen in [CNN](./cnn.py).
<details>
<summary>Results from running the script.</summary> 
Testing CNN ..
Accuracy: 67.00%

Confusion Matrix:
       0     1     2     3     4     5     6     7     8     9
 0:   543     5    59    71     5    52    17    37   160    31
 1:     1  1072     0    31    12     8    10     0     1     0
 2:    28    12   410   399     8     6    28    35    69    37
 3:    17    44    42   770     0     6    15    56    40    20
 4:     9    58     3    18   648    27    11    71    58    79
 5:    10    19    22    74    21   525    51    85    64    21
 6:     5    29    24     2    10    30   850     2     4     2
 7:    15    13     7    57    13     3     1   752    14   153
 8:    91    17    20   237    19    53    19    40   407    71
 9:    35     9     4    18     5    11     1   175    28   723

Confusion Matrix (Bar Chart):

0: █████████████████████████████████████████████       980
1: ████████████████████████████████████████████████████  1135
2: ████████████████████████████████████████████████    1032
3: ███████████████████████████████████████████████     1010
4: █████████████████████████████████████████████       982
5: █████████████████████████████████████████           892
6: ████████████████████████████████████████████        958
7: ███████████████████████████████████████████████     1028
8: █████████████████████████████████████████████       974
9: ███████████████████████████████████████████████     1009
</details>

Objective: Transition from a simple fully connected neural network to a
*convolutional neural network* (CNN) for image classification.


Key Learning Points:
- Understanding convolutional layers and why they are effective for image classification
- Implementing feature extraction through convolution and pooling layers
- Comparing fully connected networks vs. CNNs in terms of accuracy and efficiency

Extensions & Challenges:
- Implement a basic CNN with 1-2 convolutional layers and ReLU activation
- Use max pooling to reduce spatial dimensions
- Compare training speed and accuracy against the original fully connected model


### Project 7: Building a Small-Scale Autoencoder for MNIST

Instead of classification, this project focuses on learning efficient representations
of MNIST digits using an autoencoder. Students will implement an encoder-decoder architecture,
compressing images into a lower-dimensional space and then reconstructing them.

Objective: Train an autoencoder to compress and reconstruct MNIST digits.


Key Learning Points:
- Understanding unsupervised learning with autoencoders
- Exploring bottleneck representations and dimensionality reduction
- Visualising reconstructed images and loss reduction over time

Extensions & Challenges:
- Experiment with different loss functions (Mean Squared Error vs. Cross-Entropy)
- Implement a denoising autoencoder by adding noise to inputs
- Compare learned features from different architectures


### Project 8: Handwritten Digit Recognition with KNN vs. Neural Networks

This project challenges students to implement a k-NN classifier for MNIST and compare its accuracy,
training time, and inference speed against the neural network. This provides insight into when deep
learning is necessary and when simpler models suffice.

Objective: Compare a simple machine learning algorithm (K-Nearest Neighbours) against the neural network model.


Key Learning Points:
- Understanding instance-based learning (KNN) vs. parametric learning (NNs)
- Measuring accuracy and speed trade-offs for different models
- Exploring distance metrics (Euclidean vs. Manhattan)

Extensions & Challenges:
- Implement PCA to reduce MNIST dimensionality before using k-NN
- Compare k-NN with different values of k and distance metrics
- Explore using an SVM as another traditional machine learning alternative


### Project 9: Neural Network Training with Genetic Algorithms

This project moves away from gradient-based learning and instead optimises the neural network's
weights using a genetic algorithm (GA). Students will implement mutation, crossover, and selection
strategies to evolve a population of networks.

Objective: Replace backpropagation with an evolutionary algorithm to train the network.


Key Learning Points:
- Understanding optimisation methods beyond gradient descent
- Implementing evolutionary algorithms for weight optimisation
- Comparing GA-based training with backpropagation

Extensions & Challenges:
- Experiment with different mutation rates and selection strategies
- Use hybrid training: initialise weights with GA, then fine-tune with backpropagation
- Apply the genetic approach to hyperparameter tuning instead of weights


### Project 10: Adversarial Attacks on MNIST Classifiers

This project explores adversarial machine learning by slightly modifying MNIST images to trick
the model into misclassifying them. The goal is to understand model vulnerabilities and how to
defend against adversarial attacks.

Objective: Generate adversarial examples that fool the trained neural network.


Key Learning Points:
- Understanding adversarial machine learning and security risks
- Implementing gradient-based adversarial attacks (e.g., FGSM)
- Exploring defence strategies such as adversarial training

Extensions & Challenges:
- Implement iterative adversarial attacks for stronger perturbations
- Train a model that is more robust against adversarial examples
- Explore real-world implications of adversarial vulnerabilities in AI


### Project 11: Reinforcement Learning for Digit Recognition

Instead of standard supervised learning, this project explores using reinforcement learning
(RL) for classification. The agent receives rewards for correct predictions and updates its
policy accordingly.

Objective: Train a reinforcement learning (RL) agent to classify MNIST digits.


Key Learning Points:
- Understanding reinforcement learning in a classification setting
- Implementing policy-based updates instead of backpropagation
- Exploring reward shaping and exploration strategies

Extensions & Challenges:
- Compare different RL algorithms (Q-learning vs. policy gradients)
- Train an agent that actively selects which images to classify first
- Experiment with different reward structures for better learning

