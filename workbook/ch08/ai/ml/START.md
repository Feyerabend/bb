
## Introduction to ML from a Conventional Programming Standpoint

As a conventional programmer, you're used to writing explicit instructions for the computer to follow.
You define the rules, and the computer executes them to produce an output. For example, if you want
to write a program that classifies an email as "spam" or "not spam," you might write a series of `if/else`
statements:

```python
def classify_email_conventional(email_text):
    if "nigerian prince" in email_text.lower() and "urgent" in email_text.lower():
        return "spam"
    elif "free lottery" in email_text.lower() or "click here" in email_text.lower():
        return "spam"
    else:
        return "not spam"
```

This approach works well when the rules are clear, finite, and easily expressible. But what happens when
the rules are too complex, too numerous, or constantly changing? What if you can't even articulate the
rules yourself? This is where Machine Learning steps in.


#### Learning from Data

Instead of explicitly programming the rules, in Machine Learning, you provide the computer with *data*
and *examples of the desired output for that data*. The machine then *learns* the rules or patterns
from these examples.

Think of it like this:

* *Conventional Programming:* You provide the *rules* and the *data*, and the computer gives you the *answers*.
    * `Rules + Data -> Answers`
* *Machine Learning:* You provide the *data* and the *answers*, and the computer learns the *rules*.
    * `Data + Answers -> Rules (or a "model")`

Let's revisit our spam example. Instead of `if/else` statements, you would feed an ML algorithm thousands of
emails, each labeled as "spam" or "not spam." The algorithm would then analyze these examples and discover
patterns that differentiate spam from legitimate emails. These learned patterns form what we call a "model."
Once trained, this model can then predict whether a *new, unseen* email is spam or not.


#### Functions and Parameters

From a programmer's perspective, you can think of an ML model as a highly complex function that has learned
its internal parameters by observing data.

In conventional programming, you might write a function like:

```python
def calculate_area(length, width):
    return length * width
```

Here, `length` and `width` are inputs, and `area` is the output. The rule (`length * width`) is hardcoded.

In ML, you're looking for a function, let's call it $f$, such that given some input $X$, it produces an output $Y$.
$Y = f(X)$

The trick is that we don't explicitly define $f$. Instead, $f$ is implicitly defined by a set of *parameters* that
the ML algorithm learns. The goal of the learning process is to find the best possible values for these parameters
so that the function $f$ accurately maps inputs to outputs based on the training data.


#### The Language of Patterns

While ML can seem magical, it's firmly rooted in mathematics. You don't need to be a math genius, but understanding
some core areas will demystify the process.

1.  *Linear Algebra:*
    * *Concept:* Think of data as numbers organized in arrays or matrices. For example, an email might be represented
      as a list of numbers indicating the frequency of certain words. Linear algebra provides the tools to manipulate
      these collections of numbers efficiently.
    * *Why it's used:* Operations like multiplying matrices, finding vectors, and transformations are fundamental to
      how ML algorithms process and learn from data. Many ML models are essentially sophisticated linear equations.
    * *Programmer's view:* If you've ever used libraries for numerical computation like NumPy, you're already interacting
      with linear algebra concepts. Operations like dot products or matrix transpositions are common in ML code.

2.  *Calculus (especially Derivatives):*
    * *Concept:* Calculus is about change. In ML, we often want to find the "best" set of parameters for our model. How
      do we know if a set of parameters is "better" than another? We define a "cost" or "loss" function that tells us
      how far off our model's predictions are from the actual answers. The goal is to minimise this cost.
    * *Why it's used:* Derivatives help us find the direction and magnitude of change. By calculating the derivative
      of our cost function with respect to each parameter, we can determine how to adjust those parameters to reduce
      the cost. This process is called *gradient descent*, which is like walking downhill in the steepest direction
      until you reach the lowest point (minimum cost).
    * *Programmer's view:* You won't typically write derivative calculations directly, but you'll use optimisation
      algorithms (like `SGD` for Stochastic Gradient Descent) that implement these concepts under the hood to update
      model parameters.

3.  *Probability and Statistics:*
    * *Concept:* ML is often about making predictions under uncertainty. Probability helps us quantify this uncertainty,
      and statistics helps us understand the properties of our data and the likelihood of events.
    * *Why it's used:*
        * *Modeling Uncertainty:* Some ML models (like Naive Bayes for text classification) are explicitly built on
          probabilistic principles.
        * *Evaluating Models:* How good is our model? Statistical measures like accuracy, precision, and recall help
          us assess its performance and understand if its predictions are statistically significant.
        * *Data Understanding:* Statistics helps us understand the distribution of our data, identify outliers, and
          see relationships between different features.
    * *Programmer's view:* When you split your data into training and testing sets, or evaluate your model's performance
      metrics, you're applying statistical concepts.


