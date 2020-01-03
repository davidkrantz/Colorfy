import numpy as np
from time import sleep
import rpi_ws281x as neopixel

class WS281XController():
    """Controller for WS281X LED-strips connected to a Raspberry Pi.

    Attributes:
        strip (Adafruit_NeoPixel): The Neopixel led strip object.
        
    """

    def __init__(self, led_count=1, led_pin=18, led_freq_hz=800000, led_dma=10, led_invert=False, led_brightness=100, led_channel=0):
        """Connect to Raspberry Pi and initilize the GPIO pins.

        Args:
            led_count (int): Number of leds in the led strip.
            led_pin (int): GPIO pin connected to the pixels (18 uses PWM!).
            led_freq_hz (int): (Optional) LED signal frequency in hertz (usually 800khz).
            led_dma (int): (Optional) DMA channel to use for generating signal (try 10).
            led_invert (bool): (Optional) True to invert the signal (when using NPN transistor level shift).
            led_brightness (int): (Optional) LED signal frequency in hertz (usually 800khz).
            led_channel (int): (Optional) set to '1' for GPIOs 13, 19, 41, 45 or 53.

        """

        self.strip = neopixel.Adafruit_NeoPixel(led_count, led_pin, led_freq_hz, led_dma, led_invert, led_brightness, led_channel)
        self.strip.begin()

    def _linear_gradient(self, start, finish, n=40):
        """Returns an interpolation between `start` and `finish` color.

        Args:
            start (list): Start color on the form [R, G, B].
            finish (list): Finish color on the form [R, G, B].
            n (int): Number of interpolation points.

        Returns:
            list: `n` colors evenly spaced between `start` and `finish`.

        """
        # Initilize a list of the output colors with the starting color
        rgb_arr = n * [None]
        rgb_arr[0] = start
        # Calcuate a color at each evenly spaced value of t from 1 to n
        for t in range(1, n):
            # Interpolate RGB vector for color at the current value of t
            curr_rgb = [int(start[j] + (float(t)/(n-1)) * (finish[j] \
                - start[j])) for j in range(3)]
            rgb_arr[t] = curr_rgb
        return rgb_arr

    def _get_rgb_from_int(self, RGBint):
        """Returns r,g and b values from 24-bit RGB value.

        Args:
            RGBint (int): 24-bit integer RGB value

        Returns:
            tuple: (R, G, B).
            
        """
        b =  RGBint & 255
        g = (RGBint >> 8) & 255
        r = (RGBint >> 16) & 255
        return r, g, b

    def set_color(self, r, g, b, delay=0.05):
        """Sets a new color using a linear interpolation.

        Args:
            r (int): The new red value.
            g (int): The new green value.
            b (int): The new blue value.
            delay (float): Delay in seconds between each interpolation
                color.

        """
        r_old, g_old, b_old = self.get_color()
        rgb_list = self._linear_gradient(start=[r_old, g_old, b_old],
                                        finish=[r, g, b])
        for r, g, b in rgb_list:
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColorRGB(i, r, g, b)
            self.strip.show()
            sleep(delay)

    def get_color(self):
        """Returns the current color.

        Returns:
            tuple: (R, G, B). The current color.

        """
        color = self.strip.getPixelColor(1)
        return self._get_rgb_from_int(color)