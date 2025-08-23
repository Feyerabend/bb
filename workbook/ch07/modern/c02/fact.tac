DECLARE n
DECLARE fact
DECLARE i
PROC factorial:
fact := 1
i := 1
L0:
t0 := i <= n
IF_FALSE t0 GOTO L1
t1 := fact * i
fact := t1
t2 := i + 1
i := t2
GOTO L0
L1:
ENDPROC factorial
READ n
CALL factorial
WRITE fact