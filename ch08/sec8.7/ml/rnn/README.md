
## Recurrent Neural Network (RNN)

Machine learning empowers systems to learn from data and improve performance over
time without explicit programming, and a specialised type of neural network, the
*Recurrent Neural Network* (RNN), is particularly adept at handling sequential data,
making it a cornerstone for tasks like natural language processing and time series
analysis.

*Recurrent Neural Networks* (RNNs) are a foundational class of artificial neural
networks specifically designed to model and recognise patterns in sequential data.
Typical applications include natural language processing (NLP), speech recognition,
and time series forecasting--domains where the order and context of inputs play
a crucial role.

Unlike traditional feedforward neural networks, which process inputs in isolation,
RNNs incorporate feedback connections that form directed cycles within the network.
This architectural feature allows RNNs to maintain a dynamic hidden state, a form
of internal memory that captures information about previous elements in the
sequence. As a result, RNNs can, at least in principle, learn temporal dependencies
and carry forward relevant context from one step to the next.

This temporal aspect makes RNNs particularly well-suited for tasks such as language
modeling, where the probability of a word appearing in a sentence depends on the
words that precede it. For example, given the phrase "The cat sat on the", a
well-trained RNN can leverage its memory to predict that the next word is likely
to be "mat".

However, traditional RNNs face significant challenges, including difficulty in
learning long-range dependencies due to issues like vanishing and exploding gradients
during training. These limitations led to the development of more advanced architectures
such as *Long Short-Term Memory* (LSTM) networks and Gated Recurrent Units (GRUs),
which introduce gating mechanisms to better manage information flow and maintain
relevant context over longer sequences.

In recent years, the landscape of sequence modeling has been transformed by the
emergence of transformer-based architectures, most notably *Large Language Models* (LLMs)
such as GPT. These models abandon recurrence entirely in favor of attention mechanisms,
which allow them to capture dependencies over arbitrary distances without the need
for sequential processing. As a result, LLMs have largely supplanted RNNs in many
high-profile NLP tasks, offering greater scalability, parallelisability, and performance.

Nonetheless, RNNs remain a conceptually important and historically significant approach
to sequence learning, and they continue to be useful in certain settings--particularly
when computational simplicity, online processing, or real-time constraints are factors.


### Practical Examples

The provided `rnn_sample.py` and `shakespeare_naive.py` code offers a foundational
implementation of a Simple Recurrent Neural Network. The `SimpleRNN` class in
`rnn_sample.py` establishes the core components of an RNN, including the initialisation
of weights and biases, the use of `tanh` as an activation function for the hidden layer,
and `softmax` for the output layer to produce probability distributions over the
vocabulary. It also details the forward pass, where inputs are processed sequentially
and hidden states are updated, and the backward pass, which involves backpropagation
through time to calculate and apply gradients for weight updates, thereby enabling
the network to learn from its errors. The `shakespeare_naive.py` expands on this by
adding gradient clipping to prevent exploding gradients, a common issue in RNN training,
and introduces a `ShakespeareDataLoader` to manage text files, allowing for training
on larger datasets of Shakespearean works. This implementation demonstrates the
fundamental principles of RNNs, specifically for character-level language modeling,
where the network learns to predict the next character in a sequence based on the
preceding ones.


### Optimisation

Expanding on the foundational RNN implementation, `shakespeare_opt.py` introduces
significant optimisations for training stability and efficiency. It incorporates
RMSprop, an adaptive learning rate optimisation algorithm, which adjusts the learning
rate for each weight individually, leading to faster convergence and better performance
compared to vanilla stochastic gradient descent. Furthermore, it employs a decay
rate for the learning rate, gradually reducing it over epochs to fine-tune the model's
weights and prevent overshooting the optimal solution. The inclusion of a smooth loss
calculation helps to provide a more stable and readable indication of training progress
by averaging the loss over recent iterations. The `shakespeare_gpu.py` code further
enhances performance by integrating hardware GPU acceleration through the `cupy` library,
replacing standard Python lists and `math` operations with `cupy.ndarray` and
`cupy.cuda.Device` for matrix operations and computations. This leverages the parallel
processing capabilities of GPUs, drastically speeding up both the forward and backward
passes. Memory management is also addressed by explicitly clearing GPU memory at the
end of training steps. Finally, `shakespeare_tensor.py` brings a more robust and flexible
matrix and vector computation by introducing a custom `Tensor` class. This class overloads
arithmetic operators, enabling more intuitive and readable matrix manipulations. It also
incorporates an `AdamOptimizer` for weight updates, a more advanced adaptive learning
rate optimisation algorithm that combines the benefits of RMSprop and Adagrad, often
leading to even faster and more stable training. These advancements collectively demonstrate
a progression from a basic RNN implementation to more sophisticated and performant models
through optimization techniques, GPU acceleration, and improved numerical computation
structures.


