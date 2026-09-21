limit: 10000

memory_size: 4096

memory_mapped_io:

  0x80: [5]

  0x84: []

reports:

  - name: "Result"

    slice: last

    view: |

      Input: {io:0x80:dec}

      Output: {io:0x84:dec}

    assert: |

      io:0x84:dec >>> 0
