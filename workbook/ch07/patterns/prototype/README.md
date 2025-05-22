
## Prototype Pattern

..


### Example: Formtext

The code implements a text rendering system with the *Prototype* design pattern as a key component,
used in the *RenderingConfig* class to create varied configurations efficiently. The *Prototype*
pattern enables cloning of configuration objects to produce new instances with shared base settings,
avoiding repetitive initialisation.

The *RenderingConfig* class defines properties like `max_width`, `font_path`, `font_size`, `output_path`,
`padding`, `bg_color`, and `text_color`. Its `clone()` method, using `deepcopy`, creates an independent copy,
ensuring modifications (e.g., changing `font_size` or `output_path`) don't affect the original. The
*ConfigPrototypes* class provides predefined configurations ("default," "high_res," "minimalist") by
cloning and customizing a base *RenderingConfig*, showcasing the pattern's efficiency. For instance,
the "high_res" config clones the default and adjusts `font_size` and `padding`, while the main block
clones a prototype and uses a *RenderingConfigBuilder* to further customise settings.

This approach is efficient because *RenderingConfig* objects are complex, and cloning reduces overhead
compared to creating new instances from scratch. The main block demonstrates this by rendering text with
a default config and a high-resolution variant, both derived from prototypes.

Beyond the *Prototype* pattern, the code uses other patterns: *Strategy* (via *TextFormatter* for text
formatting), *Factory Method* (via *TextRenderingFactory* for creating formatters/renderers), *Builder*
(via *RenderingConfigBuilder* for constructing configs), and *Director* (via *TextRenderingDirector* for
orchestrating rendering). The *PillowRenderer* uses PIL to render formatted text onto an image, handling
font loading with fallbacks for robustness.

In summary, the *Prototype* pattern in *RenderingConfig* enables efficient creation of varied rendering
configurations by cloning, supporting flexible text rendering while minimising setup costs.


### Example: Pixel Fonts

The code implements a *BitmapFont* class using the *Prototype* design pattern to efficiently create
font instances with varied configurations. The *Prototype* pattern is realized through an abstract
base class *Prototype*, defining a `clone()` method. *BitmapFont* inherits this and implements `clone()`
with Python's `deepcopy`, creating an independent copy of the font object, including its glyphs and
properties like color and outline.

The `clone()` method enables creating new font instances without redefining the complex glyph set,
which includes bitmap arrays for digits, letters, and punctuation. This is efficient, as glyph creation
(via `_create_glyphs`) is resource-heavy. For example, the main block creates a green font, clones it,
and modifies the clone to yellow with a red outline, demonstrating flexible customization without
affecting the original.

The *BitmapFont* class supports text rendering with customizable colors, backgrounds, and outlines via
`render_char` and `render_text`. The *ColorUtils* class aids color manipulation but is secondary to the
Prototype pattern. The main block uses PIL to render styled text, showcasing cloning's efficiency in
creating font variations.

In short, the Prototype pattern allows *BitmapFont* to clone instances, preserving glyph data while
enabling style modifications, optimizing resource use for bitmap font rendering.

