define i32 @compute(i32 %a, i32 %b) local_unnamed_addr #0 {
entry:
    %0 = mul i32 %b, 2
    %1 = add i32 %a, %0
    ret i32 %1
}

!wasm.exports = !{!0}
!0 = !{void (i32, i32)* @compute, !"compute"}