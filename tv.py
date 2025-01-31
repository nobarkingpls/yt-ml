import sys

amazon_path = str(sys.argv[1])

from yt_mmc_series import series_mmc
from yt_mmc_season import season_mmc
from yt_mmc_episode import episode_mmc
from yt_series import series_mec
from yt_season import season_mec
from yt_episode import episode_mec
from yt_episode_images import episode_images

episode_images(amazon_path)
series_mmc(amazon_path)
series_mec()
season_mmc()
season_mec()
episode_mmc()
episode_mec()
