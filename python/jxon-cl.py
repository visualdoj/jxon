#!/usr/bin/env python

"""Command line tool for working with JXON and some utilities for JXON CI."""

import base64
import fractions
import io
import json
import numbers
import os
import sys
import struct

import jxon

class JSONExtendedEncoder(json.JSONEncoder):
    """Adds support for additional types to JXON encoder."""

    def default(self, obj):
        if isinstance(obj, fractions.Fraction):
            return obj.numerator / obj.denominator
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('ascii')
        return json.JSONEncoder.default(self, obj)

EXAMPLES_PREFIX = '../examples/'

def hexdump(blob, maxchars):
    dump = ""
    for b in blob:
        dump = dump + "{0:#0{1}X}".format(b, 4)[2:]
    if len(dump) > maxchars:
        dump = dump[:maxchars-3] + '...'
    if len(dump) == 0:
        dump = " "
    return dump

class Readme:
    def __init__(self):
        self.file = None
        pass

    def start(self):
        """Opens examples/README.md and writes preambula to it."""

        self.file = open(os.path.join(EXAMPLES_PREFIX, 'README.md'), 'w', encoding='utf-8')
        self.file.write('# JXON Examples\n')
        self.file.write('\n')
        self.file.write('This directory contains examples of JXON values.\n')
        self.file.write('`*.jxon` files are JXON values,\n')
        self.file.write('`*.txt` are their annotated hex dumps and\n')
        self.file.write('`*.json` are their respective JSON equivalents.\n')

    def end(self):
        """Ends README.md and closes it."""

        if self.file:
            self.file.close()
            self.file = None

    def start_chapter(self):
        """Starts a new chapter."""

        if self.file:
            self.file.write('\n')
            self.file.write(f'## {name} \n')
            self.file.write('\n')
            self.file.write('|File|Hex|Meaning|\n')
            self.file.write('|:---|:--|:------|\n')

    def add_example(self, filename, jxon, meaning, protobuf=""):
        """Adds a new example to the current table"""

        if self.file:
            jxon_dump = hexdump(jxon, 20)
            protobuf_link = f", [protobuf]({protobuf})" if protobuf else ""
            self.file.write(f"|[{filename}.jxon]({filename}.jxon) ("
                            f"[dump]({filename}.txt),"
                            f"[json]({filename}.json){protobuf_link})"
                            f"|{jxon_dump}"
                            f"|{meaning}|\n")

readme = Readme()

