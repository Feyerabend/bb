
## Simple Neural Network with Hebbian and Delta Learning: `nn.py`

This repository contains a Python script (`nn.py`) demonstrating fundamental concepts
in neural networks, focusing on classic learning rules without external machine learning libraries.


### Key Concepts

This script illustrates the core components and two historical learning algorithms in neural networks:

  * *Neurons (Units) and Layers*: At its core, a neural network is composed of interconnected *neurons*,
  often called *units* or *nodes*. These units are typically organized into *layers*:

      * *Input Layer*: Receives the initial data.
      * *Hidden Layer(s)*: Intermediate layers that perform computations and learn complex patterns from the input data.
      * *Output Layer*: Produces the final result or prediction of the network.

  * *Connections and Weights*: Neurons in different layers are connected by *links* or *synapses*, each
  associated with a numerical value called a *weight*. Weights determine the strength and influence of
  one neuron's output on another. During learning, these weights are adjusted to improve the network's performance.

  * *Activation Functions*: An *activation function* determines the output of a neuron given its input.
  It introduces non-linearity into the network, enabling it to learn more complex relationships. `nn.py` demonstrates:

      * *Linear Activation*: The new activation is simply the total input.
      * *Binary (Step) Activation*: The new activation is 1 if the input is greater than a certain `threshold`, otherwise 0.

  * *Learning Rules*: Neural networks learn by adjusting their weights based on the data they process.
  This adjustment is governed by *learning rules*:

      * *Hebbian Learning*: One of the oldest and simplest learning rules, based on the principle "neurons that fire together, wire together". It suggests that if two neurons on either side of a synapse are activated simultaneously and repeatedly, the strength of that synapse should increase. In `nn.py`, this rule updates weights based on the product of the activations (outputs) of the connected units. The rule states: $\\Delta w\_{xy} = \\text{learning\_rate} \\cdot \\text{activation}\_x \\cdot \\text{activation}\_y$, where $x$ is the 'from' unit and $y$ is the 'to' unit.

      * *Delta Rule (Widrow-Hoff Rule)*: A supervised learning rule that adjusts weights to reduce the difference between the network's actual output and the desired (target) output. It is applied to weights leading into output units. The rule states: $\\Delta w\_{yx} = \\text{learning\_rate} \\cdot (d\_x - a\_x) \\cdot a\_y$, where $d\_x$ is the desired output for unit $x$ (an output unit), $a\_x$ is the actual output of unit $x$, and $a\_y$ is the output of unit $y$ (an input to unit $x$).


### Content: `nn.py`

The `nn.py` script provides a foundational understanding of neural network mechanics.

  * *`Unit` Class*: Represents a single neuron with properties like `id`, `activation`, `output`, and boolean flags for its type (`is_input`, `is_output`, `is_hidden`).
  * *`NeuralNetwork` Class*: Manages the network's overall structure, including its `units`, `weights` (stored as `{(from_unit_id, to_unit_id): weight_value}`), and categorized unit IDs.
      * `add_unit()`: Adds a new unit to the network.
      * `add_connection()`: Adds a weighted connection between two units, initializing with a random weight if not provided.
      * `set_input()`: Sets the activation levels for the input units.
      * `_get_incoming_connections()`: A helper method to retrieve connections leading into a specific unit.
      * `_calculate_total_input()`: Calculates the sum of weighted inputs for a given unit.
      * `activate()`: Activates all non-input units using either a "linear" or "binary" activation function. It assumes a feedforward processing order (hidden units before output units).
      * `get_output_pattern()`: Retrieves the activation levels of all output units.
      * `train_hebbian()`: Applies the Hebbian learning rule to all connections.
      * `train_delta()`: Applies the Delta learning rule to weights leading into output units, based on target outputs.
  * *Example Usage (`if __name__ == "__main__":`)*: The script includes a practical demonstration:
      * Training a simple AND gate using *Binary Activation* and the *Delta Rule* over multiple epochs, showing the evolution of weights and predictions.
      * A conceptual demonstration of *Hebbian Learning* with different input/output scenarios to illustrate how weights are adjusted.

