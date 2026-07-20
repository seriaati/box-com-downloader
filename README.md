# Box.com PDF Downloader

This repo is a fork of razocrackers' [box.com-downloader](https://github.com/razorcrackers/box.com-downloader), containing fixes that allow it to work with the latest version of box.com.

This application can scrape and download protected pdf files in box.com and save it as an editable PDF file.

### Installation

This app requires [Python](https://python.org/) 3 to run.

Clone the repository and install the dependencies.

```sh
git clone https://github.com/lfasmpao/box.com-downloader
cd box.com-downloader
pip install -r requirements.txt
python main.py -h
```

Note: This requires chrome selenium driver in order to work, you can download and install it from [here](http://chromedriver.chromium.org/downloads)

### Example Usage

```sh
cd box.com-downloader
python main.py https://app.box.com/s/hs5de51wub2htrcl0hxn1wir4zpmf3wj
```

License
----

GNU General Public License v3.0
