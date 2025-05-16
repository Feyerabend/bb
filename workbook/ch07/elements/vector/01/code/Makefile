.PHONY: all clean run iclean

all: b8 clinton tiger thumb golfer picasso

b8:
	python3 svg.py b8.svg b8.png --width 400 --height 400

clinton:
	python3 svg.py clinton.svg clinton.png 400 400

tiger:
	python3 svg.py tiger.svg tiger.png 600 600

thumb:
	python3 svg.py thumb.svg thumb.png 800 800

picasso:
	python3 svg.py picasso.svg picasso.png 800 800

clean:
	rm -rf __pycache__

iclean:
	rm b8.png
	rm tiger.png
	rm thumb.png
	rm golfer.png
	rm picasso.png

run: iclean all clean
