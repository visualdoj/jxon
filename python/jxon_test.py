import os
import json

import pytest

import jxon

examples_prefix = '../examples'
def test_examples():
    examples = os.listdir(examples_prefix)
    for example in examples:
        if example.endswith('.jxon'):
            name = example[:-5]
            with open(os.path.join(examples_prefix, name + '.json'), 'r')  as f:
                json_decoded = json.load(f)
            jxon_encoded = jxon.encode(json_decoded)
            #with open(os.path.join(examples_prefix, name + '.jxon'), 'rb') as f:
            #    jxon_decoded = jxon.decode(f.read())
            #print(json_value)
            #print(jxon_value)
            #jxon.encode(json_decoded)

def check_invalid_jxon(invalid_jxon):
    with pytest.raises(ValueError):
        jxon.decode(invalid_jxon, allowJSON=False)

def test_invalid_heads():
    for c in range(128):
        check_invalid_jxon(bytes([c]))
    for c in range(0xC0, 0xEF + 1):
        check_invalid_jxon(bytes([c]))
    for c in range(0xFE, 0xFF + 1):
        check_invalid_jxon(bytes([c]))
