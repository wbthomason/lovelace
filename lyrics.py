from Naked.toolshed.shell import muterun_rb
import sys
import re
import random
import os
import nltk.data
import subprocess

ngram_length = 2
tag_regex = re.compile("\[[^\n]*?\]|[^\n]*?\]|\[[^\n]*?")
nl_regex = re.compile("\n")
period_regex = re.compile("\.")

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
    lyrics = nl_regex.sub(".\n", lyrics).lower()
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
    curr = random.choice(list(corpus.keys()))
    print("curr={}".format(curr))
    def make_verse(seed):
        print("seed={}".format(seed))
        while True:
            song = []
            for i in range(length):
                song.append(seed)
                follows = random.choice(corpus[seed])
                size = random.randint(1, min(ngram_length, len(follows)))
                seed = " ".join(follows[size - 1])
            yield song
    return make_verse(curr)

def make_song(artist_name):
    raw_words = get_lyrics(artist_name)
    print("Got lyrics!")
    lyric_ngrams = make_ngrams(raw_words)
    print("Made ngrams!")
    num_verses = random.randint(3, 6)   
    verse_length = random.randint(50,150)
    verses = []
    verse_generator = generate_lyrics(lyric_ngrams, verse_length)
    verse_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
    for i in range(num_verses):
        verse = next(verse_generator)
        verse = verse_splitter.tokenize(" ".join(verse))
        verse = list(map(lambda x: period_regex.sub("", x), verse))
        verses.append(verse)
    chorus = next(generate_lyrics(lyric_ngrams, random.randint(20,50)))
    title_start = random.randint(0, len(chorus)-1)
    title_len = random.randint(1, 4)
    title = " ".join(chorus[title_start:title_start + title_len] if title_start + title_len < len(chorus) else chorus[title_start:])
    chorus = verse_splitter.tokenize(" ".join(chorus))
    chorus = list(map(lambda x: period_regex.sub("", x), chorus))
    return [title, chorus, verses]

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Incorrect usage. Please provide the name of an artist to emulate")
    else:
       artist = " ".join(sys.argv[1:])
       song = make_song(artist)
       song_string ='"{}", by {}\n\n'.format(song[0], artist)
       song_string += "[Chorus]\n"
       for line in song[1]:
           song_string += "{}\n".format(line)
       song_string += "\n"
       for i in range(1, len(song[2]) + 1):
           song_string += "[Verse {}]\n".format(i)
           for line in song[2][i-1]:
                song_string += "{}\n".format(line)
           song_string += "\n"
       print(song_string)
       #subprocess.call(["espeak", "-ven-us", "-p80", "-l4", "-k20", song_string])
