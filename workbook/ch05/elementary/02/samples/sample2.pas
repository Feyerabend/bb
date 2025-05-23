var x, y, q, r, n, f;

procedure divide;
var w;
begin
  r := x;
  q := 0;
  w := y;
  while (w <= r) do
    w := 2 * w;
  while (w > y) do
  begin
    q := 2 * q;
    w := w / 2;
    if (w <= r) then
    begin
      r := r - w;
      q := q + 1
    end
  end
end;

procedure gcd;
var f, g;
begin
  f := x;
  g := y;
  while (f # g) do
  begin
    if (f < g) then g := g - f;
    if (g < f) then f := f - g
  end;
  z := f
end;

procedure fact;
begin
  if (n > 1) then
  begin
    f := n * f;
    n := n - 1;
    call fact;
  end;
end;


begin
  x := 3;
  y := 6;
  call divide;

  x := 3;
  y := 6;
  call gcd;

  f := 1;
  n := 10;
  call fact;
end.
