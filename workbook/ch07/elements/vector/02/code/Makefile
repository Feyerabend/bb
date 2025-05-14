
.PHONY: all clean run iclean

all: help b8 tiger thumb


help:
	python3 svg.py --help

b8:
	python3 svg.py b8.svg b8.png --width 400 --height 400

tiger:
	python3 svg.py tiger.svg tiger.png --width 600 --height 600

thumb:
	python3 svg.py thumb.svg thumb.png --width 800 --height 800 --clear-intermediate False

clean:
	rm -rf __pycache__

iclean:
	rm b8.png
	rm tiger.png
	rm thumb.png

run: iclean all clean
