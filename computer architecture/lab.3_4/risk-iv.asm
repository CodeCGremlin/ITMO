.data

.org 0x00

buffer: .byte 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95

PORT_INPUT: .word 128

PORT_OUTPUT: .word 132

MAX_INDEX: .word 31

NEWLINE: .word 10

SPACE: .word 32

LOWER_A: .word 97

LOWER_Z: .word 122

UPPER_A: .word 65

UPPER_Z: .word 90

CASE_DIFF: .word 32

ERROR_CODE_HI: .word 0xccccc

ERROR_CODE_LO: .word 3276



.text

.org 0x100



_start:

    addi a0, zero, 0

    addi a1, zero, 1

    

    addi a5, zero, 32         ; адрес констант

    lw a2, 0(a5)              ; PORT_INPUT = 128

    lw a6, 4(a5)              ; PORT_OUTPUT = 132

    lw t3, 8(a5)              ; MAX_INDEX = 31

    lw t4, 12(a5)             ; NEWLINE = 10

    lw t5, 16(a5)             ; SPACE = 32

    lw t6, 20(a5)             ; LOWER_A = 97

    

    addi a3, zero, 0



read_loop:

    beq a0, t3, check_overflow

    

    lb t1, 0(a2)

    

    beq t1, t4, end_string

    beq t1, t5, handle_space

    

    bgt t6, t1, check_upper

    lw t2, 24(a5)             ; LOWER_Z = 122

    bgt t1, t2, check_upper

    

    beqz a1, reset_flag

    lw t2, 36(a5)             ; CASE_DIFF = 32 

    sub t1, t1, t2

    j reset_flag



check_upper:

    lw t2, 28(a5)             ; UPPER_A = 65 

    bgt t2, t1, not_a_letter

    lw t2, 32(a5)             ; UPPER_Z = 90 

    bgt t1, t2, not_a_letter

    

    bnez a1, reset_flag

    lw t2, 36(a5)             ; CASE_DIFF = 32

    add t1, t1, t2

    j reset_flag



not_a_letter:

    j reset_flag



handle_space:

    addi a1, zero, 1

    j store_char



reset_flag:

    addi a1, zero, 0



store_char:

    sb t1, 0(a3)

    addi a3, a3, 1

    addi a0, a0, 1

    j read_loop



check_overflow:

    lb t1, 0(a2)

    beq t1, t4, end_string

    j overflow_error



end_string:

    addi t1, zero, 0

    sb t1, 0(a3)

    

    addi a3, zero, 0



output_loop:

    lb t1, 0(a3)

    beqz t1, halt_prog

    sw t1, 0(a6)

    addi a3, a3, 1

    j output_loop



halt_prog:

    halt



overflow_error:

    lw t0, 40(a5)             ; ERROR_CODE_HI = 0xccccc 

    slli t0, t0, 12

    lw t1, 44(a5)             ; ERROR_CODE_LO = 3276 

    add t0, t0, t1

    sw t0, 0(a6)

    halt
