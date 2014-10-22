from Naked.toolshed.shell import muterun_rb
import sys

ngram_length = 4

def get_lyrics(artist_name):
    artist_name = '"' + artist_name + '"'
    print("Retrieving lyrics for: {}".format(artist_name))
    rapgenius_result = muterun_rb('getLyrics.rb', artist_name)
    if rapgenius_result.exitcode != 0:
        print("Error retrieving lyrics: " + rapgenius_result.stderr.decode("utf-8"))
        sys.exit(-1)
    return filter(lambda x: len(x) > 0, rapgenius_result.stdout.decode("utf-8").split("\n"))

def make_ngrams(lyrics):
    ngrams = []
    for i in range(2, ngram_length + 1):
        unique_igrams = set()
        for lyric in lyrics:
            igrams = [lyric[x:x+i] for x in range(len(lyric))]
            unique_igrams.update(igrams)
        ngrams.append(unique_igrams)
    return ngrams

def check_rhyme():
    return True

def check_rhythm():
    return True

def generate_lyrics():
    return "No"

def make_song(artist_name):
    raw_lyrics = get_lyrics(artist_name)
    lyric_ngrams = make_ngrams(raw_lyrics)
    candidates = generate_lyrics(lyric_ngrams)
    return [song for song in candidates if check_rhyme(song, raw_lyrics) and check_rhythm(song, raw_lyrics)]
    
if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Incorrect usage. Please provide the name of an artist to emulate")
    else:
       print(make_song(" ".join(sys.argv[1:])))
