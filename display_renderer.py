from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
import config
import time

class DisplayRenderer:
    def __init__(self):
        # Initialize SPI interface
        # port=0, device=0 is the default /dev/spidev0.0
        self.serial = spi(port=0, device=0, gpio=noop())
        
        # Initialize max7219 device
        self.device = max7219(
            self.serial, 
            cascaded=config.CASCADED_MATRICES, 
            block_orientation=config.BLOCK_ORIENTATION
        )
        
        # Set brightness
        self.device.contrast(config.BRIGHTNESS)
        
        # Fonts
        self.font = proportional(CP437_FONT)

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

    def display_static(self, text, font=None, x_offset=0, y_offset=0):
        if font is None:
            font = self.font
            
        with canvas(self.device) as draw:
            from luma.core.legacy import text as draw_text
            draw_text(draw, (x_offset, y_offset), text, fill="white", font=font)
            
    def clear(self):
        self.device.clear()
