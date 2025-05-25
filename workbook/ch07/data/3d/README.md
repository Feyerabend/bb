
## Some 3D Algorithms

It can be interesting to start with the code of a simple 3D renderer, and build toward the mathemathics
instead of doing the opposite. Here is a suggestion of where to start. As you might see the reflection
isn't working properly, and is given to you as a task to correct. More can be found in [projects](PROJECTS.md).

| Version | Scene Elements   | Lighting | Shading Model  | Animation        | Texture | Shadows | Input  |
|---------|------------------|----------|----------------|------------------|---------|---------|--------|
| 1       | Sphere           | 1 Point  | Lambertian     | None             | None    | None    | None   |
| 2       | Sphere + Plane   | 1 Point  | Lambertian     | None             | None    | Yes     | None   |
| 3       | Sphere + Plane   | 1 Point  | Lambertian     | Vertical         | None    | Yes     | None   |
| 4       | Sphere + Plane   | 1 Point  | Lambertian     | Full 2D          | Image   | Yes     | File   |
| 5       | Sphere + Plane   | 1 Point  | Phong + Tex    | Full 2D + Rot    | Image   | Yes     | File   |
| 6       | Sphere + Plane   | 1 Point  | Phong + Tex    | Full 2D + Rot    | Image   | Yes     | File   |

Version 7. WebWorkers edition.


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

