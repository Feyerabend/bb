
## Some 3D Algorithms

It can be interesting to start with the code of a simple ray-tracing 3D renderer, and build toward the mathemathics
instead of doing the opposite. Here is a suggestion of where to start. As you might see the reflection
isn't working properly, and is given to you as a task to correct. More can be found in [projects](PROJECTS.md).


### Journey into 3D: Understanding Raytracing through Simple Web Examples

If you've ever wondered how realistic images are created on your screens, these simple web examples
offer a hands-on introduction to one of the fundamental techniques: *raytracing*.

There is a series of HTML files (`01.html` through `07.html`, and `five.html`), each building upon
the last to illustrate different aspects of 3D rendering. We'll explore them sequentially to understand
the magic behind bringing virtual worlds to life.


#### What is 3D Rendering?

At its core, 3D rendering is the process of converting a 3D model into a 2D image. Think of it like
taking a photograph of a sculpture. In computer graphics, we define objects (like spheres or planes),
lights, and a camera within a virtual 3D space. The rendering process then calculates what each pixel
on your screen should look like from the camera's perspective.

Raytracing is a rendering technique that simulates the path of light. Instead of tracing light from
the light source, it works backward:

1. *Rays from the Camera:* For every single pixel on your screen, a "ray" of light is cast from the
   virtual camera through that pixel into the 3D scene.
2. *Intersection:* The first thing the ray hits in the scene (e.g., a sphere or a plane) determines
   what that pixel will display.
3. *Lighting & Shading:* Once an intersection is found, the program calculates how light would
   illuminate that point, considering light sources, surface properties (color, shininess), and shadows.
4. *Coloring the Pixel:* Based on these calculations, the pixel is assigned a color, and this process
   repeats for every pixel, eventually forming the complete image.

This approach often results in very realistic images because it accurately models how light interacts
with objects.


#### Core Concepts You'll Encounter in These Samples:

Let's break down the key 3D concepts demonstrated in these files:

* *Vectors and Basic Math:* You'll see a `Vector` class in the JavaScript code. In 3D graphics, vectors
are essential for representing:
    * *Positions:* Where objects are in space (e.g., `x, y, z` coordinates).
    * *Directions:* Which way a light ray is traveling, or the "normal" (outward-facing) direction of a surface.
    * *Operations:* Adding, subtracting, scaling, and performing "dot products" (which help determine
      angles and how much light hits a surface).
* *Scene Setup:*
    * *Camera:* Defines the viewpoint from which the scene is rendered. This includes its position
      (`CAMERA_POS`) and Field of View (`FOV`), which is like the zoom level of a camera lens.
    * *Objects:* In these samples, you'll mainly see a `Sphere` and a `Plane`. Each has properties like
      its position and radius (for the sphere) or `y` coordinate (for the plane).
    * *Light Source:* A `LIGHT_POS` defines where the light is coming from, crucial for calculating
      shadows and diffuse lighting.
* *Ray-Object Intersection:* This is the heart of raytracing. The code calculates if and where a ray
  intersects with a sphere or a plane. This often involves solving mathematical equations (e.g.,
  quadratic equations for spheres).
* *Lighting Models:*
    * *Diffuse Lighting:* How much light "spreads" from a surface. It depends on the angle between the
      light direction and the surface's normal. Surfaces directly facing the light appear brighter.
    * *Ambient Light:* A base level of light in the scene that illuminates all surfaces equally, preventing
      completely black areas.
    * *Shadows:* By casting a "shadow ray" from the hit point towards the light source, the program can
      determine if another object blocks the light, creating a shadow.
* *Animation:* By updating object positions or properties over time (using `requestAnimationFrame` in
  JavaScript), the scenes come to life.
* *Textures:* Instead of a solid color, surfaces can have images (textures) applied to them. This adds
  detail and realism. You'll see how pixel data from an image is used to color a surface.
* *Reflection:* Simulating how light bounces off shiny surfaces. This involves casting new "reflection rays"
  from the hit point.
* *Multithreading (Web Workers):* For more complex scenes, rendering can be slow. Modern web browsers allow
  JavaScript to perform tasks in the background using "Web Workers," which can significantly speed up
  rendering by dividing the workload.


#### Exploring the Samples Sequentially:

Let's take a quick look at what each file likely demonstrates:

* `01.html` (Raytraced Sphere with Shadow): This is your basic starting point. It will render a static
  sphere and a plane, demonstrating fundamental ray-sphere and ray-plane intersection, along with basic
  diffuse lighting and shadows.

