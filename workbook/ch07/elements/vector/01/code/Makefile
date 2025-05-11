.PHONY: all clean run_and_clean

all: b8 tiger

b8:
	python3 svg.py b8.svg b8.png 400 400

tiger:
	python3 svg.py tiger.svg tiger.png 600 600

# warning: this may take a long time!
thumb:
	python3 svg.py thumb.svg thumb.png 500 500

clean:
	rm -rf __pycache__

run: all clean
