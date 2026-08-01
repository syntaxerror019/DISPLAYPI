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
            
        # Lock the X offset based on the full width with a colon
        # This prevents the left side (date and hour) from shifting AT ALL.
        full_width_text = f"{prefix}:{suffix}"
        w_full, _ = textsize(full_width_text, font=font)
        
        x_offset = (self.device.width - w_full) // 2
        if x_offset < 0:
            x_offset = 0

        # Draw the text with either a colon or a space
        actual_colon = ":" if colon_show else " "
        actual_text = f"{prefix}{actual_colon}{suffix}"
        
        with canvas(self.device) as draw:
            draw_text(draw, (x_offset, 0), actual_text, fill="white", font=font)

    def display_epileptic_countdown(self, text, hold_time=3.0, font=None):
        if font is None:
            font = self.font_standard
            
        w, h = textsize(text, font=font)
        x_offset = (self.device.width - w) // 2
        if x_offset < 0:
            x_offset = 0
            
        # 1. Intro Flashes (300ms total, super fast)
        start_time = time.time()
        inverted = False
        while time.time() - start_time < 0.3:
            with canvas(self.device) as draw:
                if inverted:
                    draw.rectangle((0, 0, self.device.width, self.device.height), fill="white")
                    draw_text(draw, (x_offset, 0), text, fill="black", font=font)
                else:
                    draw.rectangle((0, 0, self.device.width, self.device.height), fill="black")
                    draw_text(draw, (x_offset, 0), text, fill="white", font=font)
            inverted = not inverted
            time.sleep(0.03)
            
        # 2. Hold Normal (for hold_time seconds)
        with canvas(self.device) as draw:
            draw_text(draw, (x_offset, 0), text, fill="white", font=font)
        time.sleep(hold_time)
        
        # 3. Outro Flashes (300ms total, super fast)
        start_time = time.time()
        inverted = False
        while time.time() - start_time < 0.3:
            with canvas(self.device) as draw:
                if inverted:
                    draw.rectangle((0, 0, self.device.width, self.device.height), fill="white")
                    draw_text(draw, (x_offset, 0), text, fill="black", font=font)
                else:
                    draw.rectangle((0, 0, self.device.width, self.device.height), fill="black")
                    draw_text(draw, (x_offset, 0), text, fill="white", font=font)
            inverted = not inverted
            time.sleep(0.03)

    def clear(self):
        self.device.clear()
