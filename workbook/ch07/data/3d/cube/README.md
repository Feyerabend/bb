
## Introduction to 3D Graphics with a Cube

At its core, 3D graphics on a 2D screen is about taking three-dimensional data (like the vertices
of a cube) and transforming them into two-dimensional coordinates that can be drawn on a screen.
This involves a series of mathematical operations.


### 01. The Static Wireframe Cube: `fixedcube.html`

This file introduces the fundamental building blocks of our 3D cube.

#### Code Breakdown:

* *`vertices` array*: This is the heart of our cube's definition. It's an array of arrays, where
  each inner array represents a point in 3D space with `[x, y, z]` coordinates.
    ```javascript
    const vertices = [
        [-1, -1, -1], [1, -1, -1],
        [1,  1, -1], [-1,  1, -1],
        [-1, -1,  1], [1, -1,  1],
        [1,  1,  1], [-1,  1,  1]
    ];
    ```
    * *Concept: Vertices*
        Vertices are the corner points of our 3D object. In this case, we have 8 vertices for a cube,
        defining its shape in a coordinate system. The values -1 and 1 indicate that our cube is centered
        at the origin (0,0,0) and extends 1 unit in each direction along the x, y, and z axes.

* *`edges` array*: This array defines which vertices are connected to form the wireframe of the cube.
  Each inner array contains two indices, referring to the positions of vertices in the `vertices` array.
    ```javascript
    const edges = [
        [0,1],[1,2],[2,3],[3,0], // back
        [4,5],[5,6],[6,7],[7,4], // front
        [0,4],[1,5],[2,6],[3,7]  // sides
    ];
    ```
    * *Concept: Edges*
        Edges are the lines connecting vertices. They define the "wireframe" structure of the object.
        Think of it like a skeleton.

* *`rotationMatrixX(angle)` and `rotationMatrixY(angle)` functions*: These functions generate 3x3 matrices
  used to rotate 3D points around the X and Y axes, respectively.
    ```javascript
    function rotationMatrixX(angle) {
        const c = Math.cos(angle), s = Math.sin(angle);
        return [
            [1, 0, 0],
            [0, c, -s],
            [0, s, c]
        ];
    }
    // Similar for Y
    ```
    * *Concept: Rotation Matrices*
        A fundamental concept in 3D graphics is transforming points in space. Rotation matrices are mathematical
        tools that allow us to rotate a point around a specific axis. When you multiply a vertex's coordinates
        by a rotation matrix, you get new coordinates that represent the vertex's rotated position.
        * *How it works (simplified):* Each row and column of the matrix corresponds to how the new X, Y, and Z
          coordinates are calculated from the original X, Y, and Z. The `Math.cos()` and `Math.sin()` functions
          are very essential here as they handle the trigonometric calculations for rotation.

