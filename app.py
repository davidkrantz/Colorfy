from flask import Flask, jsonify, render_template, request
import os
from time import sleep
from multiprocessing import Process
import configparser
from spotify_background_color import SpotifyBackgroundColor
from current_spotify_playback import CurrentSpotifyPlayback, NoArtworkException
from led_controller import LEDController


app = Flask(__name__)

CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI')
REFRESH_TOKEN = os.environ.get('SPOTIPY_REFRESH_TOKEN')


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/spotify')
def spotify():
    global p
    if not p.is_alive():
        p = Process(target=main_spotify, args=())
        p.start()
    return render_template('spotify.html')


@app.route('/manual')
def manual():
    global p
    try:
        p.terminate()
    except AttributeError:
        pass
    return render_template('manual.html')


@app.route('/color', methods=['GET', 'POST'])
def color():
    if request.method == 'POST':
        data = request.json
        r = data['r']
        g = data['g']
        b = data['b']
        led.set_color(r, g, b, delay=0)
        return jsonify(status='updating', data=data)
    else:
        curr_r, curr_g, curr_b = led.get_color()
        return jsonify(status='current', data={'r': curr_r, 'g': curr_g, 'b': curr_b})


@app.route('/off')
def off():
    global p
    try:
        p.terminate()
    except AttributeError:
        pass
    led.set_color(0, 0, 0)
    return render_template('off.html')


def main_spotify():
    old_song_id = ''
    while True:
        spotify.update_current_playback()
        if spotify.connected_to_chromecast(name):
            if spotify.new_song(old_song_id):
                try:
                    artwork = spotify.get_artwork()
                    background_color = SpotifyBackgroundColor(
                        img=artwork, image_processing_size=(100, 100))
                    r, g, b = background_color.best_color(
                        k=8, color_tol=0)
                except NoArtworkException:
                    r, g, b = 255, 255, 255
                led.set_color(r, g, b)
                old_song_id = spotify.get_current_song_id()
        else:
            old_song_id = ''
            r, g, b = led.get_color()
            if r != 0 or g != 0 or b != 0:
                led.set_color(0, 0, 0)
        sleep(2)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    GPIO_PINS = config['GPIO PINS']
    red_pin = int(GPIO_PINS['red_pin'])
    green_pin = int(GPIO_PINS['green_pin'])
    blue_pin = int(GPIO_PINS['blue_pin'])
    name = config['CHROMECAST']['name']

    led = LEDController(red_pin, green_pin, blue_pin)
    spotify = CurrentSpotifyPlayback(CLIENT_ID, CLIENT_SECRET,
                                     REDIRECT_URI, REFRESH_TOKEN)

    p = Process(target=main_spotify, args=())

    app.run(host='0.0.0.0')
