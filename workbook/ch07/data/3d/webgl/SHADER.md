
## What is a Shader?

A shader is a small, specialised program that runs on the GPU (Graphics Processing Unit). It controls how 3D objects are
drawn--including how their surfaces appear, how they are lit, colored, textured, and transformed into the final 2D image
seen on the screen. For a simplified comparison between traditional and shader rendering, see [shaders](./shaders/).

In essence:
> A shader defines how pixels and vertices look on the screen.


### What Are Shaders Used For?

Shaders are used for:
- Lighting: simulate light interaction (diffuse, specular, shadows)
- Material effects: metal, glass, water, plastic, skin, etc.
- Textures: apply images to surfaces (e.g. brick texture on a wall)
- Animation: move or deform geometry (e.g. waving flags, morphing shapes)
- Post-processing: color grading, blur, bloom, outlines, screen effects
- Procedural generation: generate patterns, noise, terrain, etc.


### Main Types of Shaders

In modern 3D graphics (e.g. OpenGL, Vulkan, Direct3D, WebGL), the most common shader stages are:

1. Vertex Shader
- Input: vertex attributes (position, normal, UV coordinates)
- Output: transformed position in screen space
- Purpose: transform vertices using projection/view/model matrices
- Optional: pass data to the next stage (e.g., normals, colors)

2. Fragment Shader (aka Pixel Shader)
- Input: data from the rasterizer (interpolated from vertices)
- Output: final color of a pixel
- Purpose: compute lighting, apply textures, effects, etc.

3. Optional Shader Stages (in advanced pipelines)
- Geometry Shader: modifies geometry, can create new vertices
- Tessellation Shaders: add surface detail
- Compute Shader: general-purpose GPU programming (GPGPU)
- Mesh Shaders: newer GPU stage (replaces vertex/geometry in some systems)


### How Shaders Work

High-Level Flow:
1. 3D model data (vertices) is sent to the GPU
2. The vertex shader transforms these vertices into screen coordinates
3. The rasterizer converts triangles into fragments (potential pixels)
4. The fragment shader colors each pixel, considering lights/textures
5. Final pixel colors are written to the screen

Example: Simplified GLSL Vertex Shader
```
#version 300 es
in vec3 aPosition;
uniform mat4 uModelViewProjection;
void main() {
  gl_Position = uModelViewProjection * vec4(aPosition, 1.0);
}
```
Example: Fragment Shader
```
#version 300 es
precision mediump float;
out vec4 fragColor;
void main() {
  fragColor = vec4(1.0, 0.0, 0.0, 1.0); // red
}
```

### Where Are Shaders Used?

Shaders are everywhere in modern 3D rendering:
- Video Games (Unity, Unreal, Godot, etc.)
- 3D Modeling Software (Blender, Maya, 3ds Max)
- WebGL for 3D in browsers (e.g., Three.js)
- Scientific Visualization
- CAD Systems
- Augmented/Virtual Reality
- Special Effects in Films

Even mobile apps using Metal (Apple), Vulkan, or OpenGL ES on phones use shaders.


### How Are Shaders Related to Hardware?

- Executed on the GPU, which is highly parallel (good for thousands of pixels)
- Shader cores (sometimes called CUDA cores or stream processors) run these tiny programs per vertex or per pixel
- Shaders must be written in GPU-compatible languages:
- GLSL (OpenGL Shading Language)
- HLSL (High-Level Shading Language, Direct3D)
- Metal Shading Language (Apple)
- SPIR-V (intermediate representation for Vulkan)

Modern GPUs are shader-centric, meaning the whole rendering pipeline is built around programmable
stages rather than fixed-function pipelines.


### Summary Table

|Feature           | Vertex Shader     | Fragment Shader      | Other|
|------------------|-------------------|----------------------|-------------------------|
|Runs on           | GPU (per vertex)  | GPU (per pixel)      | Geometry, Compute, etc.|
|Purpose           | Transform geometry| Compute color        | Effects, deformation, etc.|
|Written in        | GLSL, HLSL, etc.  | GLSL, HLSL, etc.     | Same|
|Typical Output    | Position          | Color                | Varies|
|Controls          | Geometry placement| Pixel appearance     | Special effects, logic|


### Reference

- https://www.lighthouse3d.com/tutorials/glsl-tutorial/
