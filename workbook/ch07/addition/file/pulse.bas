10 REM Pulsing Circles
20 CLS 0
30 TEXT 80, 10, "Pulsing Circles", 65535
40 TEXT 60, 220, "Press Ctrl+C to stop", 2016
50 LET R = 10
60 LET DIR = 1
70 REM Main animation loop
80 CLS 0
90 TEXT 80, 10, "Pulsing Circles", 65535
100 REM Draw concentric pulsing circles
110 CIRCLE 160, 120, R, 63488
120 CIRCLE 160, 120, R + 20, 2016
130 CIRCLE 160, 120, R + 40, 31
140 CIRCLE 160, 120, R + 60, 65504
150 WAIT 50
160 REM Update radius
170 LET R = R + DIR * 2
180 REM Bounce between 10 and 50
190 IF R > 50 THEN DIR = -1
200 IF R < 10 THEN DIR = 1
210 GOTO 80
