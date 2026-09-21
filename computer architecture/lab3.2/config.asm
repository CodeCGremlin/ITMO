limit: 10000

memory_size: 4096



memory_mapped_io:

  0x80: [6]

  0x84: []



reports:

  - name: "Проверка"

    slice: last

    view: |

      numio[0x80]: {io:0x80:dec}

      numio[0x84]: {io:0x84:dec}

    assert: |

      numio[0x80]: [] >>> []

      numio[0x84]: [] >>> [4]
