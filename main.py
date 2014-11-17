from lyrics import make_song
import sys

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Incorrect usage. Please provide the name of an artist to emulate")
    else:
       artist = " ".join(sys.argv[1:])
       song = make_song(artist)
       song_string ='"{}", by {}\n\n'.format(song[0], artist)
       song_string += "[Chorus]\n\n"
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
