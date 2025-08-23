DECLARE x
x := 5
L0:
t0 := x > 0
IF_FALSE t0 GOTO L1
WRITE x
t1 := x - 1
x := t1
GOTO L0
L1: