
## 3D Renderer Project Ideas

These projects build on the 3D renderer, encouraging you to explore its mathematics, improve its features, or
experiment with alternative algorithms. Each project includes objectives and challenges to guide your learning.


### Project 1: Fix and Enhance the Reflection Model

The reflection in the original renderer is incorrect or incomplete. Your task is to implement a proper reflection
model using recursive ray tracing.


#### Objectives

- Understand the mathematics of ray reflection using the reflection formula:  
  `R = I - 2 * (N · I) * N`, where `I` is the incident ray direction and `N` is the surface normal.
- Implement recursive ray tracing to compute reflections up to a specified depth (e.g., 2 bounces).
- Add a reflectivity parameter to control the strength of reflections on the sphere and plane.
- Test with a mirror-like surface on the plane to reflect the sphere.

#### Challenges

- Optimise recursion to avoid excessive computation (e.g., limit ray depth).
- Handle edge cases, such as total internal reflection or grazing angles.
- Experiment with combining reflections with Phong shading for realistic materials.

#### Potential Enhancements

- Add environment mapping for reflective surfaces using a skybox texture.
- Explore glossy reflections by adding noise to the reflection direction.


### Project 2: Substitute Lambertian with Oren-Nayar Shading

Replace the Lambertian shading model with the Oren-Nayar model, which accounts for surface roughness and provides more
realistic diffuse shading for rough surfaces like the plane.


#### Objectives

- Study the Oren-Nayar model, which modifies diffuse shading based on surface roughness:  
  `L = cos(θ_i) * (A + B * max(0, cos(φ_i - φ_r)) * sin(α) * tan(β))`,  
  where `A` and `B` are roughness-dependent terms, and `θ_i`, `φ_i`, `φ_r`, `α`, `β` are angles between light, viewer, and normal.
- Implement the model in the shader code for the plane and sphere.
- Add a roughness parameter to control the effect (0 for Lambertian, 1 for fully rough).

#### Challenges

- Derive and compute the trigonometric terms efficiently in JavaScript.
- Compare visual results with Lambertian shading to understand the impact.
- Optimise performance, as Oren-Nayar is computationally heavier.

#### Potential Enhancements

- Apply different roughness values to the sphere and plane for varied materials.
- Combine with texture mapping to simulate realistic surfaces like stone or wood.


### Project 3: Implement Soft Shadows

The current renderer uses hard shadows. Modify it to support soft shadows by simulating an area light source.

### Objectives

- Research area lighting and soft shadow techniques, such as sampling multiple points on a light source disk.
- Modify the shadow ray function to sample multiple points (e.g., 4–16 samples) on a square or circular light source.
- Compute soft shadows by averaging occlusion results:  
  `shadowFactor = (number of unoccluded samples) / (total samples)`.
- Update the lighting calculation to incorporate the shadow factor.

#### Challenges

- Balance sample count with performance to maintain real-time rendering.
- Handle edge cases where samples partially intersect objects.
- Ensure consistent shadow softness across different scene distances.

#### Potential Enhancements

- Add a user-controlled light size parameter to adjust shadow softness.
- Experiment with stratified sampling or jittering to reduce noise.


### Project 4: Add Triangle Mesh Support

Extend the renderer to support triangle meshes instead of just spheres and planes, allowing you to render complex 3D models.

#### Objectives

- Learn the mathematics of ray-triangle intersection using the Möller-Trumbore algorithm:  
  `t = (Q - O) · (N × D) / (D · (P1 - P0) × (P2 - P0))`,  
  where `O` is the ray origin, `D` is the ray direction, `P0, P1, P2` are triangle vertices, and `Q` is a point on the plane.
- Implement a data structure to store triangle meshes (e.g., vertex and index arrays).
- Modify the ray intersection code to test against triangles in addition to spheres and planes.
- Load a simple mesh (e.g., a cube or low-polygon model) from a file (e.g., OBJ format).

#### Challenges

- Optimise ray-triangle intersection for performance using bounding volumes (e.g., AABB).
- Handle texture coordinates and normals for triangles.
- Parse and render a user-uploaded OBJ file correctly.

#### Potential Enhancements

- Add support for normal interpolation for smooth shading.
- Implement a simple bounding volume hierarchy (BVH) to accelerate ray intersections.


### Project 5: Replace Raycasting with Path Tracing

Convert the renderer from raycasting to a basic path tracer for more realistic global illumination.

#### Objectives

- Study path tracing principles, including Monte Carlo integration and BRDFs (Bidirectional Reflectance Distribution Functions).
- Replace the single-ray-per-pixel approach with multiple rays that scatter randomly based on material properties.
- Implement a simple diffuse BRDF:  
  `f_r = albedo / π`, with random hemispherical scattering.
- Accumulate light contributions over multiple samples per pixel for convergence.

#### Challenges

- Manage performance, as path tracing is computationally intensive.
- Implement importance sampling to reduce noise in the output.
- Handle termination of ray paths (e.g., using Russian roulette).

#### Potential Enhancements
- Add support for emissive materials to create glowing objects.
- Experiment with different BRDFs, such as glossy or metallic surfaces.


### Project 6: Add Camera Controls

Enhance user interaction by adding camera controls (e.g., orbit, zoom, pan) using mouse or keyboard input.

#### Objectives

- Implement an orbital camera model using spherical coordinates:  
  `cameraPos = [r * sin(θ) * cos(φ), r * cos(θ), r * sin(θ) * sin(φ)]`,  
  where `r` is the radius, `θ` is the polar angle, and `φ` is the azimuthal angle.
- Add mouse event listeners for dragging (to update `θ` and `φ`) and scrolling (to update `r`).
- Update the ray origin and direction based on the new camera position and orientation.

#### Challenges

- Ensure smooth and intuitive camera movement without jittering.
- Handle edge cases, such as preventing the camera from passing through objects.
- Maintain correct field of view and aspect ratio during updates.

#### Potential Enhancements

- Add keyboard controls for WASD movement or arrow keys.
- Implement a look-at system to focus the camera on the sphere.


### Getting Started

For each project, start with the code of one version of the renderer. Test incrementally to ensure each change works
before moving to the next. Use the provided code snippets (e.g., ray-sphere intersection, Phong shading) as a foundation.

- Use `console.log` or a debug canvas to visualise intermediate results (e.g., normals, UV coordinates).
- Compare your results with reference images or existing renderers to validate correctness.
- Experiment with parameters (e.g., light position, material properties) to understand their impact.

These projects will deepen your understanding of 3D rendering, from mathematical foundations to practical implementation.

