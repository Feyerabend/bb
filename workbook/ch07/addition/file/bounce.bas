10 REM Bouncing Ball Animation
20 CLS 0
30 TEXT 80, 10, "Bouncing Ball Demo", 65535
40 TEXT 60, 220, "Press Ctrl+C to stop", 2016
50 LET X = 160
60 LET Y = 120
70 LET DX = 3
80 LET DY = 2
90 LET R = 15
100 REM Main animation loop
110 CLS 0
120 TEXT 80, 10, "Bouncing Ball Demo", 65535
130 CIRCLEF X, Y, R, 63488
140 WAIT 50
150 LET X = X + DX
160 LET Y = Y + DY
170 REM Bounce off walls
180 IF X < R THEN DX = 3
190 IF X > 320 - R THEN DX = -3
200 IF Y < R + 20 THEN DY = 2
210 IF Y > 240 - R THEN DY = -2
220 GOTO 110
