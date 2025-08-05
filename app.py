from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import re

app = Flask(__name__)

def maak_bestandsnaam(titel: str, taal: str, extensie: str) -> str:
    # Verwijder ongeldige tekens voor bestandsnamen
    veilig = re.sub(r'[\\/*?:"<>|]', '_', titel)
    return f"{veilig}_{taal}.{extensie}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    formaat = request.form.get("format", "srt")  # 'srt' of 'txt'

    if not url:
        return "Geen URL ingevoerd", 400

    ydl_opts = {
        'writesubtitles': True,
        'skip_download': True,
        'subtitleslangs': ['nl', 'en'],
        'subtitlesformat': formaat,
        'outtmpl': '%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            titel = info.get("title", "ondertitel")
            taal = "nl" if "nl" in info.get("subtitles", {}) else "en"
            bestandsnaam = maak_bestandsnaam(titel, taal, formaat)

        if not os.path.exists(bestandsnaam):
            return "Ondertitelbestand niet gevonden", 500

        return send_file(bestandsnaam, as_attachment=True)

    except Exception as e:
        return f"Fout tijdens downloaden: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
