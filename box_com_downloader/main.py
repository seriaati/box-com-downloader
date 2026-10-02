# Box.com Downloader
# Copyright (C) 2018 lfasmpao
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import argparse
import os
import shutil
from importlib.metadata import version

from .dash import download_dash
from .downloader import download_file
from .scraper import Scraper, url_checker

# globals
parser = argparse.ArgumentParser(usage='%(prog)s [options]')
parser.add_argument('url', metavar='URL', type=str, help="Input box.com shared url")
parser.add_argument('--driver-path', default=None, dest='driver_location',
                    type=str, help="Specify your chrome driver path")
parser.add_argument('--wait-time', default=15, dest='wait_time',
                    type=int, help="Wait time for selenium to load in seconds (default: 15)")
parser.add_argument('--use-x11', default=False, action='store_false', dest='use_x11',
                    help='Use X11 Virtual Display (For OSX/Linux Only)')
parser.add_argument('--version', action='version', version='Box.com Downloader Version ' + version('box-com-downloader'))
parser.add_argument('--out', default=os.getcwd() + "/dl_files/",
                    dest="output_location", type=str, help="Output file folder location")


def main():
    args = parser.parse_args()
    style = "=+" * 20
    if url_checker(args.url) is False:  # url format check
        raise argparse.ArgumentTypeError('Value has to be in full url format http:// or http://')
    print(style)
    print("Box.com Downloader by @lfasmpao")

    box_object = Scraper(args.url, args.driver_location, args.use_x11, args.wait_time)
    print("Please wait for about {} seconds...".format(args.wait_time))
    box_object.load_url()
    dl_name = box_object.get_download_title()
    print(style)
    print("DATA TO BE DOWNLOADED\nTitle: {}\nBox.com URL: {}".format(dl_name, args.url))

    print(style)
    dl_url, dl_auth = box_object.get_download_url()
    print("Download URL:", dl_url)
    print(style)
    box_object.clean()  # clean

    # make directory
    directory = os.path.dirname(args.output_location)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if "manifest.mpd" in dl_url:  # video, streamed as DASH
        if shutil.which("ffmpeg") is None:
            raise SystemExit("ffmpeg is required to download videos, please install it")
        path = str(args.output_location + dl_name + ".mp4")
        print("Downloading..\nFile will be save as:", path)
        download_dash(manifest_url=dl_url, path=path, auth=dl_auth)
    else:
        print("Downloading..\nFile will be save as:",
              str(args.output_location + dl_name + ".pdf"))
        download_file(url=dl_url, path=str(args.output_location + dl_name + ".pdf"), auth=dl_auth)


if __name__ == "__main__":
    main()
