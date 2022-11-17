#!/usr/bin/env python 

#
#   Module for encoding and decoding JXON values.
#   Originally published to https://github.com/visualdoj/jxon
#
#   Author:  Doj
#   License: Public domain or MIT
#

import io
import json
import math
import numbers
import struct
import fractions


def decode(data, allowJSON=True):
    """Decodes JXON and returns it as a python value
    """

    table=[]
    stream = io.BytesIO(data)

    def guess_jxon(data):
        first = data[0]
        return (first >= 0x80) and (first < 0xFE) and (first != 0xEF)

    def decode_bigint():
        raise NotImplementedError('BigInt Decoder')

    def decode_int(head):
        low = head & 0x0F
        if low == 10:
            return struct.unpack('<b', stream.read(1))
        elif low == 11:
            return struct.unpack('<h', stream.read(2))
        elif low == 12:
            return struct.unpack('<i', stream.read(4))
        elif low == 13:
            return struct.unpack('<q', stream.read(8))
        elif low == 14:
            return decode_bigint()
        elif low == 15:
            return -1
        else:
            return low

    def decode_key_from_stream(head):
        if (head & 0xF0) != 0xB0:
            return ValueError('key must be string')
        i = decode_int(head)
        s = stream.read(i).decode('utf-8')
        stream.read(1) # skip null character
        return s

    def decode_object_from_stream():
        d = dict()
        while True:
            head = stream.read(1)
            if head == 0xF5:
                return d
            if head < 0x80:
                key = table[head]
            else:
                key = decode_key_from_stream(head)
            value = decode_value_from_stream()
            d[key] = value

    def decode_array_from_stream():
        raise NotImplementedError('TODO array decoder')

    def decode_array_from_stream():
        raise NotImplementedError('TODO object decoder')

    def decode_value_from_stream():
        while True:
            head = stream.read(1)
            if   head == 0xF0: return None
            elif head == 0xF1: return False
            elif head == 0xF2: return True
            elif head == 0xF3: return decode_object_from_stream()
            elif head == 0xF4: return decode_array_from_stream()
            elif head == 0xF5: return ValueError('unexpected end of a structure')
            elif head == 0xF6: return 0.0
            elif head == 0xF7: return struct.unpack('<f', stream.read(4))
            elif head == 0xF8: return struct.unpack('<d', stream.read(8))
            elif head == 0xF9: return fractions.Fraction(decode_bigint(), decode_bigint())
            elif 0x80 <= head[0] <= 0xBF:
                i = decode_int(head)
                if head & 0xF0 == 0x80:
                    return i
                elif head & 0xF0 == 0x90:
                    return stream.read(i)
                elif head & 0xF0 == 0xA0:
                    s = stream.read(i).decode('utf-8')
                    stream.read(1) # skip null character
                    return s
                elif head & 0xF0 == 0xB0:
                    s = stream.read(i).decode('utf-8')
                    stream.read(1) # skip null character
                    index = struct.unpack('<B', stream.read(1))
                    table[index] = s
                    continue
            else:
                raise ValueError('Invalid JXON')

    if guess_jxon(data):
        return decode_value_from_stream()
    else:
        if allowJSON:
            try:
                return json.loads(data)
            except:
                raise ValueError('data must be in JXON or JSON format')
        else:
            raise ValueError('invalid head value')


