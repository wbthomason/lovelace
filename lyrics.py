from Naked.toolshed.shell import muterun_rb
import sys
import re
import random
import os

ngram_length = 2
tag_regex = re.compile("\[[^\n]*?\]|[^\n]*?\]|\[[^\n]*?")

def get_lyrics(artist_name):
    artist_nameq = '"' + artist_name + '"'
    print("Retrieving lyrics for: {}".format(artist_nameq))
    if os.path.exists(artist_name):
        with open(artist_name, 'r') as artist_file:
            return list(filter(lambda x: len(x) > 0, artist_file.read().split()))
    rapgenius_result = muterun_rb('getLyrics.rb', artist_nameq)
    if rapgenius_result.exitcode != 0:
        print("Error retrieving lyrics: " + rapgenius_result.stderr.decode("utf-8"))
        sys.exit(-1)
    lyrics = tag_regex.sub("", rapgenius_result.stdout.decode("utf-8"))
    with open(artist_name, 'w') as artist_file:
        artist_file.write(lyrics)
    words = lyrics.split()
    return  list(filter(lambda x: len(x) > 0, words))

# This can probably be optimized to be single-pass
def make_ngrams(words):
    ngrams = {}
    for n in range(1, ngram_length + 1):
        grams = [words[x:x+n] for x in range(len(words) - n)]
        for i, ngram in enumerate(grams):
            postgrams = [words[i + n: i + n + j] if len(words) > i + n + j else [] for j in range(1, ngram_length + 1)]
            key = " ".join(ngram)
            if key in ngrams:
                ngrams[key].append(postgrams)
            else:
                ngrams[key] = [postgrams]
    return ngrams

def check_rhyme(song):
    return True

def check_rhythm(song):
    return True

def generate_lyrics(corpus, length):
    random.seed()
    song = []
    curr = random.choice(list(corpus.keys()))
    for i in range(length):
        song.append(curr)
        follows = random.choice(corpus[curr])
        size = random.randint(1, min(ngram_length, len(follows)))
        curr = " ".join(follows[size - 1])
    return song

def make_song(artist_name):
    raw_words = get_lyrics(artist_name)
    print("Got lyrics!")
    lyric_ngrams = make_ngrams(raw_words)
    print("Made ngrams!")
    song_length = random.randint(50,500)
    raw_song = " ".join(generate_lyrics(lyric_ngrams, song_length))
    song = ""
    for c in raw_song:
        if c.isupper() and c != "I":
            song += "\n"
        song += c
    return song

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Incorrect usage. Please provide the name of an artist to emulate")
    else:
       print(make_song(" ".join(sys.argv[1:])))
