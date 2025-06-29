
*A very simplified way to illustrate the early evolution of neural networks can be seen through
the problem of solving XOR. The problem is that the XOR (exclusive OR) logical function is *not*
linearly separable. This means you cannot draw a single straight line on a graph to separate
the inputs that produce a "true" (or 1) output from those that produce a "false" (or 0) output.*

*For example, in the `minsky_papert.html` file, it's explicitly shown that for inputs (0,0) and
(1,1) the XOR output is 0, while for (0,1) and (1,0) the output is 1.
A single line cannot separate these two groups.*

*Files referred to below:*
- [minsky_papert.html](./minsky_papert.html)
- [lindstrom.html](./lindstrom.html)
- [backprop.html](./backprop.html)


## The XOR Problem

The evolution of neural networks from the simple perceptron to the more sophisticated backpropagation
algorithm marks a significant journey in artificial intelligence, addressing fundamental limitations
and expanding the capabilities of machine learning.

The story begins with the *Perceptron*, introduced by Frank Rosenblatt in 1957. As demonstrated in the
`minsky_papert.html` file, a simple perceptron is a single-layer neural network designed to classify
linearly separable data. It operates by taking multiple inputs, assigning weights to them, summing
them up with a bias, and then passing the result through a step function to produce a binary output.
The learning rule adjusts weights and bias based on the difference between the target output and the
actual output. This early model showed promise in its ability to learn and classify patterns.

However, a major setback arrived in 1969 with Marvin Minsky and Seymour Papert's book "Perceptrons,"
which, as highlighted in the `minsky_papert.html` file, critically analysed the limitations of this
model. Their most famous argument centered on the XOR problem, a non-linearly separable function.
The `minsky_papert.html` file explicitly states that "no single line can separate (0,1) and (1,0)
from (0,0) and (1,1)," meaning a single perceptron cannot solve XOR. This, among others, fundamental
limitation led to a period known as the "AI Winter" in the 1970s, as research funding and interest
in neural networks waned.

Despite this period of reduced interest, research continued, leading to advancements in understanding
multi-layer networks. The `lindstrom.html` file represents an early attempt at tackling the XOR problem
with a "Classical Connectionist Network" from Sten Lindström's 1992 AI Course, using the *Delta Rule*.
This model introduces a hidden layer, which is crucial for solving non-linearly separable problems
like XOR. Unlike the perceptron's step function, this network uses a sigmoid activation function, and
its learning is based on the Delta Rule, which aims to minimize the error function $Error = ½ Σ(d_x - a_x)^2$.
The weight update rule, $Δw_{yx} = learning\_rate × (d_x - a_x) × a_y$, allows for more nuanced
adjustments to the weights based on the difference between desired and actual output, propagated
through the network. This approach, while still in development, laid the groundwork for more
effective multi-layer learning.

The breakthrough that truly revitalised the field and allowed neural networks to solve complex problems
like XOR was the re-popularization of *Backpropagation* in 1986 by Rumelhart, Hinton, and Williams.
The `backprop.html` file illustrates this "Improved Backpropagation Learning" from a 1992 perspective.
Backpropagation is a supervised learning algorithm that efficiently computes the gradient of the loss
function with respect to the weights of the network. It works by first performing a forward pass to
calculate the output and the error. Then, the error is propagated backward through the network,
layer by layer, adjusting the weights and biases based on their contribution to the error. The `backprop.html`
file details the error function, the sigmoid activation function and its derivative (essential for gradient
calculation), and separate weight update rules for the output and hidden layers. This ability to train
multi-layer networks effectively with backpropagation finally overcame the limitations of the single-layer
perceptron and paved the way for the deep learning revolution we see today.

