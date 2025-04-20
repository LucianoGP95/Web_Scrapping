postprocessors = [
    {
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    },
    {'key': 'FFmpegMetadata'},
    {'key': 'EmbedThumbnail'},
]

postprocessors[0]['postprocessor_args'] = ['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11']

print(postprocessors[0])