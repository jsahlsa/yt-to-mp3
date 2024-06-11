from flask import Flask, render_template, request, send_file
import io
import os
from pytube import YouTube
from tkinter import filedialog
import ffmpeg


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        download_location = "downloads"

        def on_complete(stream, file_path):
            title = stream.title
            filename = download_location + "/" + title + ".mp3"

        def progress(strem, chunk, bytes_remaining):
            print(strem, chunk, bytes_remaining)

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
        filename = best_stream.download(download_location)
        title = best_stream.title
        mp4_file = download_location + "/" + title + ".mp4"
        mp3_file = download_location + "/" + title + ".mp3"
        print(mp3_file)
        mp4_input = (
            ffmpeg.input(download_location + "/" + best_stream.title + ".mp4")
            .output(download_location + "/" + best_stream.title + ".mp3")
            .run(overwrite_output=True)
        )
        print(mp4_input[1])
        # remove mp4 file
        os.remove(mp4_file)
        if mp4_input[1] == None:

            return_data = io.BytesIO()
            with open(mp3_file, "rb") as fo:
                return_data.write(fo.read())
            return_data.seek(0)

            os.remove(mp3_file)
            return send_file(
                return_data, as_attachment=True, download_name=title + ".mp3"
            )
    else:
        return render_template("index.html")
