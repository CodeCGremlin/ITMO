limit: 10000

memory_size: 4096



memory_mapped_io:

  0x80: [51, 65, 52, 66, 52, 67, 10]

  0x84: []



reports:

  - name: "Трассировка"

    slice: all

    view: |

      PC:{pc:hex} {instruction} {pc:label} | D0:{D0:dec} D1:{D1:dec} D2:{D2:dec} D3:{D3:dec} A0:{A0:hex} A1:{A1:hex}



  - name: "Проверка"

    slice: last

    view: |

      numio[0x84]: {io:0x84:dec}

    assert: |

      numio[0x84]: [] >>> [65,65,65,66,66,66,66,67,67,67,67]
