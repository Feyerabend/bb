define i32 @main(i32, i32) {
  ; Block entry
  ; Block exit
  %%ptr0 = alloca i32* i32*
  %%ptr1 = alloca i32* i32*
  % = store i32 5, i32* %ptr0
  % = store i32 10, i32* %ptr1
  %0 = load i32 i32* %ptr0
  %1 = load i32 i32* %ptr1
  %2 = add i32 i32 0, i32 1
  % = br label %exit
  % = ret 2
}