#### Grasping ML Concepts

The key to understanding ML is to see the interplay between the mathematical theory and its practical implementation in code.

*1. The "Model" as a Parametrised Function:*

Let's consider a very simple ML model: *Linear Regression*. Our goal is to predict a numerical value (e.g., house price) based
on another numerical value (e.g., house size).

Mathematically, we are trying to find a linear relationship:
$y = mx + b$

Here, $y$ is the predicted house price, $x$ is the house size. Our "parameters" are $m$ (slope) and $b$ (y-intercept).

*Code Perspective:*

In conventional programming, you'd know $m$ and $b$ and calculate $y$. In ML, we have a dataset of (house size, actual price)
pairs. The ML algorithm will *learn* the best $m$ and $b$ values that best fit this data.

```python
# Conceptual Python code for a simple linear model (before training)
def predict_price(house_size, m, b):
    return m * house_size + b

# Initially, m and b are random or set to 0.
# The ML process will adjust m and b to minimize errors.
```

*2. The "Loss Function": Quantifying Error*

How do we know if our chosen $m$ and $b$ are good? We define a *loss function* (also called a cost function). A common one
for linear regression is *Mean Squared Error (MSE)*.

For each data point, we calculate the difference between our predicted $y$ and the actual $y$ (the error), square it (to
make it positive and penalize larger errors more), and then average these squared errors across all data points.

Mathematically:
$MSE = \frac{1}{N} \sum_{i=1}^{N} (y_i - (mx_i + b))^2$

Here, $N$ is the number of data points, $y_i$ is the actual price for the $i$-th house, and $(mx_i + b)$ is our model's
predicted price.

*Code Perspective:*

```python
import numpy as np

def mean_squared_error(actual_prices, predicted_prices):
    return np.mean((actual_prices - predicted_prices)*2)

# During training, the ML algorithm will try different m and b values
# and calculate the MSE, aiming to make it as small as possible.
```

*3. "Optimisation": Finding the Best Parameters (Gradient Descent)*

This is where calculus (specifically derivatives) comes into play. We want to find the $m$ and $b$ that minimise the MSE.
Imagine the MSE as a landscape, and $m$ and $b$ are our coordinates. We want to find the lowest point in this landscape.

Gradient Descent iteratively adjusts $m$ and $b$ in the direction that reduces the MSE. It's like taking small steps downhill.
The size of each step is determined by the "learning rate," a crucial hyperparameter.

*Code Perspective (Conceptual, not full implementation):*

You typically don't implement gradient descent from scratch in production. Libraries like scikit-learn or TensorFlow/PyTorch
handle this. But conceptually:

```python
# Conceptual loop for training (simplified)
learning_rate = 0.01
num_iterations = 1000

m = 0.0 # Initial guess
b = 0.0 # Initial guess

for _ in range(num_iterations):
    # 1. Calculate predictions with current m and b
    predictions = m * house_sizes + b

    # 2. Calculate the "gradient" (how much to adjust m and b to reduce error)
    # This involves derivatives of the MSE with respect to m and b
    # (Simplified: Imagine these are calculated for you)
    gradient_m = ...
    gradient_b = ...

    # 3. Update m and b
    m = m - learning_rate * gradient_m
    b = b - learning_rate * gradient_b

    # 4. (Optional) Check current MSE
    current_mse = mean_squared_error(actual_prices, predictions)
    # print(f"Iteration {_}: MSE = {current_mse}")

# After training, m and b will be the learned parameters for your model.
```

#### Transitioning Your Mindset

The biggest shift from conventional programming to ML is moving from *explicit rules* to *data-driven discovery of rules*.

* *You don't tell the machine *how* to classify spam; you show it *what* spam looks like.*
* *You don't program the formula for recognizing faces; you provide many examples of faces and non-faces.*

This paradigm shift opens up possibilities for solving problems that are intractable with traditional programming, especially
those involving complex patterns in large datasets. While the math provides the theoretical backbone, the code is how you put
these concepts into action, often leveraging powerful libraries that abstract away the low-level mathematical operations.

Start with simple models like linear regression and logistic regression. Understand their mathematical formulation, the loss
functions used, and how optimization algorithms like gradient descent work to find the best parameters. Once you grasp these
fundamental building blocks, you'll have a solid foundation for exploring the exciting world of machine learning.


