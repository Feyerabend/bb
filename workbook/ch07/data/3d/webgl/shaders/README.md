
## Shaders and Traditional Rendering

Traditional 3D rendering calculates lighting and colours once per triangle or surface. In the example 'traditional.html',
you can see this with flat shading--the entire triangle face gets one color based on a single lighting calculation
using the triangle's normal vector. This approach is computationally lighter because you're doing fewer calculations,
but it produces (in the case) that characteristic "faceted" look where each triangle is uniformly coloured.

Shader-based rendering, shown in the second example 'shader.html', performs calculations at a much more
granular level--potentially for every single pixel (in a GPU). The vertex shader transforms each vertex
position and passes along attributes like colour and normal vectors. Then the fragment shader runs for
each pixel inside the triangle, interpolating values smoothly across the surface and calculating the
final colour. This creates smooth gradients and more realistic lighting effects.

The key concepts here revolve around the rendering *pipeline stages*. Traditional rendering often combines multiple
steps into simplified calculations--transform the geometry, calculate lighting once per face, and fill in the triangles.
Shader rendering separates these into distinct programmable stages where you have precise control over each vertex
transformation and each pixel's final appearance.

Another important difference is *interpolation*. Traditional rendering might interpolate basic properties like depth
for z-buffering, but shader rendering interpolates everything--colours, normals, texture coordinates, and custom
attributes--smoothly across triangle surfaces. This interpolation happens automatically between the vertex and fragment
stages. The depth buffer concept appears in both approaches for handling which surfaces are visible, but shader
rendering typically offers more sophisticated depth testing and blending options. You also get much more flexibility
with effects like per-pixel lighting, texture mapping, and complex material properties that would be difficult or
even impossible with traditional fixed-function rendering.