def encode(value,
           keys_table=None,
          ):
    """Encodes the specified value as JXON and returns it as bytes
    """

    keys = dict()

    def encode_null(n):
        return b'\xF0'

    def encode_bigint(i):
        raise NotImplementedError('BigInt encoder')

    def encode_bigfloat(numerator, denominator):
        return bytearray(0xF9) + encode_bigint(numerator) + encode_bigint(denominator)

    def encode_int_or_len(head, i):
        if 0 <= i <= 9:
            return struct.pack("<B", head | i)
        if i == -1:
            return b'\x8F'
        if -128 <= i <= 127:
            return struct.pack("<Bb", head | 0x0A, i)
        if -32768 <= i <= 32767:
            return struct.pack("<Bh", head | 0x0B, i)
        if -2147483648 <= i <= 2147483647:
            return struct.pack("<Bi", head | 0x0C, i)
        if -9_223_372_036_854_775_808 <= i <= 9_223_372_036_854_775_807:
            return struct.pack("<Bq", head | 0x0D, i)
        return bytes(head | 0x0E) + encode_bigint(i)

    def encode_bool(b):
        if b:
            return b'\xF2'
        else:
            return b'\xF1'

    def msb_lsb(i):
        b = bin(abs(i))
        msb = len(b)-2 - 1 # ignore '0b' prefix
        lsb = 0
        for c in reversed(b):
            if c == '1':
                break
            lsb += 1
        return msb, lsb

    def encode_rational(numerator, denominator):
        if numerator == 0:
            return b'\xF6'

        if denominator & (denominator - 1) != 0:
            return encode_bigfloat(numerator, denominator)

        e = math.frexp(denominator)[1] - 1 # log2(denominator)

        msb, lsb = msb_lsb(numerator)
        resolution = msb - lsb + 1

        # r == numerator * 2**(-e)

        # r == numerator * 2**(-23-lsb) * 2**(-e+23+lsb)
        # r == numerator * 2**(-msb)    * 2**(-e+msb)
        if (
            ((resolution <= 23) and (-e+23+lsb == -126)) # denormalized 32-bit float
        or  ((resolution <= 24) and (1-127 <= -e+msb <= 254-127)) # normalized 32-bit float
        ):
            return struct.pack("<Bf", 0xF7, r)

        # r == numerator * 2**(-52-lsb) * 2**(-e+52+lsb)
        # r == numerator * 2**(-msb)    * 2**(-e+msb)
        if (
            ((resolution <= 52) and (-e+52+lsb == -1022)) # denormalized 64-bit float
        or  ((resolution <= 53) and (1-1023 <= -e+msb <= 2046-1023)) # normalized 64-bit float
        ):
            return struct.pack("<Bd", 0xF8, r)

        return encode_bigfloat(numerator, denominator)

    def encode_float(f):
        if f == 0.0:
            return b'\xF6'

        # special IEEE values
        if f != f:
            return struct.pack("<Bf", 0xF7, f)

        numerator, denominator = f.as_integer_ratio()
        return encode_rational(numerator, denominator)

    def encode_str(head, s):
        return encode_int_or_len(head, len(s.encode('utf-8'))) + s.encode('utf-8') + b'\x00'

    def encode_blob(head, b):
        return encode_int_or_len(head, len(b)) + b

    def encode_dict(document):
        blob = bytearray(b'\xF3') # "start object" marker

        for key, value in document.items():
            if type(key) is not str:
                raise TypeError("keys must be strings")
            if key in keys:
                blob = blob + struct.pack("<B", keys[key])
            else:
                blob = blob + encode_str(0xA0, key)
            blob = blob + encode_value(value)

        return blob + b'\xF5' # "end object" marker

    def encode_list(array):
        blob = bytearray(b'\xF4') # "start array" marker

        for value in array:
            blob = blob + encode_value(value)

        return blob + b'\xF5' # "end array" marker

    blob = bytearray()
    if keys_table:
        index = 0
        for key in keys_table:
            if index > 127:
                break
            keys[key] = index
            blob = blob + encode_str(0xB0, key) + struct.pack("<B", index)
            index += 1

    def encode_value(value):
        if value is None:
            return encode_null(value)
        elif value is True:
            return encode_bool(value)
        elif value is False:
            return encode_bool(value)
        elif isinstance(value, int):
            return encode_int_or_len(0x80, value)
        elif isinstance(value, numbers.Rational):
            return encode_rational(value.numerator, value.denominator)
        elif isinstance(value, float):
            return encode_float(value)
        elif isinstance(value, str):
            return encode_str(0xA0, value)
        elif isinstance(value, bytes):
            return encode_blob(0x90, value)
        elif isinstance(value, dict):
            return encode_dict(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            return encode_list(value)
        else:
            raise TypeError("value must be json-like value")

    return blob + encode_value(value)


#  ---------------------------------------------------------------------------
#
#                            .:~~. ..
#                    .    ^JB#&&&BGBGP?^         .:.
#                :?JPP5?75@@#BBB@B&#JP#B~:::!Y5BB#&BY5557^
#               J&#BGB@@@@@@@G!!J?J#&@@@@&&&@@@&@&@@@@BPB#?
#           :?5P@@B5B@@&&@@@&@B?!^Y@@&#@@@@@@@@BPJ#&B&@@&@@BGG5!:
#          ~&@@@&@@@@@@#GYP@&#@@B#@@&##&@@&#@@@&GY#Y?#@#5&@@&5#&B!
#        :G&@@@@@@&BG#@@&PYBJY&&#@@&&BPP@@&G#@@&G~^?5#B5PG&&5~JG&B5^
#       ^G@@@&&BPB@B!7P@&B5#PPPB@&&##7!~#@@&BB&@B! :^7Y555#&G7!5#5GJ
#       P@@@&#PP7JBG55JPJYJ77~.Y@@@#&5~.!&#B5B&P#B^^:.:^!G#&@@&&#@@7
#       G@@@@@&&G!??^....^....:Y&@&&B&Y:^75PGBJ7##~:^ !?B@&#GBG#&@@&57~.
#    :~J&@@@@&&&&##Y77:.^?:...:B#GP#BB! .^  !YPPPP.?7J#P&&#G!!P@@#@@@@@B?:
#   !BB@@@&&&#&&&#&7 .^!!  .7!:J@&PB#Y~J5:.^7YB&?::Y!B&G5PY7~?&@#B@@&PB@@G^
#  !#&Y?#@@@&#57PG5^:~ ^J   ^7?YPB#&@BP#P~!Y7YB5?^J. ~&#Y7:::P#PB##5?5P#@#GJ
#  Y@B5P##&@@@###@?.?B5 ~7    .JJ .^?J5P?5G5JY~ .G:   !PPJ:^.!P5P&J:.JP#&&B5.
#  ^&@@&BGYY#@@@@#??##B^:J7:..  5:     :^~. .   ?7     ~?JJ?5GP55!:~:JPGG&@G:
# :P#@####7^^7?PBB##G!::::^~!!7!75             7?        :~!Y?^~^~:::~JG#BP##^
# ^#G&@BPP:^^.  ^^^:           :^JJ           !J        .:^~7~^:JBPBG#BBB!!G#~
#  !@@@BP?!J:.7J~                .G!         ~P7!!~~~~!7~^^..  ~#5?BB5P##BGPP:
#  .P@@#GB&&5YY#P  :JY7:          :P!     .~Y?: ......:!7.    .?Y7.~7?5B&@#7^
#    J&@@@@BB@@G?:.^!P#P           :B:  :7Y7:           ^7!.   77!:?GB&#@@G
#     ^7P@&&@GJ~:!GG~J&B            ~5!?Y~.     ..!~:^.   ?!~^::7J5YGGGB#&@?
#       :GBG@GGJJG#@GB#7             ~#!       ^77^^:~^  .?  .:..:^^!!~7PB@Y
#        .?YP&@@&@&55J.              ~G        JJ~.::    :!   .!?YY::^JG##B~
#            ^!!7~:                  ^B.      ~7Y~..::.:. .: ~!?~5BGJYG#@P7.
#                                    :B.      ~5?!7^. ^. . ::??7JJJB#JJB#:
#                                    ^B.       !5GYJ7:^!~!?7^^YP#&##BY5Y~
#                                    !G         .?J57!7P57PP^!!7G@&7:^:
#                                    75          .!JP5G#BPPY5G#BBP~
#                                    ~P             :~~::!?JY?77^
#                                     .                    .
#
#               __      ___                 _ _____        _
#               \ \    / (_)               | |  __ \      (_)
#                \ \  / / _ ___ _   _  __ _| | |  | | ___  _
#                 \ \/ / | / __| | | |/ _` | | |  | |/ _ \| |
#                  \  /  | \__ \ |_| | (_| | | |__| | (_) | |
#                   \/   |_|___/\__,_|\__,_|_|_____/ \___/| |
#                                                        _/ |
#                                                       |__/
#
#  ---------------------------------------------------------------------------
#  This software is available under 2 licenses -- choose whichever you prefer.
#  ---------------------------------------------------------------------------
#  ALTERNATIVE A - MIT License
#
#  Copyright (c) 2022 Viktor Matuzenko aka Doj
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#
#  ---------------------------------------------------------------------------
#  ALTERNATIVE B - Public Domain (www.unlicense.org)
#
#  This is free and unencumbered software released into the public domain.
#
#  Anyone is free to copy, modify, publish, use, compile, sell, or distribute
#  this software, either in source code form or as a compiled binary, for any
#  purpose, commercial or non-commercial, and by any means.
#
#  In jurisdictions that recognize copyright laws, the author or authors of
#  this software dedicate any and all copyright interest in the software to
#  the public domain. We make this dedication for the benefit of the public at
#  large and to the detriment of our heirs and successors. We intend this
#  dedication to be an overt act of relinquishment in perpetuity of all
#  present and future rights to this software under copyright law.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#  For more information, please refer to <http://unlicense.org/>
#  ---------------------------------------------------------------------------
