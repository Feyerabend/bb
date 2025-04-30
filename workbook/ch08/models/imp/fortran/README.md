
### FORTRAN

FORTRAN, which stands for *FORmula TRANslation*, is one of the oldest high-level programming
languages, born in the 1950s at IBM under the leadership of John Backus. The team’s mission
was to create a language that allowed scientists and engineers to write mathematical computations
in a form close to their natural notation, freeing them from the tedious and error-prone task
of programming in assembly language.  

The first version, *FORTRAN I*, was released in 1957 for the IBM 704 computer. It was revolutionary
because its compiler could produce code nearly as efficient as hand-written assembly—a feat many
believed impossible at the time. This efficiency, combined with its intuitive syntax for mathematical
operations, made it an instant success in fields like physics, engineering, and applied mathematics.  

Early FORTRAN introduced foundational programming concepts like loops (using *DO* statements),
conditional branching (*IF*), and arrays. However, it had strict formatting rules—code had to be
written in specific columns, with statement labels in columns 1-5 and actual code between columns
7 and 72. Over time, the language evolved. *FORTRAN IV (1962)* improved reliability, and
*FORTRAN 66* became the first standardised version, ensuring portability across different machines.  

A major leap came with *FORTRAN 77*, which introduced structured programming features like
*IF…THEN…ELSE*, reducing reliance on *GOTO* statements. But the language truly modernized with
*FORTRAN 90*, which allowed free-format code (no more column restrictions), added modules,
recursion, dynamic memory allocation, and array operations. Later versions (*FORTRAN 95, 2003, 2008*)
introduced object-oriented programming, interoperability with C, and parallel computing features
like coarrays. The latest standard, *Fortran 2018*, further enhanced parallel computing and
integration with modern systems.  

FORTRAN has long dominated fields requiring heavy numerical computation, such as weather forecasting,
computational fluid dynamics, finite element analysis, and high-performance computing (HPC).
Many critical scientific libraries—like *LAPACK* and *BLAS*—are still written in FORTRAN, and
legacy codes in aerospace, seismology, and structural engineering remain in active use.  

Today, while newer languages like Python, C++, and Julia have gained popularity, FORTRAN persists
due to its unmatched optimization in numerical computing and the prohibitive cost of rewriting
decades-old scientific code. Modern compilers (such as *Intel Fortran* and *GNU Fortran*)
continue to optimise FORTRAN for cutting-edge hardware. Discussions around *Fortran 202X*
suggest further enhancements in safety and modern programming features.  

Though it may never regain mainstream status, FORTRAN's legacy is secure. It thrives in specialised
domains, often working behind the scenes—powering simulations, wrapped in Python libraries, or
running on supercomputers. As long as high-performance numerical computing remains essential,
FORTRAN will endure.  


### 1. FORTRAN 77: Simple Loop and Conditional

```fortran
      PROGRAM HELLO
      INTEGER I
      DO 10 I = 1, 5
          IF (I .EQ. 3) THEN
              PRINT *, 'Three!'
          ELSE
              PRINT *, 'Number: ', I
          END IF
10    CONTINUE
      END
```  

Explanation:
- Fixed-format (notice column restrictions—code starts at column 7).  
- `DO 10 I = 1, 5` defines a loop with a label (`10`) for the `CONTINUE` statement.  
- `IF (I .EQ. 3)` checks if `I` equals 3.  
- `PRINT *` outputs to the console.  



### 2. FORTRAN 90: Free-Format and Array Operations

```fortran
program array_ops
  implicit none
  integer, dimension(5) :: arr = [1, 2, 3, 4, 5]
  arr = arr * 2  ! Multiply all elements by 2
  print *, 'Doubled array:', arr
end program array_ops
```  

Explanation:
- Free-format (no column restrictions).  
- `implicit none` enforces variable declaration (good practice).  
- `arr = [1, 2, 3, 4, 5]` initializes an array.  
- `arr = arr * 2` performs element-wise operations (a modern feature).  



### 3. FORTRAN 95: Recursive Function (Factorial)

```fortran
recursive function factorial(n) result(res)
  integer, intent(in) :: n
  integer :: res
  if (n <= 1) then
    res = 1
  else
    res = n * factorial(n - 1)
  end if
end function

program test_factorial
  integer :: factorial
  print *, '5! = ', factorial(5)
end program
```  

Explanation:
- `recursive function` allows recursion (introduced in FORTRAN 90).  
- `result(res)` specifies the return variable.  
- `intent(in)` clarifies that `n` is input-only (safety feature).  



### 4. FORTRAN 2003: Interoperability with C

```fortran
module c_interop
  use, intrinsic :: iso_c_binding
  implicit none
contains
  subroutine fortran_sub(a) bind(c, name="fortran_sub")
    integer(c_int), intent(in) :: a
    print *, 'From Fortran:', a
  end subroutine
end module
```  

Explanation:
- `bind(c)` ensures compatibility with C.  
- `iso_c_binding` provides C-compatible types (e.g., `c_int`).  
- This subroutine can be called directly from C code.  



### 5. FORTRAN 2008: Parallel Computing with Coarrays

```fortran
program coarray_example
  implicit none
  integer :: me, total
  me = this_image()  ! Current process ID
  total = num_images()  ! Total parallel processes
  print *, 'I am image', me, 'of', total
end program
```  

Explanation:
- `this_image()` and `num_images()` are part of coarray features.  
- Enables parallel execution (e.g., running on multiple CPU cores).  
- Compile with `-fcoarray=` flag in GNU Fortran.  

