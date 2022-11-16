# JXON

`JXON` is a binary format for structured data.

* Simple to understand and use
* Uses modern binary types "as is": little-endian integers, IEEE-754 floats and UTF-8 strings
* Allows storing repeated keys in a special table for reducing memory consumption
* `JXON` and `JSON` are not mutually exclusive, interchangeability is a design goal

## Status

Draft. Format for `BigInt` is yet to be [chosen](docs/bigint_ideas.md).

## Examples

See [examples](examples#jxon-examples) directory. `*.jxon` files are JXON values,
`*.txt` are their hex dumps and `*.json` are their respective JSON equivalents.

## Specification

`JXON` value is a sequence of commands. Each command starts with 1 byte header
called *head*, which may be followed by arguments of the command.

![JXON bytes diagram](docs/jxon.svg)

Commands:

```
Head      Arguments                    Meaning
(Hex)
--------- ---------------------------- ----------------------------------------

0x00-0x7F                              ERROR: forbidden ASCII characters

0x8?      [integer]                    integer (see below)
0x9?      [size] byte*                 BLOB (arbitrary binary data, also known as byte string)
0xA?      [size] utf8char* 0           UTF-8 string
0xB?      [size] utf8char* 0 index     put UTF-8 string to table[index], 0<=index<128

0xC0-0xEF                              ERROR: reserved

0xF0                                   null
0xF1                                   false
0xF2                                   true
0xF3                                   start object
0xF4                                   start array
0xF5                                   end object or array
0xF6                                   0.0 (floating-point zero)
0xF7      float                        32-bit IEEE float
0xF8      double                       64-bit IEEE float
0xF9      BigInt BigInt                large float (mantissa and binary exponent)

0xFA-0xFD                              ERROR: reserved
0xFE-0xFF                              ERROR: forbidden UTF-8/16/32 BOMs
```

Integers (`0x8?`) and sizes (in `0x9?`, `0xA?` and `0xB?` commands) may be in
one of the following forms:

```
Head        i       Arguments           Value
Binary
----------- ------- ------------------- ---------------------------------------

b10xx0000   0                           0
b10xx0001   1                           1
b10xx0010   2                           2
b10xx0011   3                           3
b10xx0100   4                           4
b10xx0101   5                           5
b10xx0110   6                           6
b10xx0111   7                           7
b10xx1000   8                           8
b10xx1001   9                           9
b10xx1010   10      Int8                Little-endian  8-bits signed integer
b10xx1011   11      Int16               Little-endian 16-bits signed integer
b10xx1100   12      Int32               Little-endian 32-bits signed integer
b10xx1101   13      Int64               Little-endian 64-bits signed integer
b10xx1110   14      BigInt              Signed BigInt
b10xx1111   15                          -1
```

### BigInt

[TBA](docs/bigint_ideas.md)

### The table

Parser should keep up to 128 string values in a special array of strings called
*table* while parsing. Each value in the table has an index in range 0..127. At
the beginning of parsing the table should be filled with empty strings.

To store a string to the table command `Bi` is used. Format of the command is
similar to string value, the only difference is 1-byte index value at the end:

```
Binary   Hex    Arguments                       Meaning
1011iiii Bi     <size> utf8char* 0 index        put the string to table[index]
                                                (0 <= index < 128)
```

Values in the table may be overwritten by following "put" commands.

The table is used only for keys. It cannot be used for values.

### Structures: arrays and objects

An array starts with `F4` and ends with `F5`. Between the two must be a
sequence of JXON values.

An object starts with `F3` and ends with `F5`. Between the two bytes must
be a sequence of key-value pairs.

Keys are always strings. They may be specified with an index to the table:

```
Binary   Hex    Arguments                       Meaning
0iiiiiii                                        Use table[index] as the key, where index is the head byte
1010iiii Ai     <size> utf8char* 0              Use the specified UTF-8 string as key
```
