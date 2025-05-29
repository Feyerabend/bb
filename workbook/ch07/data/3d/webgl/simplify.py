# This script simplifies a 3D model in OBJ format by merging close
# vertices and removing degenerate or duplicate faces.
# e.g. aeroplane.obj -> aeroplane2.obj (look at the size)

import sys
import math

def load_obj(filename):
    vertices = []
    faces = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.strip().split()
                vertex = tuple(float(p) for p in parts[1:4])
                vertices.append(vertex)
            elif line.startswith('f '):
                parts = line.strip().split()
                face = [int(part.split('/')[0]) - 1 for part in parts[1:]]
                faces.append(face)
    return vertices, faces

def distance(v1, v2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

def merge_vertices(vertices, epsilon=1e-5):
    unique = []
    mapping = {}
    for i, v in enumerate(vertices):
        found = False
        for j, u in enumerate(unique):
            if distance(v, u) < epsilon:
                mapping[i] = j
                found = True
                break
        if not found:
            mapping[i] = len(unique)
            unique.append(v)
    return unique, mapping

def remap_faces(faces, mapping):
    new_faces = []
    seen = set()
    for face in faces:
        new_face = tuple(mapping[idx] for idx in face)
        if len(set(new_face)) < 3:
            continue  # degenerate face
        if new_face in seen:
            continue  # duplicate face
        seen.add(new_face)
        new_faces.append(new_face)
    return new_faces

def write_obj(filename, vertices, faces):
    with open(filename, 'w') as f:
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            indices = ' '.join(str(idx + 1) for idx in face)
            f.write(f"f {indices}\n")

def simplify_obj(input_file, output_file, epsilon=1e-5):
    vertices, faces = load_obj(input_file)
    new_vertices, mapping = merge_vertices(vertices, epsilon)
    new_faces = remap_faces(faces, mapping)
    write_obj(output_file, new_vertices, new_faces)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python simplify.py input.obj output.obj [epsilon]")
    else:
        epsilon = float(sys.argv[3]) if len(sys.argv) > 3 else 1e-5
        simplify_obj(sys.argv[1], sys.argv[2], epsilon)