def dump_pretty(stream, f, indent=""):
    """Dumps JXON value with indentations and (maybe) annotations."""

    def readhex(count):
        s = ""
        block = stream.read(count)
        for b in block:
            s = s + "{0:#0{1}x}".format(b,4)[2:]
        i = None
        if count == 1:
            i = struct.unpack("<b", block)[0]
        elif count == 2:
            i = struct.unpack("<h", block)[0]
        elif count == 4:
            i = struct.unpack("<i", block)[0]
        elif count == 8:
            i = struct.unpack("<q", block)[0]
        return s, i

    def readhex_i(head):
        i = 0
        additional = ""
        if head & 0x0F == 10:
            additional, i = readhex(1)
        elif head & 0x0F == 11:
            additional, i = readhex(2)
        elif head & 0x0F == 12:
            additional, i = readhex(4)
        elif head & 0x0F == 13:
            additional, i = readhex(8)
        elif head & 0x0F == 14:
            pass # TODO BigInt
        elif head & 0x0F == 15:
            i = -1
        else:
            i = head & 0x0F
        return additional, i

    def readhex_si(additional, head, i):
        additional = ""
        block = stream.read(i)
        for b in block:
            if b & 0b11000000 == 0b11000000:
                additional = additional + " "
            additional = additional + "{0:#0{1}x}".format(b,4)[2:]
        additional = additional + "  " + readhex(1)[0]
        return additional, "string"

    def readhex_s(head):
        additional, i = readhex_i(head)
        return readhex_si(additional, head, i)

    slen = 50
    def write_line(head, annotation="", additional="", additional_bytes=0):
        if additional_bytes:
            additional = additional + " " + readhex(additional_bytes)[0]
        if annotation:
            annotation = ' | ' + annotation
        annotation = ""
        hex_part = indent + "{0:#0{1}x}".format(head,4) + additional
        f.write((hex_part.ljust(slen) + annotation).rstrip() + "\n")

    while True:
        head = stream.read(1)
        if len(head) == 0:
            return True
        head = head[0]
        if   head == 0xF0:
            write_line(head, 'null')
        elif head == 0xF1:
            write_line(head, 'false')
        elif head == 0xF2:
            write_line(head, 'true')
        elif head == 0xF3:
            write_line(head, '')
            indent = indent + '    '
            while True:
                head = stream.read(1)
                if not head:
                    return True
                head = head[0]
                if head == 0xF5:
                    break
                elif head < 128:
                    write_line(head, 'key from table[' + str(head) + ']')
                elif head & 0xF0 == 0xA0:
                    additional, s = readhex_s(head)
                    write_line(head, s, additional=" " + additional)
                else:
                    write_line(head, '?')
                if not dump_pretty(stream, f, indent):
                    break
            indent = indent[:-4]
            write_line(0xF5, '')
        elif head == 0xF4:
            write_line(head, '')
            while dump_pretty(stream, f, indent + "    "):
                pass
            write_line(0xF5, '')
        elif head == 0xF5: # end of array or object
            return False
        elif head == 0xF6:
            write_line(head, '0.0')
        elif head == 0xF7:
            write_line(head, 'float32', additional_bytes=4)
        elif head == 0xF8:
            write_line(head, 'float64', additional_bytes=8)
        elif head == 0xF9:
            write_line(head, 'BigFloat (not implemented yet)')
        elif 0x80 <= head <= 0xBF:
            i = 0
            additional = ""
            if head & 0x0F == 10:
                additional, i = readhex(1)
            elif head & 0x0F == 11:
                additional, i = readhex(2)
            elif head & 0x0F == 12:
                additional, i = readhex(4)
            elif head & 0x0F == 13:
                additional, i = readhex(8)
            elif head & 0x0F == 14:
                pass # TODO BigInt
            elif head & 0x0F == 15:
                i = -1
            else:
                i = head & 0x0F

            if head & 0xF0 == 0x80:
                write_line(head, str(i), additional=" " + additional)
            elif head & 0xF0 == 0x90:
                additional = additional + " " + readhex(i)[0]
                write_line(head, 'BLOB', additional=" " + additional)
            elif head & 0xF0 == 0xA0:
                additional, s = readhex_si("", head, i)
                write_line(head, s, additional=" " + additional)
            elif head & 0xF0 == 0xB0:
                additional += (readhex(i)[0] + " " +  # string content
                               readhex(1)[0] + " " +  # null termination
                               readhex(1)[0])         # index
                write_line(head, 'put string to table', additional=" " + additional)
        else:
            write_line(head, '?')
    return True

def example(name, value, keys=None, meaning=None, protobuf=False, packed_JSON=False):
    """Generates a new example."""

    jxon_value = jxon.encode(value, keys_table=keys)
    with open(os.path.join(EXAMPLES_PREFIX, name + '.jxon'), 'wb') as f:
        f.write(jxon_value)
    if packed_JSON:
        json_value = json.dumps(value, separators=(',', ':'), cls=JSONExtendedEncoder)
    else:
        json_value = json.dumps(value, indent=4, cls=JSONExtendedEncoder)
    with open(os.path.join(EXAMPLES_PREFIX, name + '.json'), 'w', encoding='utf-8') as f:
        f.write(json_value)
    with open(os.path.join(EXAMPLES_PREFIX, name + '.txt'), 'w', encoding='utf-8') as f:
        jxon_stream = io.BytesIO(jxon_value)
        dump_pretty(jxon_stream, f)
        jxon_stream.close()
    if meaning is None:
        meaning = '`' + json.dumps(value, cls=JSONExtendedEncoder) + '`'
    protobuf_file = ""
    if protobuf:
        import movies_pb2
        import google.protobuf.json_format
        message = google.protobuf.json_format.ParseDict(value, movies_pb2.MoviesDataset())
        protobuf_file = name + '.pb'
        with open(os.path.join(EXAMPLES_PREFIX, protobuf_file), 'wb') as f:
            f.write(message.SerializeToString(deterministic=True))
    readme.add_example(name, jxon_value, meaning, protobuf=protobuf_file)

def example_s(name, s, addition=""):
    """Generates a new example for the specified string s."""

    example(name, s, meaning='`"' + s + '"`' + addition)

def example_b(name, b):
    """Generates a new example for the specified BLOB b."""

    example(name, b, meaning='`' + hexdump(b, 20) + '`')

def example_f(name, f, meaning=None):
    """Generates a new example for the specified float f."""

    if (meaning is None) and isinstance(f, str):
        meaning = f
        f = float(f)
    elif (meaning is None) and isinstance(f, numbers.Rational):
        meaning = str(f.numerator) + '/' + str(f.denominator)
    example(name, f, meaning=meaning)

