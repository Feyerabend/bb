; target triple = "arm64-apple-macosx13.0.0"

; Declare the printf function
;declare i32 @printf(i8*, ...)

; Define the format string as a global constant
;@format = private constant [4 x i8] c"%d\0A\00"
;@format_str = private constant [14 x i8] c"Hello, LLVM!\0A\00"

define i32 @compute(i32 %a, i32 %b) {
entry:
    %0 = mul i32 %b, 2      ; Compute b * 2
    %1 = add i32 %a, %0     ; Compute a + (b * 2)
    ret i32 %1              ; Return the result
}

; Main function
;define i32 @main() {
;entry:
    ; Load the format string
;    %format_ptr = getelementptr inbounds [4 x i8], [4 x i8]* @format, i32 0, i32 0
    
    ; Print the integer 42
;    %call = call i32 (i8*, ...) @printf(i8* %format_ptr, i32 42)

;    %format_ptr2 = getelementptr inbounds [13 x i8], [13 x i8]* @format_str, i32 0, i32 0
;    %call2 = call i32 (i8*, ...) @printf(i8* %format_ptr2)

    ; Return 0
;    ret i32 0
;}
