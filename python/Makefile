default : test;

PROTOC:=protoc
PYTHON:=py
PROTOBUF_PYTHON_SOURCES:=movies_pb2.py

test :
	$(PYTHON) jxon-cl.py

$(PROTOBUF_PYTHON_SOURCES) : ../protobuf/movies.proto
	$(PROTOC) -I../protobuf --python_out=. movies.proto

examples : $(PROTOBUF_PYTHON_SOURCES)
	$(PYTHON) jxon-cl.py generate_examples
