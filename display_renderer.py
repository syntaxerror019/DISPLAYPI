from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.core.legacy import show_message, textsize, text as draw_text
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT
import config

class DisplayRenderer:
    def __init__(self):
        # Initialize SPI interface
        self.serial = spi(port=0, device=0, gpio=noop())
        
        # Initialize max7219 device
        self.device = max7219(
            self.serial, 
            cascaded=config.CASCADED_MATRICES, 
            block_orientation=config.BLOCK_ORIENTATION
        )
        
        # Set brightness
        self.device.contrast(config.BRIGHTNESS)
        
        # Standard professional fonts
        self.font_standard = proportional(CP437_FONT)
        self.font_lcd = proportional(LCD_FONT)

    def scroll_text(self, text, font=None, y_offset=0):
        if font is None:
            font = self.font_standard
            
        show_message(
            self.device, 
            text, 
            fill="white", 
            font=font, 
            scroll_delay=config.SCROLL_DELAY,
            y_offset=y_offset
        )

    def display_centered(self, text, font=None, y_offset=0):
        if font is None:
            font = self.font_standard
            
        # Measure text width
        w, h = textsize(text, font=font)
        # Calculate centered X
        # Display width is device.width (e.g. 96)
        x_offset = (self.device.width - w) // 2
        
        # Prevent it from going offscreen on the left if text is too long
        if x_offset < 0:
            x_offset = 0

        with canvas(self.device) as draw:
            draw_text(draw, (x_offset, y_offset), text, fill="white", font=font)
            
    def clear(self):
        self.device.clear()
