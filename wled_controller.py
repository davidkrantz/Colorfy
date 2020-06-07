import requests

class WLEDController():
    """Controller for WS281X LED-strips connected to a Raspberry Pi.

    Attributes:
        strip (Adafruit_NeoPixel): The Neopixel led strip object.

    """

    def __init__(self, ip):
        self.ip = ip
        self.wledDeviceAddress = ip + "/win"

    def set_color(self, r, g, b):
        requests.get(url = self.wledDeviceAddress + "&R=%d&G=%d&B=%d" % (r, g, b))

    def get_color(self):
        """Returns the current color.

        Returns:
            tuple: (R, G, B). The current color.

        """
        r = requests.get(url = self.ip + "/json/state")
        data = r.json()
        r = data['seg'][0]['col'][0][0]
        g = data['seg'][0]['col'][0][1]
        b = data['seg'][0]['col'][0][2]
        return r,g,b