.PHONY: all clean run

all: b8 tiger thumb

b8:
	python3 svg.py b8.svg b8.png 400 400

tiger:
	python3 svg.py tiger.svg tiger.png 600 600

thumb:
	python3 svg.py thumb.svg thumb.png 800 800

clean:
	rm -rf __pycache__

run: all clean