The script will print the network's initial and final weights, training progress, and test results for the AND gate, along with demonstrations of Hebbian learning scenarios.



## Interactive Neural Network Visualisation: `nn.html`

This repository contains an interactive web application (`nn.html`) that visualises a neural network and demonstrates
the backpropagation algorithm with gradient descent for training.


### Key Concepts

This HTML file provides a hands-on experience with fundamental neural network concepts:

  * *Neural Network Architecture*: The application simulates a network with one input layer (2 nodes), one hidden layer (adjustable number of nodes), and one output layer (1 node).
  * *Neurons and Layers*: Individual nodes represent neurons, organized into input, hidden, and output layers.
  * *Connections and Weights*: Lines between nodes represent weighted connections. The thickness of the line shows the strength of the weight, and its color indicates whether the weight is positive (green) or negative (red).
  * *Activation Functions*: The network uses *sigmoid activation functions*. The sigmoid function squashes its input into a range between 0 and 1, allowing for continuous values suitable for gradient-based optimization.
  * *Training and Learning Algorithms*:
      * *Backpropagation*: The primary learning algorithm used. It's a method for efficiently calculating the gradient of the loss function with respect to the network's weights. The error is propagated backward from the output layer through the hidden layers, guiding weight adjustments.
      * *Gradient Descent*: An optimization algorithm that iteratively adjusts the network's weights and biases to minimize the prediction errors. It moves the weights in the direction that reduces the loss.
  * *Loss Function (Mean Squared Error)*: The network uses Mean Squared Error (MSE) to quantify the difference between its predictions and the actual target values. The goal of training is to minimize this loss.
  * *Floating-Point Inputs and Binary Logic*:
      * The network processes *floating-point inputs* (e.g., 0.0, 1.0, or 0.3).
      * For binary logic gate datasets (like XOR, AND, OR), the training data uses binary inputs (0 or 1) and targets (0 or 1).
      * The network's floating-point output (e.g., 0.73) is interpreted as binary by *thresholding*: outputs greater than 0.5 are treated as 1, and outputs less than or equal to 0.5 are treated as 0. This allows the continuous outputs of the sigmoid function to be used for binary classification tasks.


### Content: `nn.html`

The `nn.html` file contains all the necessary HTML, CSS, and JavaScript to run the interactive demo in a web browser.

  * *HTML Structure*: Sets up the layout for the network visualization, loss chart, controls, and statistics.
  * *CSS Styling*: Provides basic styling for a clean and user-friendly interface.
  * *JavaScript (`<script>`)*: Contains the neural network implementation and interactive logic:
      * *`NeuralNetwork` Class*: Implements the multi-layer perceptron (MLP) structure with methods for:
          * `constructor()`: Initializes weights and biases randomly.
          * `sigmoid()`: The activation function.
          * `dsigmoid()`: The derivative of the sigmoid function, used in backpropagation.
          * `predict()`: Performs the forward pass to generate outputs for given inputs.
          * `train()`: Implements the backpropagation algorithm to update weights and biases based on input and target values. It calculates `outputErrors`, `hiddenErrors`, and adjusts `weightsHO` (hidden-to-output) and `weightsIH` (input-to-hidden).
      * *Global Variables*: Manages the network instance, training data, training state, epoch count, loss history, and accuracy statistics.
      * *`DATASETS` Constant*: Stores pre-defined training data for XOR, AND, and OR logic gates.
      * *UI Functions*: Functions for `init()`, `updateSliderValues()`, `loadPresetData()`, `resetNetwork()`, `toggleTraining()`, `startTraining()`, `stopTraining()`, `trainOneEpoch()`, `predict()`, `testAllData()`, `updateDisplay()`, `drawNetwork()` (visualizing nodes and weighted connections), `drawLossChart()` (plotting training loss), `showTab()`, and `updateStatus()`.
  * *Interactive Elements*: Sliders for `Learning Rate` and `Hidden Neurons`, buttons for `Start Training`, `Reset Network`, `Train One Epoch`, and input fields for `Test Input`. Tabs allow switching between Training, Testing, and Data selection.

This interactive demo provides a clear visual and practical understanding of how a simple neural network
learns using backpropagation and gradient descent.

