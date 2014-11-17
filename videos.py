import youtube_dl
import urllib.request as urlreq
import os
import subprocess
import re
import speech_recognition as sr
from bs4 import BeautifulSoup

def get_video_from_search(artist, song, onlyAudio=False):
    base = "http://www.youtube.com/results?search_sort=video_view_count&search_query="
    html_artist = "+".join(artist.split())
    html_song = "+".join(song.split())
    query = "+".join([base, html_artist, html_song, "official"])

    request = urlreq.build_opener()
    request.addheaders = [("User-agent", "Mozilla/5.0")]

    soup = BeautifulSoup(request.open(query))

    section_list = soup.find(id="section-list")
    item_section = section_list.li.ol.find_all("li", recursive=False)
    print("{} items".format(len(item_section)))

    links = []
    watch_regex = re.compile(r'^/watch\?v=.*')
    for item in item_section:
        urls = [anchor.get('href') for anchor in item.find_all('a')]
        for url in urls:
            if watch_regex.match(url) and url not in links:
                links.append(url)
    print("{} video links".format(len(links)))

    # Only use the first link for now
    url = "http://www.youtube.com" + links[0]
    subprocess.call(["youtube-dl"
        , "-x" if onlyAudio else ""
        , url])

def get_video_from_url(url, onlyAudio=False):
    subprocess.call(["youtube-dl"
        , "-x" if onlyAudio else ""
        , url])

def get_subtitles_from_url(url):
    subprocess.call(["youtube-dl"
        , "--write-subs"
        , "--skip-download"
        , url])
