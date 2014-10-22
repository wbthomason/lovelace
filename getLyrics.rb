require 'rapgenius'
artist_name = ARGV[0]
song_results = RapGenius.search_by_artist(artist_name)

if song_results.length == 0
    puts "Found nothing for " + artist_name
    exit(-1)
end    

artist = song_results[0].artist
songs = artist.songs

i = 2
next_songs =[]
loop {
    next_songs = artist.songs(page: i)
    break if next_songs == []
    songs += next_songs
    i += 1
}

lyrics = songs.map { |song| song.lines.map { |line| if line.lyric[0] != "[" and line.lyric[0] != "\n" then line.lyric end } }
puts lyrics
