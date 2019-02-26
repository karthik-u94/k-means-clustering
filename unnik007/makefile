PYTHON = python
clean-pyc:
	find . -name '*.pyc' -exec rm --force {}

.PHONY:
	clean-pyc

preprocess :
	python3 preprocess.py ./reuters21578

JFLAGS = -g
JC = javac
.SUFFIXES: .java .class
.java.class:
	$(JC) $(JFLAGS) $*.java

CLASSES = kcluster.java

kcluster: classes

classes: $(CLASSES:.java=.class)

clean: $(RM) kcluster.class
