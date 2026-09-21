.text

.org 0x090



_start:

    @p 0x80         

    count_divisors

    !p 0x84             

    halt



count_divisors:

    dup if invalid_zero

    dup 0x80000000 and if valid_input

    drop

    0 inv

    ;



valid_input:

    !p VAR_NUMBER

    1

    !p VAR_DIVISOR

    0

    !p VAR_COUNT

    outer ;



outer:

    @p VAR_NUMBER

    @p VAR_DIVISOR

    inv 1 + +

    dup 0x80000000 and if continue_outer

    drop

    @p VAR_COUNT

    ;



continue_outer:

    drop

    @p VAR_NUMBER

    !p VAR_REMAINDER

    mod_loop ;



mod_loop:

    @p VAR_REMAINDER

    @p VAR_DIVISOR

    inv 1 + +

    dup 0x80000000 and if save_and_continue

    drop

    check_divisible ;



save_and_continue:

    !p VAR_REMAINDER

    mod_loop ;



check_divisible:

    @p VAR_REMAINDER

    if increment_count

    next_divisor ;



increment_count:

    @p VAR_COUNT

    1 +

    !p VAR_COUNT

    next_divisor ;



next_divisor:

    @p VAR_DIVISOR

    1 +

    !p VAR_DIVISOR

    outer ;



invalid_zero:

    drop

    0 inv

    ;



.data

.org 0x0200



VAR_NUMBER:    .word 0

VAR_DIVISOR:   .word 0

VAR_COUNT:     .word 0

VAR_REMAINDER: .word 0
