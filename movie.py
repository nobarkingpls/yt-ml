import sys

amazon_path = str(sys.argv[1])

from yt_mmc_movie import movie_mmc
from yt_movie import movie_mec
from yt_movie_images import movie_images

movie_images(amazon_path)
movie_mmc(amazon_path)
movie_mec()

