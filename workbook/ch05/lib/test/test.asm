; Compiled Z80 Assembly
    org 0x100
    jp main

main:
    ld a, 5
    ld (32768), a
    ld a, 3
    ld (32769), a
    ld a, (32768)
    push af
    pop bc
    add a, c
    ld (32770), a
    ld a, 42
    ld (32771), a
    ld a, (32770)
    ld (32772), a
    ld a, 100
    ld (32773), a
    ld (32770), a
    ld a, (32770)
    ld (32774), a
    halt