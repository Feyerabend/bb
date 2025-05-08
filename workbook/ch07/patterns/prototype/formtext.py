from abc import ABC, abstractmethod
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional, Dict, Any, Union
import copy
import os


# Strategy Pattern: Abstract base class for different text formatting algorithms
class TextFormatter(ABC):
    
    @abstractmethod
    def format_text(self, input_text: str, max_width: int, font) -> List[str]:
        pass


class ProportionalTextFormatter(TextFormatter):
    
    def format_text(self, input_text: str, max_width: int, font) -> List[str]:
        lines = []  # list to hold formatted lines
        
        for paragraph in input_text.split("\n"):  # split text by hard line breaks
            current_line = []
            current_line_width = 0
            words = paragraph.split()  # split paragraph into words
            space_width = font.getlength(" ")  # width of a space

            for word in words:
                # the width of the word when rendered with the font
                word_width = font.getlength(word)
                word_width_with_space = word_width + (space_width if current_line else 0)

                # check if adding the word would exceed the max width
                if current_line_width + word_width_with_space > max_width:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_line_width = word_width
                else:
                    current_line.append(word)
                    current_line_width += word_width_with_space

            # add the last line if there are leftover words in the current paragraph
            if current_line:
                lines.append(" ".join(current_line))
                
        return lines


# Define RenderingConfig first before it's used as a type hint
# Prototype Pattern: Configuration object for rendering
class RenderingConfig:
    
    def __init__(self):
        self.max_width = 400
        self.font_path = "Arial.ttf"  # changed to a common system font
        self.font_size = 20
        self.output_path = "formatted_text.png"
        self.padding = 20
        self.bg_color = "white"
        self.text_color = "black"
    
    # Prototype Pattern: Clone method for deep copying
    def clone(self):
        return copy.deepcopy(self)
    
    def to_dict(self) -> dict:
        return {
            "max_width": self.max_width,
            "font_path": self.font_path,
            "font_size": self.font_size,
            "output_path": self.output_path,
            "padding": self.padding,
            "bg_color": self.bg_color,
            "text_color": self.text_color
        }


class Renderer(ABC):
    
    @abstractmethod
    def render(self, formatted_lines: List[str], font, config: RenderingConfig) -> str:
        pass


