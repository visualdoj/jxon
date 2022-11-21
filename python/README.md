# Python JXON

## Library

[jxon.py](jxon.py) is the library.

### Conversion table

|Python          |JXON   |
|:---------------|:------|
|dict            |object |
|list, tuple     |array  |
|str             |string |
|int             |integer|
|float           |float  |
|True            |true   |
|False           |false  |
|None            |null   |
|bytes           |BLOB   |
|numbers.Rational|float  |


### Encoder

```python
import jxon

# jxon.encode() returns bytes
blob = jxon.encode({"a": 1, "b": "str"})

# strings in keys_table are used for compression of repeated keys
blob = jxon.encode([{"foo": 1}, {"foo": 2}, {"foo": 3}], keys_table=["foo"])
```

### Decoder

```python
import jxon

# jxon.decode() takes bytes and returns python value
print(jxon.decode(b'\xAA\x0C' b'Hello world!' b'\x00'))



# jxon.decode() can parse JSONs as well
print(jxon.decode(b'{"foo": "bar", "num": 1}'))

# to disable this feature pass allow_JSON=False
jxon.decode(b'{"foo": "bar", "num": 1}', allow_JSON=False)
# ... ValueError: Unknown head in JXON 0x7b
```

## Command line tool

```
make examples

    Generates examples in ../examples directory.
    Requires protoc and protobuf installed.
```
