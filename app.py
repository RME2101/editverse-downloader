from flask import Flask, request, render_template, send_file, after_this_request
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['url']
    format_choice = request.form.get('format', '1080') 
    
    download_folder = 'downloads'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    audio_formats = ['mp3', 'm4a', 'wav', 'flac']
    
    if format_choice in audio_formats:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format_choice,
                'preferredquality': '192',
            }],
        }
    else:
        ydl_opts = {
            'format': f'bestvideo[height<={format_choice}]+bestaudio/best[height<={format_choice}]',
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            original_filename = ydl.prepare_filename(info)
            
            base_name = original_filename.rsplit('.', 1)[0]
            if format_choice in audio_formats:
                final_filename = f"{base_name}.{format_choice}"
            else:
                final_filename = f"{base_name}.mp4"

            # This tells Flask to delete the hidden file after sending it to you
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(final_filename)
                except Exception as error:
                    print("Error removing file:", error)
                return response

            return send_file(final_filename, as_attachment=True)
            
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
