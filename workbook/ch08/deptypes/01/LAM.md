## Lambda Calculus Simulator

### Basic Numeric Tests

These tests verify the basic Church numeral operations:

```python
one = church(1)
two = church(2)
three = evaluate(App(succ, two))

print("Church numeral 2:", to_int(two))
print("Successor of 2:", to_int(three))

five = evaluate(App(App(add, two), three))
print("2 + 3 =", to_int(five))
```

- *Church numeral representation*: Verifies that Church numerals correctly encode integers
- *Successor operation*: Tests that `succ` correctly increments a Church numeral
- *Addition operation*: Tests that `add` correctly computes the sum of two Church numerals


### Pairs Tests

These tests verify the Church-encoded pair operations:

```python
p = evaluate(App(App(pair, two), three))
first = evaluate(App(fst, p))
second = evaluate(App(snd, p))

print("First of pair (2,3):", to_int(first))
print("Second of pair (2,3):", to_int(second))
```

- *Pair creation*: Creates a pair containing the Church numerals for 2 and 3
- *First projection*: Tests that `fst` correctly extracts the first element (2)
- *Second projection*: Tests that `snd` correctly extracts the second element (3)


### Boolean Logic Tests

These tests verify the Church-encoded boolean operations:

```python
print("true:", to_bool(true))
print("false:", to_bool(false))

not_true = evaluate(App(not_op, true))
print("not true:", to_bool(not_true))

and_true_false = evaluate(App(App(and_op, true), false))
print("true and false:", to_bool(and_true_false))

or_true_false = evaluate(App(App(or_op, true), false))
print("true or false:", to_bool(or_true_false))
```

- *Boolean representation*: Verifies that Church booleans correctly encode truth values
- *Negation*: Tests that `not_op` correctly negates a boolean value
- *Conjunction*: Tests that `and_op` correctly implements logical AND
- *Disjunction*: Tests that `or_op` correctly implements logical OR


### Conditional Test

This test verifies that the conditional operation works correctly:

```python
cond_test = evaluate(App(App(App(cond, true), church(1)), church(2)))
print("if true then 1 else 2:", to_int(cond_test))
```

- *Conditional operation*: Tests that `cond` selects the correct branch based on a boolean predicate
- In this case, when the condition is `true`, it should return the first branch (1)


### Number Operation Tests

These tests verify additional operations on Church numerals:

```python
is_zero_test = evaluate(App(iszero, church(0)))
print("is_zero(0):", to_bool(is_zero_test))

is_zero_test = evaluate(App(iszero, church(1)))
print("is_zero(1):", to_bool(is_zero_test))

pred_test = evaluate(App(pred, church(5)))
print("pred(5):", to_int(pred_test))

mult_test = evaluate(App(App(mult, church(3)), church(4)))
print("3 * 4 =", to_int(mult_test))
```

- *Zero test*: Tests that `iszero` correctly identifies zero and non-zero values
- *Predecessor*: Tests that `pred` correctly computes n-1 for a Church numeral
- *Multiplication*: Tests that `mult` correctly computes the product of two Church numerals


### Y Combinator Test: Factorial Implementation

This is the main test showcasing the power of the Y combinator to implement recursion:

```python
# The factorial function
# fact = λn. if (iszero n) 1 (mult n (fact (pred n)))
# Using Y combinator: Y (λf.λn. if (iszero n) 1 (mult n (f (pred n))))

fact_body = Abs('f', Abs('n', 
    App(App(App(cond, App(iszero, Var('n'))),
        church(1)),  # then branch: return 1
        App(App(mult, Var('n')),  # else branch: n * f(pred n)
            App(Var('f'), App(pred, Var('n'))))
    )
))

# Create factorial function using Y combinator
fact = App(Y, fact_body)

# Calculate factorial of 0, 1, 2, 3, 4
for i in range(5):
    result = evaluate(App(fact, church(i)), max_steps=10000)
    print(f"factorial({i}) =", to_int(result))
```


#### Understanding the Y Combinator Test

1. *Factorial Function Structure*:
   - The factorial function is defined recursively as:
     - `fact(0) = 1`
     - `fact(n) = n * fact(n-1)` for n > 0
   - In lambda calculus, this would be written as:
     - `fact = λn. if (iszero n) 1 (mult n (fact (pred n)))`

2. *Problem with Recursion in Lambda Calculus*:
   - Lambda calculus doesn't directly support recursive definitions
   - We can't use `fact` in its own definition

3. *Y Combinator Solution*:
   - The Y combinator allows for recursion without explicitly naming the function
   - It takes a function that expects itself as an argument and returns a recursive version
   - `Y = λf.(λx.f (x x)) (λx.f (x x))`

4. *Factorial Implementation Steps*:
   - Define a function body that takes a function `f` and a number `n`:
     - `λf.λn. if (iszero n) 1 (mult n (f (pred n)))`
   - Here, `f` represents the factorial function itself
   - Apply the Y combinator to this function body to create a recursive factorial function

5. *Execution Process*:
   - When calculating `factorial(3)`:
     - Check if 3 is zero (it's not)
     - Calculate 3 * factorial(2)
     - This recursively evaluates factorial(2), factorial(1), factorial(0)
     - When reaching factorial(0), returns 1
     - The recursion unwinds: factorial(1) = 1*1 = 1, factorial(2) = 2*1 = 2, factorial(3) = 3*2 = 6

#### Why/How the Y Combinator Works

The Y combinator satisfies the fixed-point equation: `Y g = g (Y g)` for any function `g`.

This means when we apply Y to our factorial function body (`fact_body`), we get:
```
Y fact_body = fact_body (Y fact_body)
```

This effectively substitutes `Y fact_body` for the recursive calls (`f`), creating the desired
recursion effect without explicitly naming the function.

### Results

The tests calculate and display the factorial values for 0 through 4:
- factorial(0) = 1
- factorial(1) = 1
- factorial(2) = 2
- factorial(3) = 6
- factorial(4) = 24

This confirms that the Y combinator successfully enables recursion in the lambda calculus, allowing
us to implement the factorial function that correctly computes the expected values.
