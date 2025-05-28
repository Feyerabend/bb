
## WebGL and OBJ files

> [!NOTE]  
> Not all browsers implement WebGL, which is required for this JS/HTML code. This also
> highlights the problem of relying on less established or non-standard programming
> languages and runtimes. As a task, you can adapt the JavaScript to your current
> operating system and web browser to run this simple OBJ viewer. Or let a LLM
> do another one for you.

To get acquainted with 3D graphics and rendering, you don't always have to start entirely from the bottom
and build everything from scratch. A top-down approach can also be useful. By exploring WebGL together
with the simple and widely supported OBJ file format, you can quickly gain insight into how 3D rendering
works and create a foundation for further experimentation and deeper understanding.

*[WebGL](./WEBGL.md)* (Web Graphics Library) is a JavaScript API that allows rendering interactive 2D
and 3D graphics directly in web browsers without needing plug-ins. Built on top of OpenGL ES (a lightweight
version of OpenGL for embedded systems), WebGL exposes low-level hardware-accelerated graphics functionality
through the browser's HTML5 <canvas> element. Developers write [shaders](./SHADER.md) in GLSL
(OpenGL Shading Language) and use JavaScript to issue rendering commands, manage buffers, define geometry,
and manipulate transformation matrices. WebGL operates very close to the metal, which means it offers
high performance and flexibility but requires a good understanding of computer graphics principles.
It forms the basis for many higher-level libraries like Three.js that simplify common tasks like scene
management, lighting, and camera control.

*OBJ* files[^obj] are a simple, text-based 3D geometry format commonly used for storing and exchanging models.
Originally developed by Wavefront Technologies, the .obj format encodes a model’s vertex positions,
texture coordinates, normals, and polygonal faces. It does not include information about materials,
lighting, or animation (though material properties can be defined in a separate .mtl file referenced
by the OBJ file, it is omitted here). Each line in the file typically begins with a keyword like v
for vertices, vt for texture coordinates, vn for normals, and f for face definitions that refer to
indices of previously listed elements. Because of its simplicity and wide support, the OBJ format is a
popular interchange format across 3D software and rendering pipelines.

[^obj]: https://en.wikipedia.org/wiki/Wavefront_.obj_file
