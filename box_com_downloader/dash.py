# Box.com Downloader
# Copyright (C) 2026 seriaati
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

import math
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

import urllib3

WORKERS = 8


def _iso_duration_seconds(value):
    # e.g. PT15M37.6S
    match = re.fullmatch(r"PT(?:([\d.]+)H)?(?:([\d.]+)M)?(?:([\d.]+)S)?", value)
    hours, minutes, seconds = (float(g or 0) for g in match.groups())
    return hours * 3600 + minutes * 60 + seconds


def download_dash(manifest_url, path, auth=None):
    """
    Downloads the best video and audio tracks of a DASH manifest and muxes them into path with ffmpeg
    """
    http = urllib3.PoolManager(maxsize=WORKERS)
    headers = {"Authorization": auth} if auth else None
    base_url, query = manifest_url.split("?", 1)
    base_url = base_url.rsplit("/", 1)[0] + "/"

    def fetch(url):
        r = http.request("GET", url, headers=headers)
        if r.status != 200:
            raise RuntimeError("Failed to download {} (HTTP {})".format(url, r.status))
        return r.data

    root = ET.fromstring(fetch(manifest_url))
    total_seconds = _iso_duration_seconds(root.get("mediaPresentationDuration"))

    track_paths = []
    for adaptation_set in root.findall(".//{*}AdaptationSet"):
        best = max(
            adaptation_set.findall("{*}Representation"),
            key=lambda r: int(r.get("bandwidth")),
        )
        template = best.find("{*}SegmentTemplate")
        segment_seconds = int(template.get("duration")) / int(template.get("timescale"))
        start = int(template.get("startNumber", 1))
        count = math.ceil(total_seconds / segment_seconds)

        track_path = "{}.{}.part".format(path, adaptation_set.get("contentType"))
        segments = [template.get("initialization")] + [
            template.get("media").replace("$Number$", str(n))
            for n in range(start, start + count)
        ]
        with open(track_path, "wb") as out, ThreadPoolExecutor(WORKERS) as pool:
            # map yields in segment order, so chunks are written sequentially
            data = pool.map(
                fetch, [base_url + segment + "?" + query for segment in segments]
            )
            for i, chunk in enumerate(data):
                print(
                    "\r{}: {}/{}".format(
                        adaptation_set.get("contentType"), i + 1, len(segments)
                    ),
                    end="",
                    flush=True,
                )
                out.write(chunk)
        print()
        track_paths.append(track_path)

    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for track_path in track_paths:
        cmd += ["-i", track_path]
    cmd += (
        ["-map", "0"]
        + (["-map", "1"] if len(track_paths) > 1 else [])
        + ["-c", "copy", path]
    )
    subprocess.run(cmd, check=True)
    for track_path in track_paths:
        os.remove(track_path)
