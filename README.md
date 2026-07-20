# box-pdf-downloader

This repo is a fork of razocrackers' [box.com-downloader](https://github.com/razorcrackers/box.com-downloader), containing fixes that allow it to work with the latest version of box.com and the latest version of Selenium. I also packaged it as a pip-installable tool for easier installation and usage.

This application can scrape and download protected docx or pdf files in box.com and save it as an editable PDF file.

## Installation

Any Python package manager can be used to install this tool. Here are some examples:

```sh
uv tool install box-pdf-downloader

pipx install box-pdf-downloader

pip install box-pdf-downloader
```

## Example Usage

Use either the `box-pdf-downloader` command or its shorter `bpd` alias:

```sh
box-pdf-downloader https://app.box.com/s/hs5de51wub2htrcl0hxn1wir4zpmf3wj

bpd https://app.box.com/s/hs5de51wub2htrcl0hxn1wir4zpmf3wj
```

The PDF is saved to `dl_files/` in the current directory.
