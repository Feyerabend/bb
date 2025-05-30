
## 3D Graphics: An Introduction

### Cube: Basic Graphics Examples

This [cube](./cube/) folder introduces fundamental *3D graphics* concepts by rendering and
manipulating a simple *cube* on a 2D screen using mathematical operations. The core process
involves taking 3D data (vertices) and transforming it into 2D coordinates for drawing.

The examples demonstrate key concepts incrementally:
- *Coordinate Systems:* Defining points in 3D space (x, y, z).
- *Vertices, Edges, Faces:* The building blocks defining the object's shape.
- *Transformations:* Moving, rotating (using rotation matrices), and resising
  objects in 3D space. Matrix-vector multiplication is the core operation for
  applying transformations.
- *Projection:* Converting 3D points to 2D points on the screen to create the
  illusion of depth (perspective projection).
- *Rendering Order (Painter's Algorithm):* Sorting and drawing faces from furthest
  to closest to ensure correct occlusion of solid objects.
- *Normal Vectors:* Vectors perpendicular to a surface, used for determining face
  orientation and lighting.
- *Vector Math Utilities:* Functions for vector operations like subtraction, cross
  product (finding normals), dot product (lighting, culling, alignment), and normalisation.
  The *dot product* is highlighted for lighting and culling, while the *cross product*
  is used for finding normal vectors.
- *Lighting Models:* Specifically *Lambertian lighting*, where brightness depends on the
  angle between the surface normal and the light direction.
- *Shadows:* Creating a simple planar shadow by projecting vertices onto a plane.
- *Reflections:* Simulating reflections by creating and drawing a mirrored version of the object.
- *Animation:* Using `requestAnimationFrame` for auto-rotation.
- *User Interaction:* Allowing user control of rotation via mouse dragging.
- *Back-Face Culling:* Not drawing faces that are pointing away from the camera to save rendering time.

The series progresses from a static wireframe cube (01.html) to auto-rotation (02.html - Auto),
user-rotation (02.html - User), a solid filled cube with depth sorting (03.html), a lit cube
with culling and shadows (04.html), and finally a reflective cube (05.html). It serves as a
hands-on introduction to how linear algebra and geometry create visual effects in 3D graphics.


### Balls: Raytracing Examples

This folder [balls](./balls/) introduces *3D rendering*, specifically the technique of *raytracing*,
through a series of simple web examples. Raytracing simulates the path of light, working backward
from the camera. For each pixel on the screen, a ray is cast from the camera into the 3D scene.
The color of the pixel is determined by the first object the ray intersects, considering
lighting, shading, and shadows at that intersection point. This method often results in
very realistic images.

The examples demonstrate core 3D concepts incrementally:
- *Vectors and Basic Math:* Essential for positions, directions, and operations like dot products.
- *Scene Setup:* Defining the camera (position, FOV), objects (Spheres, Planes), and light source.
- *Ray-Object Intersection:* Calculating where a ray hits objects, often involving solving
  mathematical equations.
- *Lighting Models:* Including diffuse (Lambertian) and ambient light, and shadows.
- *Animation:* Updating object properties over time using `requestAnimationFrame`.
- *Textures:* Applying images to surfaces.
- *Reflection:* Simulating light bouncing off surfaces (the examples include a faulty reflection
  implementation to be fixed).
- *Multithreading:* Using Web Workers to improve performance for complex scenes.

The series evolves from a basic static sphere/plane with shadows (01.html) to animated color
(02.html), bouncing (03.html), textures (04.html, 05.html), reflection (06.html), and multithreading
(07.html) (plus a multi-sphere scene: five.html). It provides a practical, step-by-step understanding
of raytracing.


### Commonalities and Differences

Both folders share several fundamental concepts and approaches to teaching 3D graphics:

- *Core Goal:* Both aim to explain how *3D data is converted into a 2D image* on a screen.
- *Use of Math:* Both heavily rely on *mathematical concepts*, particularly *vector math*
  and operations like the *dot product*, which are crucial for understanding positions,
  directions, lighting, and geometry.
- *Object Representation:* Both define objects within a *virtual 3D space*.
- *Lighting and Shadows:* Both cover *lighting models* (specifically mentioning Lambertian/diffuse lighting)
  and the creation of *shadows* to enhance realism.
- *Animation:* Both introduce *animation* using the `requestAnimationFrame` browser API.
- *Textures:* Both discuss the application of *textures* (images) to surfaces for added
  detail and realism.
- *Reflection:* Both address the concept of *reflection*.

Despite the common ground, the documents focus on different *3D rendering techniques* and
highlight different aspects of the graphics pipeline:

- *Primary Rendering Technique:*
    - Balls focuses specifically on *Raytracing*, a technique that traces the path of light
      rays from the camera to the scene.
    - Cube focuses on a more traditional *polygon-based rendering* approach, transforming
      and drawing the faces of objects.

- *Handling Visibility and Occlusion:*
    - Raytracing inherently handles visibility and occlusion by finding the *first* object
      a ray intersects.
    - Polygon Rendering requires specific algorithms like the *Painter's Algorithm (Depth Sorting)*
      to draw faces in the correct order (furthest to closest) and *Back-Face Culling* to
      avoid drawing hidden faces.

- *Approach to Object Geometry:*
    - Raytracing often relies on *mathematical descriptions* of objects (like the quadratic
      equation for spheres) and calculates ray intersections with these forms.
    - Polygon Rendering defines objects using explicit lists of *vertices, edges, and faces*.

- *Emphasis on Transformations:*
    - Cube places a strong emphasis on *geometric transformations* (like rotation) applied
      via *matrix multiplications* to vertices.
    - Balls focuses more on how rays interact with objects and calculating properties at the
      intersection point, with transformations being less central to the core ray-intersection
      logic presented.

- *Specific Math Highlighted:*
    - Balls highlights vector math and solving equations for *ray-object intersection* (e.g.,
      quadratic formula for spheres).
    - Cubs highlights *matrix math for transformations* (rotation matrices, matrix-vector
      multiplication) and using vector operations (cross product) to find *normal vectors*.

- *Performance Optimization:*
    - Balls explicitly introduces *multithreading (Web Workers)* as a way to improve raytracing
      performance, especially for complex scenes.
    - Cube mentions performance savings through Back-Face Culling but does not introduce multithreading.

- *Interaction Features:*
    - Balls mentions user interaction primarily in the context of *loading textures*.
    - Cube includes *user interaction* for controlling the cube's rotation via mouse dragging.


### WebGL and the file format OBJ

The third folder [WebGL](./webgl/) focuses on *WebGL* and the *OBJ file format*.

   *WebGL as a Rendering API:* This folder explains that WebGL is a *JavaScript API* for rendering
   *hardware-accelerated 2D and 3D graphics* directly in web browsers. It's built on OpenGL ES and
   requires using *GLSL shaders*. While the first two folders manually calculate aspects like ray
   intersections, transformations, projections, lighting, and shadows in JavaScript, WebGL provides
   a framework that leverages the GPU for much of this work. This suggests a move from a purely CPU-based,
   manual approach to one that utilises specialised hardware for potentially much higher performance,
   especially for complex scenes.

   *OBJ for Model Data:* The document introduces the *OBJ file format* as a standard, text-based way
   to define and store 3D geometry, including *vertices, texture coordinates, normals, and polygonal faces*.
   This differs from the first two folders, where the geometry (e.g., sphere parameters, cube vertices
   and faces) is defined directly within the JavaScript code. Using OBJ allows for loading pre-existing
   3D models rather than hardcoding simple shapes.

   *Different Learning Approach:* We suggests that exploring WebGL and OBJ files can offer a
   *top-down approach* to understanding 3D rendering, contrasting with the *bottom-up* method of
   building everything from scratch shown in the first two folders. It implies that this top-down
   method can help you quickly gain insight and build a foundation. The first two folders, conversely,
   meticulously build complexity from basic elements like vectors, scene setup, and fundamental algorithms.

   *Requirements and Limitations:* We also notes that *not all browsers implement WebGL*, highlighting
   a potential dependency issue that the pure JavaScript examples in the first two folders do not have.
   Learning WebGL also requires understanding concepts like shaders, which adds a new layer of complexity
   beyond the mathematics used in the first two documents.


### Build Your Own 3D Engine

Students find it interesting to building their own 3D engine in C (often intended for games) to learn concepts.
This folder [simple](./simple/) will only begin with one way to do that.

