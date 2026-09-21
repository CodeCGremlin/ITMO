limit: 10000

memory_size: 4096



memory_mapped_io:

  0x80: [104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100, 10]

  0x84: []



reports:

  - name: "Трассировка"

    slice: all

    view: |

      PC:{pc:hex} {instruction} {pc:label}



  - name: "Проверка памяти"

    slice: last

    view: |

      mem[0..31]: {memory:0:31}
