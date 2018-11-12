# Colorfy
A small program written in Python 3 that sets the color of your LED-strip to the background color that Spotify sets when playing on a Chromecast. It analyzes the album artwork and computes the correct background color (same as Spotify sets) in about 80 % of the cases.

The program uses k-means clustering to find distinct colors in the artwork and then computes a colorfulness index as defined by [Hasler and Süsstrunk (2003)](https://infoscience.epfl.ch/record/33994/files/HaslerS03.pdf) for each of the colors. The color with the highest index is then set to the LED-strip if it is greater than or equal to a given colorfulness tolerance.

## Images
<img src="images/rhcp.jpg">
<p float="center">
  <img src="images/color_gradient.gif" width="481" height="271"/>
  <img src="images/5sos.jpg" width="409" height="271"/>
</p>
<img src="images/khalid.jpg">
<img src="images/falco.jpg">

## Running locally
### Connect LED-strip to Raspberry Pi
Many different LED-strips can be used with this program. The only requirement is that it needs to connect with three data pins to the Raspberry Pi, i.e. one data pin for each of the color channels R, G and B.

I used the [IKEA Dioder](https://www.ikea.com/us/en/catalog/categories/series/25230/) LED-strip which I connected to my Raspberry Pi 3 model B+ by following [this](https://dordnung.de/raspberrypi-ledstrip/) guide.

### Clone/download repository
When the hardware is set up, you will need to [download](https://github.com/davidkrantz/Colorfy/archive/master.zip) or clone the repository, the latter can be done by typing
```
git clone https://github.com/davidkrantz/Colorfy.git
```
in your terminal.

### Create a Spotify application
1. Go to your [Spotify dashboard](https://developer.spotify.com/dashboard/applications).
2. Create a new application.
3. Press *EDIT SETTINGS* and set the redirect URI to for example `http://localhost/` and save it.

### Set environment variables
These are found inside your Spotify application and are preferably added to `~/.profile` (or something similar like `~/.bash_login` or `~/.bashrc`) on your Raspberry Pi.
```
export SPOTIPY_CLIENT_ID=''
export SPOTIPY_CLIENT_SECRET=''
export SPOTIPY_REDIRECT_URI=''
```

### Get refresh token
1. Run the included `setup.py` script with a string as argument. This can be any string, but preferably something your will remember (for example your Spotify username to which you wish to connect the Spotify application to) since this will make it easy to find the generated refresh token if you lose it. So for example:
```
python setup.py spotify_username
```

2. A page will open. Accept the terms and then copy the URL you are redirected to into the terminal and hit enter.

3. Your refresh token will then be printed in the terminal. It will also be saved in a file called `.cache-{spotify_username}` inside the active directory.

4. Set the refresh token as an environment variable just as the ones before with `export SPOTIPY_REFRESH_TOKEN=''`.

### Set up config file
1. Copy and rename `config.ini.default` to `config.ini`.

2. Edit `config.ini` such that the used GPIO pins and Chromecast name matches yours, for example:
```
[GPIO PINS]
red_pin = 17
green_pin = 22
blue_pin = 24

[CHROMECAST]
name = Chromecast Krantz
```

### Run it
1. First you will have to install the needed packages. These are listed in the `requirements.txt` file and *should* be easily installed using `pip` with
```
pip3 install -r /path/to/requirements.txt
```
**NOTE:** The Spotipy package needs to be installed directly from GitHub, otherwise an old version will be installed
```
pip3 install git+https://github.com/plamere/spotipy.git --upgrade
```

2. Initialize `pigpiod` on your Raspberry Pi with `sudo pigpiod`

3. Run `main.py` together with some suitable arguments, for example
```
python3 main.py -k 8 -t 10 -s 100 100
```
which will resize the album artworks to `100x100`, find `8` distinct colors and return the most colorful color if it is greater than or equal to the colorfulness tolerance `10`. If no arguments are inputted `python3 main.py`, the default values will be used. The default values are the arguments which gave me the best result with regards to accuracy and computational time, which is why I recommend using them. But feel free to experiment with these to try to improve the accuracy!

## Starting and updating on reboot
The two previous steps can be automated by doing the following:
1. Run `sudo systemctl enable pigpiod` once on your Raspberry Pi.

2. Copy and rename `start.sh.default` to `start.sh`.

3. Edit `start.sh` such that it works on your Raspberry Pi.

4. Add `@reboot . $HOME/path/to/env/var; sh /path/to/project/start.sh > /path/to/project/logs/log.txt 2>&1` to `crontab -e`. For the logging to work you will have create a directory with `mkdir logs` inside the project folder. A file called `log.txt` in `/path/to/project/logs` will then contain the logs which can be used for debugging.
