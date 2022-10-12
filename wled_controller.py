import requests

class WLEDController():
    """Controller for WLED devices.

    Attributes:
        ip (string): The IP address of the WLED device.

    """

    def __init__(self, ip):
        self.ip = ip
        self.wledControlURL = ip + "/win"
        self.wledStateURL = ip + "/json/state"

    def set_color(self, r, g, b):
        """Sets a new color. WLED already smoothly transitions between colors.

        Args:
            r (int): The new red value.
            g (int): The new green value.
            b (int): The new blue value.

        """
        requests.get(url = self.wledControlURL + "&R=%d&G=%d&B=%d" % (r, g, b))

    def get_color(self):
        """Returns the current color.

        Returns:
            tuple: (R, G, B). The current color.

        """
        r = requests.get(url = self.wledStateURL)
        data = r.json()
        r = data['seg'][0]['col'][0][0]
        g = data['seg'][0]['col'][0][1]
        b = data['seg'][0]['col'][0][2]
        return r,g,b