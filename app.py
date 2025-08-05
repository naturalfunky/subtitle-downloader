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

    os.makedirs("downloads", exist_ok=True)
    taal = "nl"
    ydl_format = "srt"  # yt-dlp gebruikt o.a. srt, vtt

    srt_pad = f"downloads/video.{taal}.{ydl_format}"
    txt_pad = f"downloads/video.{taal}.txt"

    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [taal],
        'subtitlesformat': ydl_format,
        'outtmpl': 'downloads/video.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            titel = info.get("title", "ondertitels")

            if not info.get("subtitles") and not info.get("automatic_captions"):
                return "Geen ondertitels gevonden", 404

            ydl.download([url])
    except Exception as e:
        return f"Fout bij downloaden: {str(e)}", 500

    # Verwerk .txt (tijdcodes strippen)
    if formaat == "txt" and os.path.exists(srt_pad):
        with open(srt_pad, encoding="utf-8") as f:
            regels = f.readlines()
        tekstregels = [r.strip() for r in regels if not r.strip().isdigit() and "-->" not in r and r.strip()]
        with open(txt_pad, "w", encoding="utf-8") as f:
            f.write("\n".join(tekstregels))

        downloadnaam = maak_bestandsnaam(titel, taal, "txt")
        return send_file(txt_pad, as_attachment=True, download_name=downloadnaam)

    # Anders: .srt teruggeven
    if os.path.exists(srt_pad):
        downloadnaam = maak_bestandsnaam(titel, taal, "srt")
        return send_file(srt_pad, as_attachment=True, download_name=downloadnaam)
    else:
        return "Bestand niet gevonden", 500

if __name__ == "__main__":
    app.run(debug=True)