* *`matrixVectorMult(m, v)` function*: This function performs a matrix-vector multiplication. It takes a 3x3
  matrix `m` and a 3D vector (vertex) `v` and returns the transformed 3D vector.
    ```javascript
    function matrixVectorMult(m, v) {
        return [
            m[0][0]*v[0] + m[0][1]*v[1] + m[0][2]*v[2],
            m[1][0]*v[0] + m[1][1]*v[1] + m[1][2]*v[2],
            m[2][0]*v[0] + m[2][1]*v[1] + m[2][2]*v[2],
        ];
    }
    ```
    * *Concept: Matrix-Vector Multiplication*
        This is the core operation for applying transformations (like rotation) to our vertices. Each new
        coordinate (x', y', z') is a sum of products of the matrix elements and the original vector coordinates.

* *`project([x, y, z])` function*: This function takes a 3D point and converts it into a 2D point on the canvas.
  This is a simple perspective projection.
    ```javascript
    function project([x, y, z]) {
        const scale = 150 / (5 - z);
        return [
            x * scale + width / 2,
            -y * scale + height / 2
        ];
    }
    ```
    * *Concept: Perspective Projection*
        This is how we create the illusion of depth on a flat screen. Objects further away appear smaller,
        and objects closer appear larger.
        * The `(5 - z)` in the `scale` calculation simulates a "camera" at `z=5`. The further an object is
          (larger positive `z` value, or smaller negative `z` value, as `z` here is depth *into* the screen),
          the larger `(5-z)` becomes, making `scale` smaller. This results in smaller projected `x` and `y` values.
        * `width / 2` and `height / 2` are added to center the projected points on the canvas.
        * `-y * scale` is used because in computer graphics, the Y-axis typically points *downwards*, while in
          mathematical coordinates, it points upwards.

* *`drawCube()` function*: This function orchestrates the drawing process.
    1. It clears the canvas.
    2. It defines fixed rotation angles for X and Y axes.
    3. It transforms each vertex by applying the rotation matrices.
    4. It projects the transformed 3D vertices into 2D coordinates.
    5. It then iterates through the `edges` array, drawing a line between the two projected 2D points
       for each edge.


### 02. Auto-Rotating Cube: `autorot.html`

This file builds on the `fixedcube.html` by adding animation.

* *`angleX` and `angleY` variables*: These are introduced to keep track of the current rotation angles.
* *`draw()` function*: The core logic is moved into a `draw()` function.
* *Animation Loop (`requestAnimationFrame`)*:
    ```javascript
    angleX += 0.01;
    angleY += 0.02;
    requestAnimationFrame(draw);
    ```
    * *Concept: Animation Loop*
        `requestAnimationFrame` is a browser API that tells the browser you want to perform an animation
         and requests that the browser calls a specified function to update an animation before the browser's
         next repaint. By repeatedly calling `requestAnimationFrame` within the `draw` function, we create a
         continuous animation loop. In each frame, `angleX` and `angleY` are incremented, causing the cube
         to rotate.


### 02. User-Rotated Cube: `userrot.html`

This file adds interactivity, allowing the user to rotate the cube by dragging the mouse.

* *`dragging`, `lastX`, `lastY` variables*: These are introduced to manage mouse interaction state.
* *Event Listeners (`mousedown`, `mouseup`, `mousemove`)*:
    ```javascript
    canvas.addEventListener('mousedown', e => { /* .. */ });
    canvas.addEventListener('mouseup', () => { /* .. */ });
    canvas.addEventListener('mousemove', e => { /* .. */ });
    ```
    * *Concept: Event Listeners*
        These JavaScript mechanisms allow the code to react to user input.
        * `mousedown`: When the mouse button is pressed, `dragging` is set to `true`, and the current
          mouse coordinates (`e.clientX`, `e.clientY`) are stored as `lastX` and `lastY`. The cursor
          also changes to `grabbing`.
        * `mouseup`: When the mouse button is released, `dragging` is set to `false`, and the cursor
          changes back to `grab`.
        * `mousemove`: If `dragging` is true, the change in mouse position (`dx`, `dy`) since the last
          frame is calculated. These changes are then used to update `angleY` (for horizontal mouse
          movement, rotating around the Y-axis) and `angleX` (for vertical mouse movement, rotating
          around the X-axis). This creates the interactive rotation effect.

* *HUD (`info` div)*: A `div` element is added to display the current rotation angles to the user.

### 03. Solid, Filled Cube: `filled.html`

This file moves from a wireframe to a solid cube with colored faces. It introduces the crucial concept of rendering order.

* *`faces` array*: Instead of just `edges`, we now define `faces`. Each face is an array of four vertex
indices that form a quadrilateral.
    ```javascript
    const faces = [
        [0,1,2,3], // back
        [4,5,6,7], // front
        // ... more faces
    ];
    ```
    * *Concept: Faces*
        Faces are the flat surfaces that make up the object. For a cube, each face is a square defined by four vertices.

* *`colors` array*: An array of hexadecimal color codes, one for each face.
* *Painter's Algorithm (Depth Sorting)*: This is the most significant addition.
    ```javascript
    // Compute average Z for each face (used for sorting)
    const faceDepths = faces.map((face, i) => {
        const avgZ = face.reduce((sum, idx) => sum + transformed[idx][2], 0) / 4;
        return { index: i, depth: avgZ };
    });

    // Painter's algorithm: sort by depth (furthest first)
    faceDepths.sort((a, b) => b.depth - a.depth);

    // Draw faces
    for (const {index} of faceDepths) { /* .. */ }
    ```
    * *Concept: Painter's Algorithm / Depth Sorting*
        When rendering solid 3D objects, the order in which you draw the faces matters. If you draw a closer face
        *before* a further one, the further one might incorrectly draw over the closer one. The Painter's Algorithm
        solves this by sorting all faces by their average Z-depth (distance from the camera) and then drawing them
        from furthest to closest. This ensures that closer objects correctly obscure further objects, creating a
        realistic solid appearance.

* *Drawing Faces*:
    ```javascript
    ctx.beginPath();
    projected.forEach(([x, y], i) => {
        if (i === face[0]) ctx.moveTo(x, y);
    });
    for (let i = 1; i < face.length; i++) {
        const [x, y] = projected[face[i]];
        ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fillStyle = colors[index] + "88"; // semi-transparent
    ctx.fill();
    ctx.strokeStyle = "#000";
    ctx.stroke();
    ```
    Instead of `lineTo` for edges, `ctx.fill()` is now used to fill the polygon defined by the face's projected
    vertices. A semi-transparent color (`"88"` at the end of the hex code) and a black stroke are applied.

### 04. Lit Cube with Culling and Shadow: `litcube.html`

This file significantly enhances realism by adding lighting, back-face culling, and a rudimentary shadow.

* *`lightDir`*: This 3D vector represents the direction of the light source.
    * *Concept: Light Direction*
        In basic lighting models, a light source is often represented by a direction vector. This vector
        tells us from which direction the light is shining onto the object.

* *Vector Math Utilities (`sub`, `cross`, `dot`, `normalize`)*: These functions are crucial for performing
  3D vector operations.
    * *`sub(a, b)`*: Subtracts vector `b` from vector `a`.
    * *`cross(a, b)`*: Computes the cross product of two vectors `a` and `b`. The cross product of two
      vectors gives a new vector that is perpendicular (normal) to both original vectors. This is essential
      for finding the face normal.
    * *`dot(a, b)`*: Computes the dot product of two vectors `a` and `b`. The dot product is a scalar value
      that indicates the angle between two vectors. It's used here for lighting and culling calculations.
    * *`normalize(v)`*: Converts a vector into a unit vector (a vector with a length of 1) while maintaining
      its direction. This is important for consistent lighting calculations.
    * *Concept: Normal Vector*:
        A normal vector to a surface is a vector that is perpendicular to that surface. For each face of our
        cube, we calculate its normal vector. This vector tells us which way the face is "facing".

* *Back-Face Culling*:
    ```javascript
    const normal = cross(sub(pts3d[1], pts3d[0]), sub(pts3d[2], pts3d[0]));
    const viewDir = normalize(sub([0, 0, 5], center)); // Camera at (0, 0, 5)

    const isFrontFacing = dot(normalize(normal), viewDir) > 0;
    // ...
    if (pass === 0 && isFrontFacing) continue; // Skip front faces in first pass
    if (pass === 1 && !isFrontFacing) continue; // Skip back faces in second pass
    ```
    * *Concept: Back-Face Culling*
        In 3D graphics, we only need to draw the faces that are visible to the camera. Faces pointing away from
        the camera are called "back faces" and can be "culled" (not drawn) to save rendering time. This is
        determined by taking the dot product of the face's normal vector and the camera's view direction. If
        the dot product is positive, the face is pointing towards the camera (front-facing); otherwise, it's
        a back-face.

* *Lambertian Lighting*:
    ```javascript
    const brightness = Math.max(0.4, dot(normalize(normal), lightDir)) * 0.9;
    ctx.fillStyle = face.color; // color is now adjusted based on brightness
    ```
    * *Concept: Lambertian Lighting Model*
        This is a simple model for how light interacts with a diffuse (non-shiny) surface. The idea is that the
        more directly a surface faces a light source, the brighter it appears. This is calculated using the dot
        product of the face's normal vector and the light direction vector. A dot product of 1 means they are
        perfectly aligned (brightest), 0 means perpendicular (no direct light), and -1 means facing away (darkest).
        `Math.max(0.4, ...)` ensures a minimum ambient brightness even for faces facing away from the light.

* *Shadow (`projectShadow`)*:
    ```javascript
    function projectShadow(v, lightDir) {
      const t = (v[1] + 1.5) / lightDir[1]; // Project to y = -1.5
      return [
        v[0] - lightDir[0] * t,
        -1.5,
        v[2] - lightDir[2] * t
      ];
    }
    // ...
    const shadowVerts = pts3d.map(v => project(projectShadow(v, lightDir)));
    ```
    * *Concept: Simple Planar Shadow*
        This creates a shadow by projecting each vertex of the cube onto a flat plane (in this case, `y = -1.5`)
        along the direction of the light. The projected points then form the shadow polygon, which is drawn in
        a dark, semi-transparent color.

* *Floor*: A simple perspective floor is drawn with a gradient.

### 05. Reflective Cube: `reflectcube.html`

This final file adds reflections to the cube, making the scene even more dynamic.

* *`reflectAcrossFloor(v, floorY)` function*: This function calculates the mirrored position of a vertex across
a horizontal plane (the floor).
    ```javascript
    function reflectAcrossFloor(v, floorY) {
      return [v[0], 2 * floorY - v[1], v[2]];
    }
    ```
    * *Concept: Reflection*:
        To simulate reflection, we create a "mirrored" version of the cube by reflecting each of its vertices
        across the plane of the floor. The formula `2 * floorY - v[1]` effectively flips the Y-coordinate relative
        to the floor.

* *Drawing Reflection*:
    ```javascript
    const reflectedCube = cube.map(v => reflectAcrossFloor(v, floorY));
    // ...
    drawCube(reflectedCube, true); // Draw reflection first
    // ...
    drawCube(cube, false); // Then draw main cube
    ```
    The `drawCube` function is now called twice: once for the reflected cube (with a `isReflection` flag set to
    `true`) and once for the main cube. The reflected cube is drawn *first* to ensure it appears "under" the floor.

* *Adjustments for Reflection Drawing*:
    * *Face Culling for Reflections*: For reflected objects, the `isFrontFacing` logic needs to be inverted because
      we are effectively viewing the cube from "underneath".
        ```javascript
        if (isReflection) {
          isFrontFacing = !isFrontFacing;
        }
        ```
    * *Lighting for Reflections*: The normal vector for lighting calculations is also flipped for reflections.
        ```javascript
        let lightingNormal = normalize(normal);
        if (isReflection) {
          lightingNormal = lightingNormal.map(x => -x);
        }
        ```
    * *Opacity and Brightness for Reflections*: The reflection is made more transparent (`alpha *= 0.4`) and
      slightly darker (`finalBrightness *= 0.7`) to give it a more realistic reflective appearance.
    * *Darkening Colors for Reflection*: A clever trick is used to darken the colors of the reflected cube
      by converting them to RGB and then scaling the RGB components.
    * *Lighter Stroke for Reflection*: The stroke around reflected faces is made lighter for a more subtle look.


### Summary Concepts

* *Coordinate Systems*: Everything starts with defining points in a 3D space (`[x, y, z]`).
* *Transformations (Rotation, Translation, Scaling)**: How we move, rotate, and resize objects
  in 3D space. These are typically done using matrix multiplications. Imagine a stamp: transformations
  are how you position, turn, or size that stamp before pressing it down.
* *Projection*: The process of converting 3D points to 2D points on your screen. This is crucial
  for creating the illusion of depth. Think of it like taking a photo of a 3D object--the camera
  projects the 3D scene onto a 2D image.
* *Rendering Order (Painter's Algorithm)*: When you have solid objects, you need to draw them in
  the correct order (furthest to closest) to ensure that closer objects correctly cover up further
  ones. Otherwise, you'd see through solid parts. It's like painting a mural: you paint the background
  first, then the midground, then the foreground.
* *Normal Vectors*: These are invisible arrows pointing straight out from a surface. They are essential
  for determining which way a surface is facing (for culling) and how light interacts with it (for lighting).
* *Dot Product*: A mathematical operation that tells you how "aligned" two vectors are. It's used to
  calculate how much light a surface receives and whether a face is pointing towards or away from the camera.
* *Cross Product*: A mathematical operation that gives you a new vector perpendicular to two other vectors.
  This is how we find the normal vector of a face defined by two edges.
* *Lighting Models (Lambertian)*: Simple rules that describe how light interacts with surfaces to give
  them brightness and shading.
* *Shadows and Reflections*: Achieved by creating "extra" objects (projected onto a plane for shadows,
  or mirrored for reflections) and rendering them in the correct order with adjusted properties
  (transparency, color).

This series of files provides a fantastic, hands-on journey into the fundamentals of 3D graphics,
showing how basic linear algebra and geometry come together to create compelling visual effects.

