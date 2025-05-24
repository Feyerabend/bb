
## Some 3D Algorithms

| Version | Scene Elements   | Lighting | Shading Model  | Animation        | Texture | Shadows | Input  |
|---------|------------------|----------|----------------|------------------|---------|---------|--------|
| 1       | Sphere           | 1 Point  | Lambertian     | None             | None    | None    | None   |
| 2       | Sphere + Plane   | 1 Point  | Lambertian     | None             | None    | Yes     | None   |
| 3       | + Y Bounce       | 1 Point  | Lambertian     | Vertical         | None    | Yes     | None   |
| 4       | + X Bounce       | 1 Point  | Lambertian     | Full 2D          | Image   | Yes     | None   |
| 5       | + Texture        | 1 Point  | Phong + Tex    | Full 2D + Rot    | Image   | Yes     | File   |


### 1. Static Raytracer

Conceptual Features
- Ray casting from camera to pixel.
- Ray-sphere intersection with quadratic root.
- Single light source for illumination.
- Diffuse (Lambertian) shading using dot product.

Code Characteristics
- Constants for resolution, FOV, sphere center.
- Camera rays constructed by pixel-to-viewport mapping.
- discriminant computed for sphere intersection:

```javascript
const discriminant = b * b - 4 * a * c;
```

- Normal at hit point used for simple Lambert shading:

```javascript
const diffuse = Math.max(dot(normal, lightDir), 0);
```


### 2. Adding Plane and Shadows

Conceptual Additions
- Ray-plane intersection (y = -1 plane).
- Shadow rays from hit point to light.
- Occlusion testing to simulate hard shadows.

Code Enhancements
- Introduced function to test if any object blocks light:

```javascript
if (discriminantShadow >= 0 && tShadow > 0 && tShadow < lightDist) {
  inShadow = true;
}
```

- When hit, compute whether pixel is shadowed.
- Added a checkerboard pattern on the plane using:

```javascript
const checker = (Math.floor(hitPoint[0]) + Math.floor(hitPoint[2])) % 2;
```


Impact
- Introduced multiple object intersections.
- Illumination becomes context-sensitive: light blocked → shadow.



### 3. Vertical Animation (Bouncing Sphere)

Conceptual Additions
- Animation system using requestAnimationFrame.
- Time-dependent vertical position via sine wave.
- Simulates bouncing sphere over time.

Code Additions
- Frame time used to control bounce phase:

```javascript
const bounceY = BASE_Y + Math.abs(Math.sin(time * 0.002)) * BOUNCE_HEIGHT;
const SPHERE_CENTER = [0, bounceY, -3];
```

- Scene is now redrawn per frame.

Impact
- Introduced temporal component.
- Rendering becomes continuous, not single-frame.



### 4. 2D Motion (X + Y)

Conceptual Additions
- Horizontal sinusoidal motion added to vertical bounce.
- Sphere moves along ellipse-like path.

Code Additions
- Independent horizontal phase:

```javascript
const bounceX = Math.sin(horizontalPhase * Math.PI * 2) * HORIZONTAL_BOUNCE_AMPLITUDE;
const SPHERE_CENTER = [bounceX, bounceY, -3];
```

- Same raycasting logic applies, but position is now 2D-animated.

Impact
- More complex animation path, giving scene liveliness.
- Illumination/shadowing must track new positions dynamically.



### 5. Texture Mapping and User Interaction

Conceptual Additions
- UV texture mapping based on surface normal.
- Texture coordinate rotation over time.
- Image upload from user via file input.
- Phong specular highlights for realism.

Code Additions
- UV from normal using spherical projection:

```javascript
let u = 0.5 + Math.atan2(normal[2], normal[0]) / (2 * Math.PI);
let v = 0.5 - Math.asin(normal[1]) / Math.PI;
```

- Image loaded and sampled from ImageData:

```javascript
const pixelIndex = (y * textureImage.width + x) * 4;
const texColor = [...];
```

- Texture rotation using:

```javascript
const uRotated = (u + rotationPhase) % 1.0;
```

- Lighting includes specular term:

```javascript
const specular = Math.pow(Math.max(dot(normal, halfDir), 0), SPECULAR_POWER);
```


Impact
- Moves from procedural color to photographic realism.
- Adds user-driven interactivity (uploading textures).
- Introduces full Phong model (ambient + diffuse + specular).
- Demonstrates how raytracing can incorporate raster texture logic.


### Evolution

1. From Geometry → Material Realism
- Geometry remained similar (single sphere + plane), but appearance became dramatically richer via:
- Procedural color → shadows → textures
- Hardcoded colors → per-pixel texture sampling

2. From Static Image → Continuous Animation
- Initially rendered once.
- Later versions render 60 FPS animations using requestAnimationFrame.

3. From Local → Global Scene Awareness
- Shadows and moving light increased awareness of inter-object relationships (occlusion, projection).
- Texture mapping introduced surface orientation awareness via normals → UV.

4. From Single-purpose → Flexible & Interactive
- Later versions allow arbitrary images.
- Code generalizes for arbitrary lighting, animation parameters.



### Conclusion


| Feature           | Early Versions           | Later Versions                                      |
|-------------------|--------------------------|-----------------------------------------------------|
| Scene Definition  | Constants only           | Parametrized by time, user input                    |
| Rendering Flow    | Single render loop       | Continuous redraw (`requestAnimationFrame`)         |
| Materials         | Hardcoded RGB            | Textures from user image + procedural fallback      |
| Lighting          | Diffuse (Lambert) only   | Phong: ambient + diffuse + specular                 |
| Interactivity     | None                     | Image file upload (`<input type="file">`)           |
| Shadows           | None initially           | Implemented with occlusion logic                    |
| Code Layout       | Monolithic loop          | Modular logic with functions (intersection, shading, etc.) |


The project demonstrates a clear and progressive pedagogical trajectory:
- Starts from the fundamentals of ray-object intersection and lighting.
- Introduces animation and shadows to enrich scene dynamics.
- Adds texture mapping and real-time interactivity for realism.
- Gradually transitions from a toy renderer into a miniature raytracing engine with extensible scene and material systems.

