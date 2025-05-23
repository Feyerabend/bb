
## Portfolio Analysis Example

Portfolio analysis is a key part of financial analysis—it helps assess how different assets (like stocks)
perform when combined. In this example, we track three stocks over five days and calculate their daily
returns, the overall portfolio return based on chosen weights, and statistical measures like average
return and volatility. One important metric we use is the *Sharpe ratio*, which tells us how much return
we get for each unit of risk taken. A higher Sharpe ratio means a better balance between reward and 
volatility, which is critical for making smart investment choices.

The script is written in a variant of the K language, a concise and array-focused language well suited
for financial computations. K's vectorised operations allow us to perform calculations like returns,
weighted sums, and variance without loops, making the code both fast and compact. This small example
illustrates how even simple data, when paired with the right tools, can reveal insights about portfolio
performance and guide optimisation strategies.

The script uses a price matrix (`transposed_prices`) for three stocks over five days:

```
Day 0: [100.0, 50.0, 75.0]
Day 1: [102.0, 51.0, 76.5]
Day 2: [101.5, 49.5, 74.0]
Day 3: [103.0, 52.0, 77.0]
Day 4: [104.5, 53.0, 78.5]
```
Each row represents daily closing prices for stocks A, B, and C.

#### 1. Daily Returns

For each day \( i \) (1 to 4), the script computes percentage returns:
- *Formula*: \( \text{returns}_i = \left( \frac{\text{prices}_i - \text{prices}_{i-1}}{\text{prices}_{i-1}} \right) \times 100 \)
- *K Code* (inferred):
  ```k
  day_i: transposed_prices@i
  day_prev: transposed_prices@(i-1)
  diff: day_i - day_prev
  returns: diff % day_prev
  ```
  - `@`: Indexes the price matrix.
  - `-`: Element-wise subtraction.
  - `%`: Dyadic percentage (divides `diff` by `day_prev`, scales by 100).

*Results*:
- Day 1: `[2.0, 2.0, 2.0]` (all stocks increase by 2%).
- Day 2: `[-0.49019607843137253, -2.941176470588235, -3.2679738562091507]` (negative returns).
- Day 3: `[1.477832512315271, 5.05050505050505, 4.054054054054054]` (positive returns).
- Day 4: `[1.4563106796116505, 1.9230769230769231, 1.948051948051948]` (positive returns).

The dyadic `%` operator (fixed in `k_simple_interpreter.py`) correctly computes `x%y` as `(x/y)*100`.


#### 2. Portfolio Returns

The script calculates daily portfolio returns using weights for each stock:
- *Formula*: \( \text{portfolio_return}_i = \sum (\text{weights} \times \text{returns}_i) \)
- *K Code* (inferred):
  ```k
  returns_at_i: returns@i
  weighted_returns: weights * returns_at_i
  portfolio_return: +/ weighted_returns
  ```
  - `*`: Element-wise multiplication.
  - `+/`: Sum (monadic `+` applied over the list).

*Initial Weights*: `[0.4, 0.3, 0.3]` (40% stock A, 30% stock B, 30% stock C).
- Day 1: `[0.4*2.0, 0.3*2.0, 0.3*2.0] = [0.8, 0.6, 0.6]`, Sum: `2.0`.
- Day 2: `[0.4*(-0.49019607843137253), 0.3*(-2.941176470588235), 0.3*(-3.2679738562091507)] = [-0.19607843137254902, -0.8823529411764705, -0.9803921568627452]`, Sum: `-2.0588235294117645`.
- Day 3: Sum: `3.3225007362938395`.
- Day 4: Sum: `1.7438629331833215`.

*Portfolio Returns*: `[2.0, -2.0588235294117645, 3.3225007362938395, 1.7438629331833215]`.

#### 3. Portfolio Metrics

- *Average Daily Return*:
  - *Formula*: \( \text{avg_return} = \frac{\sum \text{portfolio_return}_i}{n} \)
  - *K Code*: `avg_return: % portfolio_returns` (monadic `%` computes mean).
  - Result: `(2.0 + (-2.0588235294117645) + 3.3225007362938395 + 1.7438629331833215) / 4 = 1.251885035016349`.

- *Volatility* (standard deviation):
  - *Steps*:
    1. `mean_subtracted`: `portfolio_returns - avg_return`.
    2. `squared_diff`: `mean_subtracted * mean_subtracted`.
    3. `variance`: `% squared_diff` (mean of squared differences).
    4. Volatility: Square root of variance (not shown in K, likely computed in Python).
  - *K Code* (inferred):
    ```k
    mean_subtracted: portfolio_returns - avg_return
    squared_diff: mean_subtracted * mean_subtracted
    variance: % squared_diff
    ```
  - Result: Variance = `4.012489708517954`, Volatility = `sqrt(4.012489708517954) ≈ 2.003120`.

- *Sharpe Ratio*:
  - *Formula*: \( \text{Sharpe} = \frac{\text{avg_return}}{\text{volatility}} \)
  - Result: `1.251885035016349 / 2.003120 ≈ 0.624968`.

#### 4. Portfolio Optimisation

The script tests multiple weight combinations to maximize the Sharpe ratio. Each iteration:
- Uses new `weights` (e.g., `[0.5796471843520543, 0.6449336115087482, 0.7754192041391975]`).
- Recalculates portfolio returns and metrics.
- Tracks the combination with the highest Sharpe ratio.

*Optimised Portfolio*:
- *Best Weights*: `[0.617, 0.124, 0.26]` (61.7% stock A, 12.4% stock B, 26% stock C).
- *Portfolio Returns*: `[2.0, -1.5147831145839254, 2.5886559387564922, 1.641752623941319]`.
- *Metrics*:
  - Average Return: `1.1789063620284714`.
  - Volatility: `sqrt(2.532944572495304) ≈ 1.591523`.
  - Sharpe Ratio: `1.1789063620284714 / 1.591523 ≈ 0.740741`.

The optimised Sharpe ratio (`0.740741`) is higher than the initial (`0.624968`), indicating successful optimisation.

## Role of K Language
K's concise syntax and array operations are ideal for this analysis:
- *Vectorized Operations*: Computing `diff` and `returns` across all stocks simultaneously avoids loops.
- *Terse Syntax*: Operators like `@`, `%`, and `+/` reduce code complexity.
- *Dyadic `%`*: Critical for percentage returns, fixed in `k_simple_interpreter.py` to handle `x%y` as `(x/y)*100`.
- *Monadic `%`*: Simplifies averaging for `avg_return` and `variance`.

The debug output shows K expressions like `['transposed_prices', '@', 1]` and `[[2.0, 1.0, 1.5], '%', [100.0, 50.0, 75.0]]`, reflecting K's postfix notation and array focus.


## Potential Improvements
- *Input Data*: Day 1 returns are uniformly 2%, which is correct but may indicate
  simplified test data. Real market data could add realism.
- *Optimisation*: The script tests many weights, but the method (e.g., grid search)
  isn't clear. A more efficient algorithm (e.g., gradient-based) could be explored.
- *Variance*: Uses population variance (dividing by \( n \)). Sample variance (dividing
  by \( n-1 \)) might be better for small datasets (\( n=4 \)).
- *Weight Constraints*: Some weight sums slightly deviate from 1 (e.g., `1.001`).
  Enforce exact sums in optimisation.


### Conclusion

The portfolio analysis script leverages K's array-oriented power to compute stock returns,
portfolio metrics, and optimise weights. The calculations are accurate, and the optimisation
improves the Sharpe ratio. The K language's efficiency makes it well-suited for such financial
modeling tasks.

