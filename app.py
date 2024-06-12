from flask import Flask, render_template, request, send_file
import io
import os
from pytube import YouTube
import ffmpeg
import re


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        download_location = "downloads"

        def on_complete(stream, file_path):
            title = re.sub("[^0-9a-zA-Z]+", "_", stream.title)
            print(f"title in on complete: {title}")
            convert = (
                ffmpeg.input(download_location + "/" + title + ".mp4")
                .output(download_location + "/" + title + ".mp3", loglevel="quiet")
                .run(overwrite_output=True)
            )

        def progress(strem, chunk, bytes_remaining):
            print(chunk)

        input = request.form.get("url")
        try:
            yt = YouTube(
                input,
                on_complete_callback=on_complete,
                on_progress_callback=progress,
                use_oauth=True,
                allow_oauth_cache=True,
            )
        except:
            error = "That Youtube URL does not work"
            return render_template("index.html", error=error)

        audio_streams = yt.streams.filter(type="audio", subtype="mp4")
        best_stream = audio_streams[:-1][0]
        # get rid of all weird characters
        title = re.sub("[^0-9a-zA-Z]+", "_", best_stream.title)
        # download the mp4
        filename = best_stream.download(download_location, filename=title + ".mp4")
        # location of mp4 file
        mp4_file_location = download_location + "/" + title + ".mp4"
        # remove the mp4 file, on complete callback already converted it to an mp3
        os.remove(mp4_file_location)
        # location of mp3 file
        mp3_file = download_location + "/" + title + ".mp3"
        # make sure file exists
        if os.path.isfile(mp3_file):

            # trick to use send file and also delete the mp3
            return_data = io.BytesIO()
            with open(mp3_file, "rb") as fo:
                return_data.write(fo.read())
            return_data.seek(0)

            # remove the mp3 file
            os.remove(mp3_file)
            # send the file as an attachment
            return send_file(
                return_data,
                as_attachment=True,
                download_name=title + ".mp3",
            )
        error = "mp3 could not be downloaded"
        return render_template("index.html", error=error)

    else:
        return render_template("index.html")
