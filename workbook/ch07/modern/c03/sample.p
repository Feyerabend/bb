var x, y, z;

procedure waste;
begin
    x := 5 + 3 * 0;
    y := x + 0;
    z := y * 1
end;

begin
    x := 10 + 2 * 3;
    y := x - 0;
    z := y / 1;
    
    if 1 = 1 then
        begin
            ! x;
            ! y
        end;
    
    if 0 = 1 then
        begin
            x := 999;
            y := 888
        end;
    
    while x > 15 do
        begin
            ! x;
            x := x - 1
        end;
    
    while 0 do
        begin
            x := x + 1
        end;
    
    call waste
end.