* `02.html` (Raytraced Sphere with Animated Color): Builds on `01.html` by introducing animation. You'll
  see the sphere's color changing over time. This shows how time can be incorporated into the rendering
  loop.

* `03.html` (Raytraced Bouncing Sphere with Animated Color): Adds more complex animation. The sphere will
  bounce up and down, demonstrating dynamic object positioning.

* `04.html` (Raytraced Bouncing Sphere with Texture): Introduces texture mapping. Instead of a plain colored
  sphere, it will display a texture (like the `checker.png` file) on its surface. You might even be able
  to load your own textures.

* `05.html` (Raytraced Bouncing Sphere with Texture - Enhanced/Multiple Spheres): This
  continue to refine the texture implementation.

* `06.html` (Raytraced Bouncing Sphere with Texture and Reflection): This file will demonstrate
  poor and faulty reflections, making the plane or sphere appear shiny and reflective of other
  objects in the scene. Build it better!

* `07.html` (Multi-threaded Raytracer with Web Workers): Focuses on performance. This example will show
  how the rendering workload can be distributed across multiple CPU cores using Web Workers, making the
  animations smoother, especially on more complex scenes.

* `five.html` (Multi-Sphere Raytracer): Introduce multiple spheres or a more complex scene setups. The
  textures are distored and have to be fixed ..

By examining the JavaScript code in each file, you'll see how these concepts are implemented step-by-step,
giving you a practical understanding of 3D raytracing from the ground up.

Next we wil give you some more detailed notes on the implementations.


### 1. Static Raytracer

*Conceptual Features*
- Ray casting from camera to pixel.
- Ray-sphere intersection using the quadratic formula.
- Single point light source for illumination.
- Diffuse (Lambertian) shading using dot product.

*Code Characteristics*
- Constants for resolution, field of view (FOV), and sphere center.
- Camera rays constructed by mapping pixel coordinates to viewport.
- Discriminant computed for sphere intersection:

```javascript
const a = dot(rayDir, rayDir);
const b = 2 * dot(subtract(rayOrigin, sphereCenter), rayDir);
const c = dot(subtract(rayOrigin, sphereCenter), subtract(rayOrigin, sphereCenter)) - sphereRadius * sphereRadius;
const discriminant = b * b - 4 * a * c;
if (discriminant >= 0) {
  const t = (-b - Math.sqrt(discriminant)) / (2 * a);
  // compute hit point and normal
}
```

- Lambertian shading using the normal and light direction:

```javascript
const hitPoint = add(rayOrigin, scale(rayDir, t));
const normal = normalize(subtract(hitPoint, sphereCenter));
const lightDir = normalize(subtract(lightPos, hitPoint));
const diffuse = Math.max(0, dot(normal, lightDir));
const color = scale([0.8, 0.3, 0.3], diffuse);
```


### 2. Adding Plane and Shadows

*Conceptual Additions*
- Ray-plane intersection for a ground plane (y = -1).
- Shadow rays from hit point to light source.
- Occlusion testing for hard shadows.

*Code Enhancements*
- Ray-plane intersection and shadow testing:

```javascript
function rayPlaneIntersection(rayOrigin, rayDir) {
  const t = -(rayOrigin[1] + 1) / rayDir[1];
  return t > 0 ? t : Infinity;
}

function isInShadow(hitPoint, lightPos, sphereCenter, sphereRadius) {
  const lightDir = normalize(subtract(lightPos, hitPoint));
  const tShadow = raySphereIntersection(hitPoint, lightDir, sphereCenter, sphereRadius);
  return tShadow > 0 && tShadow < distance(hitPoint, lightPos);
}
```

- Checkerboard pattern on the plane:

```javascript
const checker = (Math.floor(hitPoint[0]) + Math.floor(hitPoint[2])) % 2 === 0 ? 1 : 0;
const planeColor = checker ? [1, 1, 1] : [0.5, 0.5, 0.5];
```

*Impact*
- Supports multiple objects (sphere and plane).
- Shadows enhance realism by accounting for light occlusion.


### 3. Vertical Animation (Bouncing Sphere)

*Conceptual Additions*
- Animation using `requestAnimationFrame`.
- Time-dependent vertical position via sine wave.
- Simulates a bouncing sphere.

*Code Additions*
- Dynamic sphere position:

```javascript
const bounceY = BASE_Y + Math.abs(Math.sin(time * 0.002)) * BOUNCE_HEIGHT;
const sphereCenter = [0, bounceY, -3];

function render() {
  // update canvas with new sphere position
  requestAnimationFrame(render);
}
```

