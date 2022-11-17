"""Tests for jxon module."""

import os
import json

import pytest

import jxon

def test_special():
    """Test special and simple values."""

    assert jxon.encode(None)   == b'\xF0'
    assert jxon.encode(False)  == b'\xF1'
    assert jxon.encode(True)   == b'\xF2'
    assert jxon.encode({})     == b'\xF3\xF5'
    assert jxon.encode(dict()) == b'\xF3\xF5'
    assert jxon.encode([])     == b'\xF4\xF5'
    assert jxon.encode(0.0)    == b'\xF6'

def test_integers():
    """Test integer values.

       JXON encoder in Python by default should choose the most compact integer
       representation.
    """

    assert jxon.encode(0)      == b'\x80'
    assert jxon.encode(1)      == b'\x81'
    assert jxon.encode(2)      == b'\x82'
    assert jxon.encode(3)      == b'\x83'
    assert jxon.encode(4)      == b'\x84'
    assert jxon.encode(5)      == b'\x85'
    assert jxon.encode(6)      == b'\x86'
    assert jxon.encode(8)      == b'\x88'
    assert jxon.encode(9)      == b'\x89'
    assert jxon.encode(10)     == b'\x8A\x0A'
    assert jxon.encode(-1)     == b'\x8F'
    assert jxon.encode(-2)     == b'\x8A\xFE'

    min8 = - 2**7
    max8 =   2**7 - 1
    min16 = - 2**15
    max16 =   2**15 - 1
    min32 = - 2**31
    max32 =   2**31 - 1
    min64 = - 2**63
    max64 =   2**63 - 1

    assert jxon.encode(min8)      == b'\x8A\x80'
    assert jxon.encode(max8)      == b'\x8A\x7F'

    assert jxon.encode(min16)     == b'\x8B\x00\x80'
    assert jxon.encode(max16)     == b'\x8B\xFF\x7F'
    assert jxon.encode(min8 - 1)  == b'\x8B\x7f\xff'
    assert jxon.encode(max8 + 1)  == b'\x8B\x80\x00'

    print(jxon.encode(min16 - 1))
    assert jxon.encode(min32)     == b'\x8C\x00\x00\x00\x80'
    assert jxon.encode(max32)     == b'\x8C\xFF\xFF\xFF\x7F'
    assert jxon.encode(min16 - 1) == b'\x8C\xff\x7f\xff\xff'
    assert jxon.encode(max16 + 1) == b'\x8C\x00\x80\x00\x00'

    assert jxon.encode(min64)     == b'\x8D\x00\x00\x00\x00\x00\x00\x00\x80'
    assert jxon.encode(max64)     == b'\x8D\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F'
    assert jxon.encode(min32 - 1) == b'\x8D\xFF\xFF\xFF\x7F\xFF\xFF\xFF\xFF'
    assert jxon.encode(max32 + 1) == b'\x8D\x00\x00\x00\x80\x00\x00\x00\x00'

    with pytest.raises(NotImplementedError):
        jxon.encode(max64 + 1)

def test_floats():
    """Test integer values.

       JXON encoder in Python by default should choose the most compact float
       representation.
    """

    assert jxon.encode(1.0)      == b'\xF7\x00\x00\x80\x3F'
    assert jxon.encode(0.5)      == b'\xF7\x00\x00\x00\x3F'

def check_invalid_jxon(invalid_JXON):
    """Checks that decoder raises ValueError for the specified invalid_JXON"""

    with pytest.raises(ValueError):
        jxon.decode(invalid_JXON, allow_JSON=False)

def test_invalid_heads():
    """Checks that decoder failes on forbidden head bytes."""

    for byte in range(128):
        check_invalid_jxon(bytes([byte, 0xF0]))
    for byte in range(0xC0, 0xEF + 1):
        check_invalid_jxon(bytes([byte, 0xF0]))
    for byte in range(0xFE, 0xFF + 1):
        check_invalid_jxon(bytes([byte, 0xF0]))

EXAMPLES_PREFIX = '../examples'
def test_examples():
    """Checks consistency of examples."""

    examples = os.listdir(EXAMPLES_PREFIX)
    for example in examples:
        if example.endswith('.jxon'):
            name = example[:-5]
            with open(os.path.join(EXAMPLES_PREFIX, name + '.json'), 'r', encoding="utf-8")  as f:
                json_decoded = json.load(f)
            jxon.encode(json_decoded)
            #with open(os.path.join(EXAMPLES_PREFIX, name + '.jxon'), 'rb') as f:
            #    jxon_decoded = jxon.decode(f.read())
            #print(json_value)
            #print(jxon_value)
            #jxon.encode(json_decoded)