### LSTM

Building upon the previously discussed RNN implementations, `shakespeare_lstm.py` introduces
a significant architectural advancement with the integration of Long Short-Term Memory
(LSTM) cells. Unlike the simpler recurrent units, LSTMs are specifically designed to address
the vanishing and exploding gradient problems that can hinder the training of traditional
RNNs on long sequences. This is achieved through a sophisticated internal structure comprising
a cell state and three distinct gates: the input gate, the forget gate, and the output gate.
The forget gate controls which information from the previous cell state should be discarded,
while the input gate determines what new information will be stored in the current cell state.
Finally, the output gate regulates what part of the cell state is outputted as the hidden
state. The `LSTM` class in `shakespeare_lstm.py` implements the forward and backward passes
for these gates and the cell state, showcasing a more complex but powerful mechanism for
learning long-range dependencies in sequential data. This makes the LSTM particularly
well-suited for tasks like Shakespearean text generation, where understanding distant contextual
relationships is crucial for producing coherent and stylistically accurate prose. The training
process remains similar to the optimized RNNs, but the internal workings of the LSTM cell
allow for more effective information flow and retention over extended sequences, leading
to potentially better performance on challenging language modeling tasks.


### GRU

Further extending the capabilities of the recurrent neural networks, `shakespeare_gru.py`
introduces the *Gated Recurrent Unit* (GRU) as an alternative to the LSTM. The GRU, while
also designed to mitigate vanishing gradients and capture long-range dependencies, offers
a simpler architecture compared to the LSTM by combining the forget and input gates into
a single "update gate" and merging the cell state with the hidden state. This reduction in
complexity often translates to fewer parameters and faster training times, while still
maintaining competitive performance for many sequence-to-sequence tasks. The `GRU` class
within `shakespeare_gru.py` implements the forward and backward passes for its update and
reset gates, showcasing how this streamlined gating mechanism effectively controls the
flow of information and memory within the network. Like the LSTM, the GRU's ability to
selectively update and reset its hidden state allows it to learn from and generate coherent
sequences, making it another powerful tool for character-level language modeling on
datasets like Shakespeare's works.


### Gradient Challlenges

The vanishing gradient problem arises during the training of neural networks when
gradients--the values used to update model weights during backpropagation--become extremely
small as they are propagated backward through many layers or time steps. This is particularly
problematic in deep networks and recurrent neural networks (RNNs), especially when trying
to learn long-term dependencies in sequences.

When you train a network using backpropagation, each weight is updated in proportion to
the gradient of a loss function with respect to that weight. For traditional RNNs, the
repeated application of the chain rule across many time steps leads to the multiplication
of many Jacobian matrices. If these matrices contain values less than one in magnitude
(which is common when using activation functions like the sigmoid or tanh), the gradients
can shrink exponentially as they propagate backward through time. Eventually, they
become so small that further weight updates are effectively negligible. As a result,
the earlier layers (or time steps) learn extremely slowly, if at all. This is known as
the vanishing gradient problem. It means that the network "forgets" what it saw earlier
in the sequence, making it difficult or impossible to learn long-term dependencies.

On the other hand, exploding gradients occur when those Jacobian matrix values are
greater than one, leading to gradients that grow exponentially and result in unstable
updates. This is often addressed with gradient clipping.

LSTMs (Long Short-Term Memory networks) are designed to counteract the vanishing gradient
problem by introducing a more sophisticated memory mechanism. They include a memory cell
and gating mechanisms--input, output, and forget gates--which allow the network to
control the flow of information explicitly. The key insight is that the memory cell
uses additive rather than multiplicative updates, which helps preserve the gradient
across many time steps. This structure allows LSTMs to maintain and propagate error
signals for much longer, effectively remembering information over longer sequences
and learning long-range dependencies that standard RNNs cannot.

In short, the vanishing gradient problem is a fundamental limitation of standard RNNs
that prevents them from learning long-term patterns. LSTMs solve this by design,
enabling effective learning even in sequences with distant relevant information.

