#!/usr/bin/env python3
# Convert simple SVG <path> to C path array

import sys
import re
from xml.etree import ElementTree as ET

SVG_NS = '{http://www.w3.org/2000/svg}'

 
# Yield (cmd, (x,y)) tuples from SVG path data
def parse_path(d):
    tokens = re.split(r'[\s,]+', d.strip())
    i = 0
    cmd = None
    rel = False
    cur_x = cur_y = 0.0

    while i < len(tokens):
        t = tokens[i]
        if t and t[0].isalpha():
            cmd = t.upper()
            rel = t.islower()
            i += 1
        else:
            cmd = cmd or 'L'  # implicit line-to after move

        if cmd == 'M':
            x = float(tokens[i]);   i += 1
            y = float(tokens[i]);   i += 1
            cur_x = x + cur_x if rel else x
            cur_y = y + cur_y if rel else y
            yield ('M', (cur_x, cur_y))
        elif cmd == 'L':
            x = float(tokens[i]);   i += 1
            y = float(tokens[i]);   i += 1
            cur_x = x + cur_x if rel else x
            cur_y = y + cur_y if rel else y
            yield ('L', (cur_x, cur_y))
        elif cmd == 'Z':
            yield ('Z', None)
            i += 1
        else:
            # skip unsupported commands (C, Q, etc.)
            i += 1
    yield ('E', None)   # end marker

def svg_bounds(tree):
    root = tree.getroot()
    w = float(root.get('width', '320').replace('px',''))
    h = float(root.get('height','240').replace('px',''))
    return w, h

def main():
    if len(sys.argv) != 3:
        print("Usage: svg2path.py <file.svg> <SYMBOL_NAME>", file=sys.stderr)
        sys.exit(1)

    svg_file, sym = sys.argv[1], sys.argv[2]
    tree = ET.parse(svg_file)
    w, h = svg_bounds(tree)

    print(f"/* Auto-generated from {svg_file} */")
    print(f"#ifndef {sym.upper()}_PATH_H")
    print(f"#define {sym.upper()}_PATH_H\n")
    print("#include \"display.h\"")
    print(f"static const path_entry_t {sym}_path[] = {{")
    print(f"    /* viewBox 0 0 {w} {h} */")

    for path in tree.iter(SVG_NS + 'path'):
        d = path.get('d')
        if not d: continue
        points = list(parse_path(d))
        first = True
        for cmd, pt in points:
            if cmd == 'M':
                if not first: print("    {PATH_CLOSE,{0,0}},")
                x = int(pt[0] * 256)   # 8.8 fixed point
                y = int(pt[1] * 256)
                print(f"    {{PATH_MOVE, {{.x = {x}, .y = {y}}}}},")
                first = False
            elif cmd == 'L':
                x = int(pt[0] * 256)
                y = int(pt[1] * 256)
                print(f"    {{PATH_LINE, {{.x = {x}, .y = {y}}}}},")
            elif cmd == 'Z':
                print("    {PATH_CLOSE,{0,0}},")
            elif cmd == 'E':
                break
    print("    {PATH_END,{0,0}}")
    print("};\n#endif")

if __name__ == '__main__':
    main()
