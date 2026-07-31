from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT, UKR_FONT, TOMS_FONT
from PIL import ImageOps
import config
import time
import random

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
        
        # Fonts collection for "epilepsy" randomized effects
        self.fonts = [
            proportional(CP437_FONT),
            proportional(TINY_FONT),
            proportional(SINCLAIR_FONT),
            proportional(LCD_FONT),
            proportional(UKR_FONT),
            proportional(TOMS_FONT)
        ]
        self.font = self.fonts[0]

    def get_random_font(self):
        return random.choice(self.fonts)

    def scroll_text(self, text, font=None, y_offset=0):
        if font is None:
            font = self.font
            
        show_message(
            self.device, 
            text, 
            fill="white", 
            font=font, 
            scroll_delay=config.SCROLL_DELAY,
            y_offset=y_offset
        )

    def display_static(self, text, font=None, x_offset=0, y_offset=0, invert=False):
        if font is None:
            font = self.font
            
        with canvas(self.device) as draw:
            from luma.core.legacy import text as draw_text
            # If invert is true, draw white background and black text
            if invert:
                draw.rectangle(self.device.bounding_box, outline="white", fill="white")
                draw_text(draw, (x_offset, y_offset), text, fill="black", font=font)
            else:
                draw_text(draw, (x_offset, y_offset), text, fill="white", font=font)

    def flash_effect(self, text, duration=2.0, font=None):
        """Flashes text rapidly with inverted colors for a given duration"""
        if font is None:
            font = self.get_random_font()
            
        start_time = time.time()
        invert = False
        while time.time() - start_time < duration:
            self.display_static(text, font=font, invert=invert)
            invert = not invert
            # Fast flash
            time.sleep(0.05)
        
        # Settle on non-inverted
        self.display_static(text, font=font, invert=False)
        
    def clear(self):
        self.device.clear()
