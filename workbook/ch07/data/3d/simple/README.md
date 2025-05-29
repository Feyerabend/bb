
## Project: Develop Your Own 3D Engine in C

Many students in game development are drawn to learning C and C++ because these languages sit at the
heart of the game industry's technical foundation. A major reason is the sheer abundance of mature
libraries and engines--such as SDL, OpenGL, DirectX, Vulkan, Bullet Physics, and Unreal Engine--that
are either written in or provide first-class support for C and C++. This ecosystem gives learners
direct access to powerful, low-level tools for graphics, physics, input handling, audio, and networking.

Moreover, decades of accumulated knowledge about 3D rendering, real-time simulation, performance optimisation,
and memory management have been codified in the C/C++ programming culture. Many of the classic texts,
tutorials, and research papers in graphics and game development assume familiarity with these languages.
As a result, learning C/C++ gives students a gateway into this deep and well-documented tradition, which
can be invaluable for understanding how things really work under the hood—and for writing high-performance,
platform-level code where efficiency and control are critical.

In short, C and C++ offer not just tools but direct access to the accumulated technical wisdom of the
game development field.

Many also want to develop their own 3D engine for making games. Here the project can be structured as follows:

1. Set Up a Basic Rendering Pipeline
Begin with a minimal application using OpenGL or SDL to create a window and draw simple shapes. Learn how
to clear the screen, handle buffers, and draw colored triangles. This step introduces the fundamental flow
of a real-time rendering loop: *input → update → render*.

2. Implement a Math Library
To manipulate 3D geometry, you'll need basic linear algebra: vectors, matrices, dot and cross products,
transformations, and projections. Rather than relying on external libraries, implementing your own helps
solidify the mathematical concepts that underpin 3D engines.

3. Define and Load 3D Models
Add support for reading simple 3D model formats, such as OBJ. Learn to parse vertex positions, texture
coordinates, and normals. Display wireframes or flat-shaded models to validate your pipeline.

4. Build a Camera System
Introduce a movable camera with position, direction, and perspective projection. Implement user-controlled
movement (e.g. WASD + mouse look), which brings your 3D world to life and makes it navigable.

5. Add Lighting and Shading
Write basic GLSL shaders for diffuse and ambient lighting. Then add more complex effects like specular
highlights or point lights. Explore how normals and material properties affect visual realism.

6. Texture Mapping and Materials
Extend your renderer to support texture loading and mapping. Learn how to apply UV coordinates, sample
textures in shaders, and handle materials defined in OBJ/MTL files.

7. Scene Graph or Entity System
As complexity grows, you'll need a way to manage multiple objects and their transformations. Implement
a simple scene graph or entity-component system to organize updates, rendering, and object hierarchies.

8. Physics and Collision Detection
Incorporate a physics module or connect to a physics library like Bullet. Begin with bounding box or
sphere collision, then experiment with simple rigid body dynamics.

9. Optimisation and Performance Tools
Profile your engine and optimise hotspots. Introduce spatial partitioning structures (e.g., octrees or
BSP trees), frustum culling, or level-of-detail techniques to improve efficiency.

10.	Asset Pipeline and Scripting
Create a workflow for importing assets, defining scenes, and scripting behaviors. Consider embedding a
scripting language like Lua or writing a minimal configuration format.

11.	User Interface and Final Touches
Add a basic GUI system for debugging or menus. Final polish may include post-processing effects like
bloom, fog, or shadow mapping.


### Simple Start

If you're completely new to this field, a beginner-friendly starting point is provided in the folder [01](./01/).
This setup is designed to stay within the familiar territory of C, Python, and JavaScript, and we've intentionally
kept external dependencies to a minimum.

In this first part, we'll use:
- C for generating 3D geometry and rendering wireframes
- Python (with the Pillow library as an addition) for image processing
- JavaScript (in the browser) for viewing PAM files


__Step 1: Compile the Wireframe Renderer__

To generate a simple wireframe cube, compile the program with:

```shell
> make wireframe
```

This produces three output files:
- output.pam
- output2.pam
- points.pam

The first two files show the cube as a wireframe, rendered from different rotated positions.
The third file contains the 3D point data.

You can view the wireframe images using the provided pam7viewer.html tool in your browser.
The PAM7 format (in ASCII)[^pam] is simple to read and inspect manually, which makes it ideal for
learning and debugging.

[^pam]: See e.g. https://en.wikipedia.org/wiki/Netpbm#PAM_graphics_format.


__Step 2: Compile the Solid Renderer__

Next, compile the version that renders a solid-colored cube:

```shell
> make solid
```

This will generate a sequence of image files showing the cube rotating:
cube_frame_01.pam, cube_frame_02.pam, … up to cube_frame_15.pam.
Each frame shows the cube in a different orientation.


__Step 3: Merge Frames into an Animation__

Finally, you can merge the sequence of frames into a single animated image using:

```shell
> make merge
```

This creates an animated GIF, allowing you to easily view the rotating cube as a continuous animation.

This sequence of steps introduces the basics of 3D rendering, image processing, and minimal animation,
while keeping the system simple, transparent, and easily inspectable. You can walk this path for 
sometime, but eventually you will have to switch to other tools which makes much more sense developing
the engine further.


### Going Further

In [02](./02/), we delve into both general programming concepts and the specifics of rendering a rotating
cube. While we've primarily employed standard matrix operations thus far, alternative mathematical approaches
are available. These methods may present increased complexity in some aspects but offer simplifications in
others. The key takeaway is that solutions need not always follow traditional paths. By exploring and
experimenting with different techniques, you may uncover unexpected and valuable insights.
