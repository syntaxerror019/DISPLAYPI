from luma.core.interface.serial import spi, noop
# pyrefly: ignore [missing-import]
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.core.legacy import show_message, textsize, text as draw_text
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT, SINCLAIR_FONT
import config
import time

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
        self.font_sinclair = proportional(SINCLAIR_FONT)

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
            
        w, h = textsize(text, font=font)
        x_offset = (self.device.width - w) // 2
        
        if x_offset < 0:
            x_offset = 0

        with canvas(self.device) as draw:
            draw_text(draw, (x_offset, y_offset), text, fill="white", font=font)

    def display_centered_animated(self, text, font=None, hold_time=2.5):
        # Slide In (from bottom up)
        for y in range(8, -1, -1):
            self.display_centered(text, font=font, y_offset=y)
            time.sleep(0.05)
            
        # Hold on screen
        time.sleep(hold_time)
        
        # Slide Out (up and away)
        for y in range(0, -9, -1):
            self.display_centered(text, font=font, y_offset=y)
            time.sleep(0.05)

    def display_time_with_blinking_colon(self, prefix, colon, suffix, font=None, colon_show=True):
        if font is None:
            font = self.font_lcd
            
        w_prefix, h_prefix = textsize(prefix, font=font)
        w_colon, h_colon = textsize(colon, font=font)
        w_suffix, h_suffix = textsize(suffix, font=font)
        
        # Calculate full width for centering
        w_full = w_prefix + w_colon + w_suffix
        x_offset = (self.device.width - w_full) // 2
        if x_offset < 0:
            x_offset = 0

        with canvas(self.device) as draw:
            # Draw prefix
            draw_text(draw, (x_offset, 0), prefix, fill="white", font=font)
            
            # Draw colon if it should be shown
            if colon_show:
                draw_text(draw, (x_offset + w_prefix, 0), colon, fill="white", font=font)
                
            # Draw suffix
            draw_text(draw, (x_offset + w_prefix + w_colon, 0), suffix, fill="white", font=font)

    def clear(self):
        self.device.clear()
