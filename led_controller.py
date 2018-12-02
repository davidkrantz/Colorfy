import pigpio
import numpy as np
from time import sleep


class LEDController():
    """Controller for LED-strips connected to a Raspberry Pi.

    Attributes:
        pi (pigpio): Control the Raspberry Pi's GPIO.
        red_pin (int): GPIO pin used for the red LED channel.
        green_pin (int): GPIO pin used for the green LED channel.
        blue_pin (int): GPIO pin used for the blue LED channel.

    """

    def __init__(self, red_pin, green_pin, blue_pin, host=None):
        """Connect to Raspberry Pi and initilize the GPIO pins.

        Args:
            red_pin (int): GPIO pin used for the red LED channel.
            green_pin (int): GPIO pin used for the green LED channel.
            blue_pin (int): GPIO pin used for the blue LED channel.
            host (str): Nme or IP Address of Raspberry Pi.

        """
        if host:
            self.pi = pigpio.pi(host)
        else:
            self.pi = pigpio.pi()
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.pi.set_PWM_dutycycle(self.red_pin, 0)
        self.pi.set_PWM_dutycycle(self.green_pin, 0)
        self.pi.set_PWM_dutycycle(self.blue_pin, 0)

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
                self.pi.set_PWM_dutycycle(self.red_pin, r)
                self.pi.set_PWM_dutycycle(self.green_pin, g)
                self.pi.set_PWM_dutycycle(self.blue_pin, b)
                sleep(delay)

    def get_color(self):
        """Returns the current color.

        Returns:
            tuple: (R, G, B). The current color.

        """
        r = self.pi.get_PWM_dutycycle(self.red_pin)
        g = self.pi.get_PWM_dutycycle(self.green_pin)
        b = self.pi.get_PWM_dutycycle(self.blue_pin)
        return r, g, b

    def __del__(self):
        """Releases pigpio resources."""
        self.pi.stop()