*Impact*
- Introduces temporal dynamics for continuous rendering.
- Shadows adapt to the moving sphere.


### 4. 2D Motion (X + Y)

*Conceptual Additions*
- Horizontal sinusoidal motion combined with vertical bounce.
- Sphere follows an elliptical path.
- User-uploaded image via file input.

*Code Additions*
- 2D motion for the sphere:

```javascript
const bounceX = Math.sin(time * 0.001 * Math.PI * 2) * HORIZONTAL_BOUNCE_AMPLITUDE;
const bounceY = BASE_Y + Math.abs(Math.sin(time * 0.002)) * BOUNCE_HEIGHT;
const sphereCenter = [bounceX, bounceY, -3];
```

- Texture applied to the sphere (image-based):

```javascript
const textureColor = sampleTexture(imageData, u, v);
```

- File input handling:

```javascript
document.getElementById('fileInput').addEventListener('change', function(event) {
  const file = event.target.files[0];
  const img = new Image();
  img.onload = () => {
    const canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    textureImage = ctx.getImageData(0, 0, img.width, img.height);
  };
  img.src = URL.createObjectURL(file);
});
```

*Impact*
- Enhances animation complexity with 2D motion.
- Texture mapping introduces image-based rendering.


### 5. Texture Mapping and User Interaction

*Conceptual Additions*
- UV texture mapping using spherical projection.
- Texture coordinate rotation over time.
- Phong shading with specular highlights.

*Code Additions*
- UV coordinates from normal:

```javascript
const u = 0.5 + Math.atan2(normal[2], normal[0]) / (2 * Math.PI);
const v = 0.5 - Math.asin(normal[1]) / Math.PI;
```

- Texture sampling:

```javascript
function sampleTexture(imageData, u, v) {
  const x = Math.floor(u * imageData.width);
  const y = Math.floor(v * imageData.height);
  const pixelIndex = (y * imageData.width + x) * 4;
  return [
    imageData.data[pixelIndex] / 255,
    imageData.data[pixelIndex + 1] / 255,
    imageData.data[pixelIndex + 2] / 255
  ];
}
```

- Texture rotation:

```javascript
const uRotated = (u + time * 0.0001) % 1.0;
```

- Phong shading:

```javascript
const viewDir = normalize(subtract(cameraPos, hitPoint));
const halfDir = normalize(add(lightDir, viewDir));
const diffuse = Math.max(0, dot(normal, lightDir));
const specular = Math.pow(Math.max(0, dot(normal, halfDir)), SPECULAR_POWER);
const finalColor = add(scale(texColor, diffuse + AMBIENT), scale([1, 1, 1], specular));
```


*Impact*
- Enables photographic realism with user textures.
- Adds interactivity via file uploads.
- Implements full Phong model for enhanced lighting.

Etc.


### Evolution

1. *Geometry → Material Realism*
   - Simple sphere evolves to textured sphere with shadows and plane.
   - Hardcoded colors → user-uploaded textures.

2. *Static → Continuous Animation*
   - Single-frame rendering evolves to 60 FPS animations using `requestAnimationFrame`.

3. *Local → Global Scene Awareness*
   - Shadows and dynamic lighting introduce inter-object relationships.
   - Texture mapping uses surface normals for UV coordinates.

4. *Single-purpose → Interactive*
   - User input via file uploads enables dynamic textures.
   - Generalized code supports flexible lighting and animation.


### Conclusion

This project traces the evolution of a raytracing engine from a basic static renderer to a dynamic, interactive system.
Each version builds incrementally:

- *Version 1*: Establishes ray-sphere intersection and Lambertian shading.
- *Version 2*: Adds a plane and shadows for multi-object scenes.
- *Version 3*: Introduces vertical animation for dynamic rendering.
- *Version 4*: Extends to 2D motion and basic texture mapping.
- *Version 5*: Incorporates user-uploaded textures, texture rotation, and Phong shading.
- *Version 6*: Reflection ray for the plane and traces it to check for sphere intersections, blending the result with the plane’s color.
- *Version 7*: Changing single work rendering to split work among WebWorkers.


The progression highlights core graphics concepts: raycasting, lighting models, animation, and texture mapping.
The modular design and interactive features make it a versatile foundation for further enhancements, such as complex
geometries or advanced lighting. This serves as an effective educational tool for understanding 3D rendering principles.