class PillowRenderer(Renderer):
    
    def render(self, formatted_lines: List[str], font, config: RenderingConfig) -> str:
        # total image height based on the number of lines and font size
        line_height = font.getbbox("A")[3]  # line height from bounding box
        total_height = line_height * len(formatted_lines) + config.padding  # padding

        # blank image with a background color
        image = Image.new(
            "RGB", 
            (config.max_width + config.padding, total_height), 
            config.bg_color
        )
        draw = ImageDraw.Draw(image)

        # draw each line of text
        y = config.padding // 2  # start
        for line in formatted_lines:
            draw.text(
                (config.padding // 2, y), 
                line, 
                font=font, 
                fill=config.text_color
            )
            y += line_height

        # save image
        image.save(config.output_path)
        return config.output_path

# Builder Pattern: Builder for rendering configuration
class RenderingConfigBuilder:
    
    def __init__(self, prototype: Optional[RenderingConfig] = None):
        if prototype:
            self.config = prototype.clone()
        else:
            self.config = RenderingConfig()
    
    def set_max_width(self, width: int):
        self.config.max_width = width
        return self
    
    def set_font(self, path: str, size: int):
        self.config.font_path = path
        self.config.font_size = size
        return self
    
    def set_output_path(self, path: str):
        self.config.output_path = path
        return self
    
    def set_colors(self, bg_color: str = "white", text_color: str = "black"):
        self.config.bg_color = bg_color
        self.config.text_color = text_color
        return self
    
    def set_padding(self, padding: int):
        self.config.padding = padding
        return self
    
    def build(self) -> RenderingConfig:
        return self.config


# Factory Method Pattern: Factory for creating renderers and formatters
class TextRenderingFactory:
    
    @staticmethod
    def create_formatter(formatter_type: str = "proportional") -> TextFormatter:
        if formatter_type.lower() == "proportional":
            return ProportionalTextFormatter()
        # add more formatter types here as needed
        else:
            raise ValueError(f"Unsupported formatter type: {formatter_type}")
    
    @staticmethod
    def create_renderer(renderer_type: str = "pillow") -> Renderer:
        if renderer_type.lower() == "pillow":
            return PillowRenderer()
        # add more renderer types here as needed
        else:
            raise ValueError(f"Unsupported renderer type: {renderer_type}")


# Director Pattern: Orchestrates the text rendering process
class TextRenderingDirector:
    
    def __init__(self, formatter: TextFormatter, renderer: Renderer):
        self.formatter = formatter
        self.renderer = renderer
    
    def render_text(self, text: str, config: RenderingConfig) -> str:
        try:
            # try loading font
            font = ImageFont.truetype(config.font_path, config.font_size)
        except OSError:
            # fallback to default system font, if the specified font can't be found
            print(f"Warning: Could not find font '{config.font_path}'. Using default font.")
            # use system font that's likely to exist
            try:
                # try common system fonts
                system_fonts = [
                    "Arial.ttf", "arial.ttf",
                    "DejaVuSans.ttf", "DejaVuSans-Bold.ttf",
                    "Times.ttf", "TimesNewRoman.ttf",
                    "Verdana.ttf", 
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux path
                    "/System/Library/Fonts/Helvetica.ttc",  # macOS path
                    "C:\\Windows\\Fonts\\arial.ttf"  # Windows path
                ]
                
                for font_path in system_fonts:
                    try:
                        font = ImageFont.truetype(font_path, config.font_size)
                        print(f"Using font: {font_path}")
                        break
                    except OSError:
                        continue
            except:
                # last resort: use default font
                print("Using PIL default font.")
                font = ImageFont.load_default()
        
        formatted_lines = self.formatter.format_text(text, config.max_width, font)
        return self.renderer.render(formatted_lines, font, config)


# create some prototype configurations
class ConfigPrototypes:
    
    @staticmethod
    def get_prototypes() -> Dict[str, RenderingConfig]:
        prototypes = {}
        
        # default config
        default = RenderingConfig()
        prototypes["default"] = default
        
        # high-resolution config
        high_res = default.clone()
        high_res.font_size = 32
        high_res.padding = 40
        prototypes["high_res"] = high_res
        
        # minimalist config
        minimalist = default.clone()
        minimalist.padding = 10
        minimalist.bg_color = "black"
        minimalist.text_color = "white"
        prototypes["minimalist"] = minimalist
        
        return prototypes



# example
def main():
    text = (
    "To be, or not to be, that is the question: "
    "Whether ’tis nobler in the mind to suffer "
    "The slings and arrows of outrageous fortune, "
    "Or to take arms against a sea of troubles "
    "And, by opposing, end them. To die, to sleep— "
    "No more—and by a sleep to say we end "
    "The heartache and the thousand natural shocks "
    "That flesh is heir to—’tis a consummation "
    "Devoutly to be wished. To die, to sleep— "
    "To sleep, perchance to dream. Ay, there’s the rub, "
    "For in that sleep of death what dreams may come, "
    "When we have shuffled off this mortal coil, "
    "Must give us pause. There’s the respect "
    "That makes calamity of so long life. "
    "For who would bear the whips and scorns of time, "
    "Th’ oppressor’s wrong, the proud man’s contumely, "
    "The pangs of disprized love, the law’s delay, "
    "The insolence of office, and the spurns "
    "That patient merit of th’ unworthy takes, "
    "When he himself might his quietus make "
    "With a bare bodkin? Who would fardels bear, "
    "To grunt and sweat under a weary life, "
    "But that the dread of something after death, "
    "The undiscovered country from whose bourn "
    "No traveler returns, puzzles the will, "
    "And makes us rather bear those ills we have "
    "Than fly to others that we know not of? "
    "Thus conscience does make cowards of us all, "
    "And thus the native hue of resolution "
    "Is sicklied o’er with the pale cast of thought, "
    "And enterprises of great pitch and moment "
    "With this regard their currents turn awry "
    "And lose the name of action.—Soft you now, "
    "The fair Ophelia! Nymph, in thy orisons "
    "Be all my sins remembered."
    )
    # prototype config
    config_prototypes = ConfigPrototypes.get_prototypes()
    
    # clone and customise a prototype using the builder pattern
    config = (RenderingConfigBuilder(config_prototypes["default"])
              .set_max_width(400)
              # use a system font that's likely to exist
              .set_font("Arial.ttf", 12)
              .set_output_path("formatted_text.png")
              .build())
    
    # demonstrate creating a variant using the prototype pattern
    high_res_config = config_prototypes["high_res"].clone()
    high_res_config.output_path = "high_res_text.png"
    
    # create formatter and renderer using the factory
    formatter = TextRenderingFactory.create_formatter("proportional")
    renderer = TextRenderingFactory.create_renderer("pillow")
    
    # create the director and render the text
    director = TextRenderingDirector(formatter, renderer)
    output_path = director.render_text(text, config)
    
    print(f"Image saved at: {output_path}")
    
    # render high-res version using the prototype-based config
    high_res_output_path = director.render_text(text, high_res_config)
    print(f"High-res image saved at: {high_res_output_path}")


if __name__ == "__main__":
    main()

