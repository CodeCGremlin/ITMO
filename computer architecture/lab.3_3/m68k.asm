.text

.org 0x0100



_start:

    movea.l 4000, A7

    jsr rle_decompress

    halt



rle_decompress:

    movea.l 128, A0      

    movea.l 2048, A1     

    clr.l D0             

    clr.l D7            



read_loop:

    clr.l D1

    move.b (A0), D1

    add.l 1, D7    

    cmp.b 10, D1

    beq done



    cmp.b 48, D1

    ble error_format_drain

    cmp.b 57, D1

    bgt error_format_drain



    sub.b 48, D1

    move.l D1, D2



    clr.l D3

    move.b (A0), D3

    add.l 1, D7         

    cmp.b 10, D3

    beq error_format_nodrain 



    move.l D2, -(A7)

    move.l D3, -(A7)

    jsr process_pair

    move.l (A7)+, D3

    move.l (A7)+, D2



    cmp.l 0, D1

    blt error_overflow_drain



    jmp read_loop



done:

    movea.l 2048, A2     

    movea.l 132, A3     

    move.l D0, D4       

    cmp.l 0, D4

    beq flush_done

flush_loop:

    move.b (A2)+, D5

    move.b D5, (A3)

    sub.l 1, D4

    bgt flush_loop

flush_done:

    rts



process_pair:

    move.l 8(A7), D2

    move.l 4(A7), D3



write_loop:

    cmp.l 63, D0         

    bge overflow_err



    move.b D3, (A1)+     

    add.l 1, D0



    sub.l 1, D2

    bgt write_loop



    clr.l D1

    rts



overflow_err:

    clr.l D1

    sub.l 1, D1          

    rts





drain_input:

    cmp.l 128, D7        

    bge drain_done

    move.b (A0), D6

    add.l 1, D7

    cmp.b 10, D6

    bne drain_input

drain_done:

    rts



error_format_drain:

    jsr drain_input

error_format_nodrain:

    movea.l 132, A3

    clr.l D4

    sub.l 1, D4          

    move.l D4, (A3)      

    rts



error_overflow_drain:

    jsr drain_input

    movea.l 132, A3

    move.l 0xCCCCCCCC, D4

    move.l D4, (A3)      

    rts