def example_movies():
    """Generates movies dataset."""

    z = 20170705
    a = 742938285
    e = 31
    m = 2**e -1
    def rand():
        nonlocal z
        z = (z + a) % m
        return z

    def randChoice(l):
        return l[rand() % len(l)]

    def randomMovieId():
        id = "MOVUID-"
        for i in range(20):
            id = id + str(rand() % 10)
        return id

    def randomTitle():
        adj = ['Happy','Dirty','Terrible','Red','Blue','Orange']
        noun = ['Ball','Cube','Dell','Cognition','Redemption','Event','Tooth']
        pre = ['of','in','out of','under','over','inside']
        place = ['the House','the World','Deep Space','Abyss','the Mind']
        title = ""
        if rand() % 100 < 50:
            title = title + 'The '
        if rand() % 100 < 70:
            title = title + randChoice(adj) + ' '
        title = title + randChoice(noun) + ' '
        if rand() % 100 < 70:
            title = title + randChoice(pre) + ' '
            title = title + randChoice(place) + ' '
        return title

    def randomDirector():
        name = ['Liam','Noah','William','James','Oliver','Benjamin','Elijah','Lucas','Logan',
                'Emma','Olivia','Ava','Isabella','Sophia','Charlotte','Mia','Amelia','Harper','Evelyn']
        surname = ['Chronenberg']
        director = randChoice(name)
        if rand() % 1000 < 10:
            director = director + ' ' + randChoice(['L','C','K','M','N']) + '.'
        director = director + ' ' + randChoice(surname)
        if rand() % 100 < 10:
            director = director + ' Jr.'
        return director

    movies = []
    while len(movies) < 1000:
        genres = ['comedy']
        movies.append({'id': randomMovieId(),
                       'year': 1900 + rand() % 200,
                       'title': randomTitle(),
                       'director': randomDirector(),
                       'genres': genres})

    movies.sort(key = lambda movie: movie['year'])

    example('movies', {"movies": movies},
            meaning='List of randomly generated movies')
    example('movies_compressed', {"movies": movies},
            keys=['id', 'title', 'year', 'director', 'genres'],
            meaning='The same list, but keys table is used',
            protobuf=True,
            packed_JSON=True)


def generate_examples():
    """Generates examples in ../examples directory.

       Requires protobuf sources to be generated.
    """

    generate_examples()
    readme.start()

    readme.start_chapter('Simple values')
    example("null", None)
    example('false', False)
    example('true', True)
    example('zero', 0)

    readme.start_chapter('Integers')
    for i in range(0, 12):
        example(f'int_{i}', i)
    for i in range(1, 3):
        example(f'int_neg_{i}', -i)
    example('int_min8',   -128)
    example('int_max8',    127)
    example('int_min16',  -32768)
    example('int_max16',   32767)
    example('int_min32',  -2147483648)
    example('int_max32',   2147483647)
    example('int_min64',  -9_223_372_036_854_775_808)
    example('int_max64',   9_223_372_036_854_775_807)

    readme.start_chapter('Strings and BLOBs')
    example_s('str_empty', '')
    example_s('str_hello', 'Hello!')
    example_s('str_hello_chinese', '你好', addition=" (notice that 6 in `A6` means number of **bytes**, not **characters**)")
    example_b('blob_empty', bytes())
    example_b('blob_0123', bytes([0, 1, 2, 3]))

    readme.start_chapter('Floats')
    example_f('float_0', 0.0)
    example_f('float_1', 1.0)
    example_f('float_nan', "NaN")
    example_f('float_neg_nan', "-NaN")
    example_f('float_inf', "Infinity")
    example_f('float_neg_inf', "-Infinity")
    example_f('float_nan', "NaN")
    example_f('float_half', fractions.Fraction(1, 2))
    example_f('float_minnorm32', fractions.Fraction(1, 2**126), meaning="`2^-126` (minimal normalized float)")
    # example_f('float_maxdenorm32', fractions.Fraction(1, 2**126 - 2*123))
    # example_f('float_max32', fractions.Fraction(2**128 - 2**104, 1))
    example_f('float_minnorm64', fractions.Fraction(1, 2**1022), meaning="`2^-1022` (minimal normalized double)")

    readme.start_chapter('Structured values')
    example('object_empty', {})
    example('object', {"key1": 1, "key2": "string"})
    example('array_empty',  [])
    example('array_123',  [1, 2, 3])

    readme.start_chapter('Datasets')
    example_movies()

    readme.end()


if __name__ == "__main__" :
    subprogram = sys.argv[1]

    if subprogram == "generate_examples":
        generate_examples()
        sys.exit()

    print("Unknown subprogram ", subprogram)
