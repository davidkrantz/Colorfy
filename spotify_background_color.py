import numpy as np
import scipy.misc as sp
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from PIL import Image


class SpotifyBackgroundColor():
    """Analyzes an image and finds a fitting background color.

    Main use is to analyze album artwork and calculate the background
    color Spotify sets when playing on a Chromecast.

    Attributes:
        img (ndarray): The image to analyze.

    """

    def __init__(self, img, format='RGB', image_processing_size=None):
        """Prepare the image for analyzation.

        Args:
            img (ndarray): The image to analyze.
            format (str): Format of `img`, either RGB or BGR.
            image_processing_size: (tuple): Process image or not.
                tuple as (width, height) of the output image (must be integers)

        Raises:
            ValueError: If `format` is not RGB or BGR.

        """
        if format == 'RGB':
            self.img = img
        elif format == 'BGR':
            self.img = self.img[..., ::-1]
        else:
            raise ValueError('Invalid format. Only RGB and BGR image '\
                             'format supported.')

        if image_processing_size:
            img = Image.fromarray(self.img)
            self.img = np.asarray(img.resize(image_processing_size, Image.BILINEAR))

    def best_color(self, k=8, color_tol=10, plot=False):
        """Returns a suitable background color for the given image.

        Uses k-means clustering to find `k` distinct colors in
        the image. A colorfulness index is then calculated for each
        of these colors. The color with the highest colorfulness
        index is returned if it is greater than or equal to the
        colorfulness tolerance `color_tol`. If no color is colorful
        enough, a gray color will be returned. Returns more or less
        the same color as Spotify in 80 % of the cases.

        Args:
            k (int): Number of clusters to form.
            color_tol (float): Tolerance for a colorful color.
                Colorfulness is defined as described by Hasler and
                Süsstrunk (2003) in https://infoscience.epfl.ch/
                record/33994/files/HaslerS03.pdf.
            plot (bool): Plot the original image, k-means result and
                calculated background color. Only used for testing.

        Returns:
            tuple: (R, G, B). The calculated background color.

        """
        artwork = self.img.copy()
        self.img = self.img.reshape((self.img.shape[0]*self.img.shape[1], 3))

        clt = KMeans(n_clusters=k)
        clt.fit(self.img)
        hist = self.find_histogram(clt)
        centroids = clt.cluster_centers_

        colorfulness = [self.colorfulness(color[0], color[1], color[2]) for color in centroids]
        max_colorful = np.max(colorfulness)

        if max_colorful < color_tol:
            # If not colorful, set to gray
            best_color = [230, 230, 230]
        else:
            # Pick the most colorful color
            best_color = centroids[np.argmax(colorfulness)]

        if plot:
            bar = np.zeros((50, 300, 3), dtype='uint8')
            square = np.zeros((50, 50, 3), dtype='uint8')
            start_x = 0

            for (percent, color) in zip(hist, centroids):
                # Plot the relative percentage of each cluster
                end_x = start_x + (percent * 300)
                bar[:, int(start_x):int(end_x)] = color
                start_x = end_x
            square[:] = best_color

            plt.figure()
            plt.subplot(1, 3, 1)
            plt.title('Artwork')
            plt.axis('off')
            plt.imshow(artwork)

            plt.subplot(1, 3, 2)
            plt.title('k = {}'.format(k))
            plt.axis('off')
            plt.imshow(bar)

            plt.subplot(1, 3, 3)
            plt.title('Color {}'.format(square[0][0]))
            plt.axis('off')
            plt.imshow(square)
            plt.tight_layout()

            plt.plot()
            plt.show(block=False)

        return best_color[0], best_color[1], best_color[2]

    def find_histogram(self, clt):
        """Create a histogram of image.

        Args:
            clt (array_like): Input data.

        Returns:
            array: The values of the histogram.

        """
        num_labels = np.arange(0, len(np.unique(clt.labels_)) + 1)
        hist, _ = np.histogram(clt.labels_, bins=num_labels)

        hist = hist.astype('float')
        hist /= hist.sum()

        return hist

    def colorfulness(self, r, g, b):
        """Returns a colorfulness index of given RGB combination.

        Implementation of the colorfulness metric proposed by
        Hasler and Süsstrunk (2003) in https://infoscience.epfl.ch/
        record/33994/files/HaslerS03.pdf.

        Args:
            r (int): Red component.
            g (int): Green component.
            b (int): Blue component.

        Returns:
            float: Colorfulness metric.

        """
        rg = np.absolute(r - g)
        yb = np.absolute(0.5 * (r + g) - b)

        # Compute the mean and standard deviation of both `rg` and `yb`.
        rg_mean, rg_std = (np.mean(rg), np.std(rg))
        yb_mean, yb_std = (np.mean(yb), np.std(yb))

        # Combine the mean and standard deviations.
        std_root = np.sqrt((rg_std ** 2) + (yb_std ** 2))
        mean_root = np.sqrt((rg_mean ** 2) + (yb_mean ** 2))

        return std_root + (0.3 * mean_root)
