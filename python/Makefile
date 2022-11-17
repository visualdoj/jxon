default : test;

PROTOC?=protoc
PYTHON?=python
PYTEST?=pytest
PYLINT?=pylint

PROTOBUF_PYTHON_SOURCES:=movies_pb2.py

test :
	$(PYTEST)

lint :
	$(PYLINT) --good-names allow_JSON,i,s,f \
		      --max-returns 20 \
			  --max-branches 20 \
			  --max-statements 100 \
			  --max-locals 20 \
			  jxon.py
	$(PYLINT) --good-names invalid_JXON,f \
		      --disable use-dict-literal \
              jxon_test.py

$(PROTOBUF_PYTHON_SOURCES) : ../protobuf/movies.proto
	$(PROTOC) -I../protobuf --python_out=. movies.proto

examples : $(PROTOBUF_PYTHON_SOURCES)
	$(PYTHON) jxon-cl.py generate_examples
