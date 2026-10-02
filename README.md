# box-pdf-downloader

This repo is a fork of razocrackers' [box.com-downloader](https://github.com/razorcrackers/box.com-downloader), containing fixes that allow it to work with the latest version of box.com and the latest version of Selenium. I also packaged it as a pip-installable tool for easier installation and usage.

This application can download protected PDF and docx files from box.com as text-based (searchable, selectable) PDFs. It can also download video files, which are saved as MP4.

## Installation

Any Python package manager can be used to install this tool. Here are some examples:

```sh
uv tool install box-pdf-downloader

pipx install box-pdf-downloader

pip install box-pdf-downloader
```

Downloading videos additionally requires [ffmpeg](https://ffmpeg.org/download.html) to be installed and available on your `PATH`.

## Example Usage

Use either the `box-pdf-downloader` command or its shorter `bpd` alias:

```sh
box-pdf-downloader https://app.box.com/s/hs5de51wub2htrcl0hxn1wir4zpmf3wj

bpd https://app.box.com/s/hs5de51wub2htrcl0hxn1wir4zpmf3wj
```

The file is saved to `dl_files/` in the current directory.
