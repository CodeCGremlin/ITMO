

.data

.org 0x88

l:  .word 31

r:  .word 0

c:  .word 1

t:  .word 0

v:  .word 0



.text

.org 0x100

_start:

    load_addr 0x80        

    store_addr v          

    load_imm 31

    store_addr l

    load_imm 0

    store_addr r

    load_imm 1

    store_addr c



loop:

    load_addr l

    sub r

    ble ok                

    load_addr v

    shiftr r

    and c

    store_addr t

    load_addr v

    shiftr l

    and c

    sub t

    bnez fail            

    load_addr r

    add c

    store_addr r

    load_addr l

    sub c

    store_addr l

    jmp loop



ok:

    load_imm 1

    store_addr 0x84       

    halt



fail:

    load_imm 0

    store_addr 0x84       

    halt


