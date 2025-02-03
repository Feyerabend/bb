
## Intermediate Code: LLVM



__Build__

```shell
make clean
make samples
```

From the richness of the *Abstract Syntax Tree* (AST) we can build our code. This time it
will be intermediate into *Three Address Code* (TAC), one step closer to the ultimate goal of
more executable code.

__View__

..

### Overview and Uses


```llvm

```



```llvm
; Function: computeGCD
define void @computeGCD() {
L0:
    ; t0 = LOAD b.g
    %t0 = load i32, i32* @b_g
    ; t1 = LOAD 0
    %t1 = load i32, i32* @zero
    ; t2 = != t0 t1
    %t2 = icmp ne i32 %t0, %t1
    ; IF_NOT t2 GOTO L1
    br i1 %t2, label %L2, label %L1

L1:
    ; t15 = LOAD a.g
    %t15 = load i32, i32* @a_g
    ; gcd.g = t15
    store i32 %t15, i32* @gcd_g
    ret void

L2:
    ; t3 = LOAD a.g
    %t3 = load i32, i32* @a_g
    ; t4 = LOAD b.g
    %t4 = load i32, i32* @b_g
    ; t5 = > t3 t4
    %t5 = icmp sgt i32 %t3, %t4
    ; IF_NOT t5 GOTO L3
    br i1 %t5, label %L4, label %L5

L3:
    ; t6 = LOAD a.g
    %t6 = load i32, i32* @a_g
    ; t7 = LOAD b.g
    %t7 = load i32, i32* @b_g
    ; t8 = - t6 t7
    %t8 = sub i32 %t6, %t7
    ; a.g = t8
    store i32 %t8, i32* @a_g
    br label %L0

L4:
    ; t9 = LOAD a.g
    %t9 = load i32, i32* @a_g
    ; t10 = LOAD b.g
    %t10 = load i32, i32* @b_g
    ; t11 = <= t9 t10
    %t11 = icmp sle i32 %t9, %t10
    ; IF_NOT t11 GOTO L5
    br i1 %t11, label %L6, label %L3

L5:
    ; t12 = LOAD b.g
    %t12 = load i32, i32* @b_g
    ; t13 = LOAD a.g
    %t13 = load i32, i32* @a_g
    ; t14 = - t12 t13
    %t14 = sub i32 %t12, %t13
    ; b.g = t14
    store i32 %t14, i32* @b_g
    br label %L0

L6:
    ret void
}

; Function: main
define void @main() {
    ; t16 = LOAD 48
    %t16 = load i32, i32* @const_48
    ; a.g = t16
    store i32 %t16, i32* @a_g

    ; t17 = LOAD 18
    %t17 = load i32, i32* @const_18
    ; b.g = t17
    store i32 %t17, i32* @b_g

    ; CALL computeGCD
    call void @computeGCD()

    ret void
}

; Global variables
@a_g = global i32 0
@b_g = global i32 0
@gcd_g = global i32 0
@zero = global i32 0
@const_48 = global i32 48
@const_18 = global i32 18
```



```llvm
; Global variables
@a.g = global i32 0
@b.g = global i32 0
@gcd.g = global i32 0

; Function: computeGCD
define void @computeGCD() {
entry:
  br label %L0

L0:
  %t0 = load i32, i32* @b.g
  %t1 = icmp ne i32 %t0, 0
  br i1 %t1, label %L0_body, label %L1

L0_body:
  %t3 = load i32, i32* @a.g
  %t4 = load i32, i32* @b.g
  %t5 = icmp sgt i32 %t3, %t4
  br i1 %t5, label %L2, label %L2_skip

L2:
  %t6 = load i32, i32* @a.g
  %t7 = load i32, i32* @b.g
  %t8 = sub i32 %t6, %t7
  store i32 %t8, i32* @a.g
  br label %L2_skip

L2_skip:
  %t9 = load i32, i32* @a.g
  %t10 = load i32, i32* @b.g
  %t11 = icmp sle i32 %t9, %t10
  br i1 %t11, label %L3, label %L3_skip

L3:
  %t12 = load i32, i32* @b.g
  %t13 = load i32, i32* @a.g
  %t14 = sub i32 %t12, %t13
  store i32 %t14, i32* @b.g
  br label %L3_skip

L3_skip:
  br label %L0

L1:
  %t15 = load i32, i32* @a.g
  store i32 %t15, i32* @gcd.g
  ret void
}

; Function: main
define void @main() {
entry:
  ; Initialize a.g and b.g
  store i32 48, i32* @a.g
  store i32 18, i32* @b.g

  ; Call computeGCD
  call void @computeGCD()

  ret void
}
```

