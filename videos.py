import youtube_dl
import urllib.request as urlreq
import os
import subprocess
import re
import speech_recognition as sr
from bs4 import BeautifulSoup
from moviepy.editor import *

def get_video_from_search(artist, song, onlyAudio=False, outputFile="temp.mp4"):
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
    if onlyAudio:
        subprocess.call(["youtube-dl"
            , "-x"
            , "-o{}".format(outputFile)
            , url])
    else:
        subprocess.call(["youtube-dl"
            , "-o{}".format(outputFile)
            , url])

def get_video_from_url(url, onlyAudio=False, outputFile="temp.mp4"):
    if onlyAudio:
        subprocess.call(["youtube-dl"
            , "-x"
            , "-o{}".format(outputFile)
            , url])
    else:
        subprocess.call(["youtube-dl"
            , "-o{}".format(outputFile)
            , url])

def get_subtitles_from_url(url):
    subprocess.call(["youtube-dl"
        , "--write-subs"
        , "--skip-download"
        , url])

def parse_interval(interval):
    start = 0
    end = 0
    on_start = True
    matches = list(re.finditer(r"\d*:\d*:\d*", interval))
    times = matches[0].group(0).split(":")
    start += int(times[2])
    start += 60*int(times[1])
    start += 3600*int(times[0])

    times = matches[1].group(0).split(":")
    end += int(times[2])
    end += 60*int(times[1])
    end += 3600*int(times[0])

    return [start, end]

def parse_subtitles(filepath):
    subtitle_file = open(filepath, 'r')
    intervals = []
    lyrics = ""
    interval = []
    words_to_intervals = []
    count = 0
    for line in subtitle_file:
        trimmed = line.strip()
        trimmed = trimmed.lower()
        if trimmed == "":
            intervals.append([interval, lyrics])
            words = lyrics.split()
            index = len(intervals)-1
            for word in words:
                words_to_intervals.append([word, index])
            interval = []
            lyrics = ""
            count = 0
            continue
        elif count == 0: # number
            pass
        elif count == 1:
            interval = parse_interval(trimmed)
        elif count > 1:
            lyrics += " " + trimmed
        count += 1
    return (intervals, words_to_intervals)

def split_video(subtitle_file, video_file):
    (subtitle_intervals,mapping) = parse_subtitles(subtitle_file)
    full_clip = VideoFileClip("temp.mp4")
    subclips = []
    full_song = ""
    for interval in subtitle_intervals:
        start = interval[0][0]
        stop = interval[0][1]
        full_song += interval[1]
        print(start)
        print(stop)
        subclips.append(full_clip.subclip(start,stop))
    return (subtitle_intervals, mapping, full_song, subclips)

def stream(f):
    for line in f:
        for word in line.split():
            yield word.lower()

def in_text(buff, words):
    print("in_text: buff={}".format(buff))
    num_matched = []
    max_matched = []
    offset = 0
    for (i, mapping) in enumerate(words):
        word = mapping[0]
        if offset < len(buff) and word == buff[offset]:
                num_matched.append(mapping)
                offset += 1
        elif len(num_matched) > len(max_matched):
                max_matched = num_matched[:]
                num_matched = []
                offset = 0
    return max_matched

def splice_video(lyrics_file, subtitle_file, video_file):
    (subtitle_intervals,mapping,full_song,subclips) = split_video(subtitle_file,video_file)

    print('mapping=')
    print(mapping)
    video = None

    f = open(lyrics_file, 'r')
    buff = []
    for word in stream(f):
        print("splice_video: on word '{}'".format(word))
        buff.append(word)
        max_match = in_text(buff, mapping)
        if len(max_match) == len(buff):
            pass
        else:
            # lookup all words and get their intervals
            indices = set()
            for item in max_match:
                indices.add(item[1])

            sorted_indices = []
            for index in indices: sorted_indices.append(index)
            sorted_indices.sort()
            print("splice_video: indices={}".format(sorted_indices))

            clips = []
            for index in sorted_indices:
                clips.append(subclips[index])
            print("len(clips)={}".format(len(clips)))
            clip_video = concatenate(clips)
            if video == None:
                video = clip_video
            else: # add to end
                video_list = [video]
                video_list.extend(clips)
                video = concatenate(video_list)

            buff = [word] # restart the buffer

    video.to_videofile("output.mp4")


#get_video_from_search("Idina Menzel", "Let it go")
#get_video_from_url("http://www.youtube.com/watch?v=moSFlvxnbgk")
#intervals = parse_subtitles("let_it_go.srt")
#for interval in intervals:
#    print(interval)

splice_video("Idena Menzel", "let_it_go.srt", "temp.mp4")
