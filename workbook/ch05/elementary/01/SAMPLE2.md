
## Sample no. 2

Variables:

Initially, all variables are declared with `var` and set to `0`.


__1. call multiply__

Procedure `multiply` calculates \( z = x $\times$ y \) using a bitwise algorithm.

Initial values:
- \( x = 3 \), \( y = 6 \)
- \( z = 0 \), \( a = 3 \), \( b = 6 \)

Iterations:
1. \( b = 6 \) (even): \( a = 6, b = 3, z = 0 \)
2. \( b = 3 \) (odd): \( z = z + a = 6, a = 12, b = 1 \)
3. \( b = 1 \) (odd): \( z = z + a = 18, a = 24, b = 0 \)

Final:
- \( z = 18 \) (i.e. \( 3 $\times$ 6 \))


__2. call divide__

Procedure `divide` calculates the quotient (\( q \)) and remainder (\( r \))
of \( x $\div$ y \) using an iterative approach.

Initial values:
- \( x = 3 \), \( y = 6 \)
- \( r = 3 \), \( q = 0 \), \( w = 6 \)

Iterations:
1. \( w $\leq$ r \): \( w = 12 \) (exit first loop).
2. \( w = 12 > y \): \( q = 0, w = 6 \).
3. \( w = 6 > r \): \( q = 0, w = 3 \) (no change to \( r \)).

Final:
- \( q = 0 \), \( r = 3 \)


__3. call gcd__

Procedure `gcd` calculates the greatest common divisor (\( z \)) of
\( x \) and \( y \) using the Euclidean algorithm.

Initial values:
- \( x = 3 \), \( y = 6 \)
- \( f = 3 \), \( g = 6 \)

Iterations:
1. \( f $\neq$ g \), \( f = 3 < g = 6 \): \( g = g - f = 3 \).
2. \( f = 3, g = 3 \) (exit loop).

Final:
- \( z = 3 \) (GCD of \( 3 \) and \( 6 \)).



__4. call fact__

Procedure `fact` calculates \( f = n! \) recursively.

Initial values:
- \( n = 10 \), \( f = 1 \)

Recursive calls:
1. \( n = 10 \): \( f = 10, n = 9 \)
2. \( n = 9 \): \( f = 90, n = 8 \)
3. \( n = 8 \): \( f = 720, n = 7 \)
4. \( n = 7 \): \( f = 5040, n = 6 \)
5. \( n = 6 \): \( f = 30240, n = 5 \)
6. \( n = 5 \): \( f = 151200, n = 4 \)
7. \( n = 4 \): \( f = 604800, n = 3 \)
8. \( n = 3 \): \( f = 1814400, n = 2 \)
9. \( n = 2 \): \( f = 3628800, n = 1 \)

Final:
- \( f = 3628800 \) (\( 10! \))



## Final Values

At the end of the program:
- \( x = 3 \), \( y = 6 \), \( z = 3 \) (from `gcd`)
- \( q = 0 \), \( r = 3 \) (from `divide`)
- \( n = 1 \) (from `fact`)
- \( f = 3628800 \) (\( 10! \))