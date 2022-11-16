default : test;

PROTOC:=protoc
PYTHON:=py
PROTOBUF_PYTHON_SOURCES:=movies_pb2.py
PYTEST:=pytest

test :
	$(PYTEST)

$(PROTOBUF_PYTHON_SOURCES) : ../protobuf/movies.proto
	$(PROTOC) -I../protobuf --python_out=. movies.proto

examples : $(PROTOBUF_PYTHON_SOURCES)
	$(PYTHON) jxon-cl.py generate_examples
