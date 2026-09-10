"""Hardware abstraction layer for the MAX7219 LED matrix display."""

import time

from luma.core.interface.serial import spi, noop
# pyrefly: ignore [missing-import]
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.core.legacy import show_message, textsize, text as draw_text
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT, SINCLAIR_FONT

from . import config


class DisplayRenderer:
    """High-level drawing helpers on top of the luma MAX7219 driver."""

    def __init__(self):
        self.serial = spi(port=0, device=0, gpio=noop())

        self.device = max7219(
            self.serial,
            cascaded=config.CASCADED_MATRICES,
            block_orientation=config.BLOCK_ORIENTATION,
        )

        self.device.contrast(config.BRIGHTNESS)

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
            y_offset=y_offset,
        )

    def display_centered(self, text, font=None, y_offset=0):
        if font is None:
            font = self.font_standard

        text_width, _ = textsize(text, font=font)
        x_offset = max((self.device.width - text_width) // 2, 0)

        with canvas(self.device) as draw:
            draw_text(draw, (x_offset, y_offset), text, fill="white", font=font)

    def display_centered_animated(self, text, font=None, hold_time=2.5):
        for y in range(8, -1, -1):
            self.display_centered(text, font=font, y_offset=y)
            time.sleep(0.05)

        time.sleep(hold_time)

        for y in range(0, -9, -1):
            self.display_centered(text, font=font, y_offset=y)
            time.sleep(0.05)

    def display_time_with_blinking_colon(self, prefix, colon, suffix, font=None, colon_show=True):
        if font is None:
            font = self.font_lcd

        # Measure and center using the full text so the string never shifts.
        full_text = f"{prefix}{colon}{suffix}"
        full_width, _ = textsize(full_text, font=font)

        x_offset = max((self.device.width - full_width) // 2, 0)

        with canvas(self.device) as draw:
            draw_text(draw, (x_offset, 0), full_text, fill="white", font=font)

            if not colon_show:
                # Draw a black mask over the colon only, leaving the 1px gap
                # after it intact so adjacent characters are not clipped.
                prefix_width, _ = textsize(prefix, font=font)
                colon_width, _ = textsize(colon, font=font)
                colon_x = x_offset + prefix_width
                x0 = colon_x
                x1 = colon_x + colon_width - 2
                draw.rectangle((x0, 0, x1, self.device.height), fill="black")

    def display_epileptic_countdown(self, text, hold_time=3.0, font=None, flash=True):
        if font is None:
            font = self.font_standard

        text_width, _ = textsize(text, font=font)
        x_offset = max((self.device.width - text_width) // 2, 0)

        if not flash:
            with canvas(self.device) as draw:
                draw_text(draw, (x_offset, 0), text, fill="white", font=font)
            time.sleep(hold_time + 0.6)
            return

        self._flash(text, x_offset, font, duration=0.3)

        with canvas(self.device) as draw:
            draw_text(draw, (x_offset, 0), text, fill="white", font=font)
        time.sleep(hold_time)

        self._flash(text, x_offset, font, duration=0.3)

    def display_celebration(self, text, duration=60.0, font=None):
        if font is None:
            font = self.font_standard

        text_width, _ = textsize(text, font=font)
        x_offset = max((self.device.width - text_width) // 2, 0)

        start_time = time.time()
        inverted = False
        while time.time() - start_time < duration:
            self._render_centered_inverted(text, x_offset, font, inverted)
            inverted = not inverted
            time.sleep(0.5)

    def clear(self):
        self.device.clear()

    def _flash(self, text, x_offset, font, duration):
        start_time = time.time()
        inverted = False
        while time.time() - start_time < duration:
            self._render_centered_inverted(text, x_offset, font, inverted)
            inverted = not inverted
            time.sleep(0.03)

    def _render_centered_inverted(self, text, x_offset, font, inverted):
        with canvas(self.device) as draw:
            if inverted:
                draw.rectangle((0, 0, self.device.width, self.device.height), fill="white")
                draw_text(draw, (x_offset, 0), text, fill="black", font=font)
            else:
                draw.rectangle((0, 0, self.device.width, self.device.height), fill="black")
                draw_text(draw, (x_offset, 0), text, fill="white", font=font)