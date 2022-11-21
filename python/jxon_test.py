"""Tests for jxon module."""

import math
import base64
import json
import os

import pytest

import jxon

def are_deeply_equal(value1, value2):
    """Checks values value1 and value2 for equality.

       Stable for order of keys in dicts.
    """

    if isinstance(value1, bytes):
        value1 = base64.b64encode(value1).decode('ascii')

    if isinstance(value2, bytes):
        value2 = base64.b64encode(value2).decode('ascii')

    if type(value1) != type(value2): # pylint: disable=unidiomatic-typecheck
        return False

    if isinstance(value1, dict):
        for key, value in value1.items():
            if (key not in value2) or not are_deeply_equal(value, value2[key]):
                return False
        for key, value in value2.items():
            if (key not in value1) or not are_deeply_equal(value1[key], value):
                return False
        return True

    if isinstance(value1, float) and math.isnan(value1) and math.isnan(value2):
        return True

    return value1 == value2

def is_bijective(value, encoded_value):
    """Checks both encoder and decoder."""

    return jxon.encode(value) == encoded_value \
       and are_deeply_equal(jxon.decode(encoded_value), value)

def test_special():
    """Test special and simple values."""

    assert is_bijective(None,   b'\xF0')
    assert is_bijective(False,  b'\xF1')
    assert is_bijective(True,   b'\xF2')
    assert is_bijective({},     b'\xF3\xF5')
    assert is_bijective(dict(), b'\xF3\xF5')
    assert is_bijective([],     b'\xF4\xF5')
    assert is_bijective(0.0,    b'\xF6')

def test_integers():
    """Test integer values.

       JXON encoder in Python by default should choose the most compact integer
       representation.
    """

    assert is_bijective(0,  b'\x80')
    assert is_bijective(1,  b'\x81')
    assert is_bijective(2,  b'\x82')
    assert is_bijective(3,  b'\x83')
    assert is_bijective(4,  b'\x84')
    assert is_bijective(5,  b'\x85')
    assert is_bijective(6,  b'\x86')
    assert is_bijective(8,  b'\x88')
    assert is_bijective(9,  b'\x89')
    assert is_bijective(10, b'\x8A\x0A')
    assert is_bijective(-1, b'\x8F')
    assert is_bijective(-2, b'\x8A\xFE')

    min8 = - 2**7
    max8 =   2**7 - 1
    min16 = - 2**15
    max16 =   2**15 - 1
    min32 = - 2**31
    max32 =   2**31 - 1
    min64 = - 2**63
    max64 =   2**63 - 1

    assert is_bijective(min8,       b'\x8A\x80')
    assert is_bijective(max8,       b'\x8A\x7F')

    assert is_bijective(min16,      b'\x8B\x00\x80')
    assert is_bijective(max16,      b'\x8B\xFF\x7F')
    assert is_bijective(min8 - 1,   b'\x8B\x7f\xff')
    assert is_bijective(max8 + 1,   b'\x8B\x80\x00')

    assert is_bijective(min32,      b'\x8C\x00\x00\x00\x80')
    assert is_bijective(max32,      b'\x8C\xFF\xFF\xFF\x7F')
    assert is_bijective(min16 - 1,  b'\x8C\xff\x7f\xff\xff')
    assert is_bijective(max16 + 1,  b'\x8C\x00\x80\x00\x00')

    assert is_bijective(min64,      b'\x8D\x00\x00\x00\x00\x00\x00\x00\x80')
    assert is_bijective(max64,      b'\x8D\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F')
    assert is_bijective(min32 - 1,  b'\x8D\xFF\xFF\xFF\x7F\xFF\xFF\xFF\xFF')
    assert is_bijective(max32 + 1,  b'\x8D\x00\x00\x00\x80\x00\x00\x00\x00')

    with pytest.raises(NotImplementedError):
        jxon.encode(max64 + 1)

def test_floats():
    """Test integer values.

       JXON encoder in Python by default should choose the most compact float
       representation.
    """

    assert is_bijective(1.0, b'\xF7\x00\x00\x80\x3F')
    assert is_bijective(0.5, b'\xF7\x00\x00\x00\x3F')

def check_invalid_jxon(invalid_JXON):
    """Checks that decoder raises ValueError for the specified invalid_JXON"""

    with pytest.raises(ValueError):
        jxon.decode(invalid_JXON, allow_JSON=False)

def test_invalid_heads():
    """Checks that decoder fails on forbidden head bytes."""

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
                original = json.load(f)
            with open(os.path.join(EXAMPLES_PREFIX, name + '.jxon'), 'rb') as f:
                expected = f.read()

            assert are_deeply_equal(original, jxon.decode(expected))
