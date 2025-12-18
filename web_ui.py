import os
from flask import Flask, render_template, request, jsonify, send_file
import ffmpeg
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'resized_videos'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def resize_video(input_folder, video_name, filename_suffix='_resized', size=[1,1]):
    video_full_path = os.path.join(input_folder, video_name)
    filename, extension = os.path.splitext(video_name)
    extension = '.mp4'
    output_folder = app.config['OUTPUT_FOLDER']
    output_file_name = os.path.join(output_folder, filename + filename_suffix + extension)
    
    try:
        print(f'Processing: {video_full_path}')
        probe = ffmpeg.probe(video_full_path)
        vid_size = float(probe['format']['size'])

        i = ffmpeg.input(video_full_path)
        ffmpeg.output(i, output_file_name,
                        **{'c:v': 'libx264', 's': f'{size[0]}x{size[1]}', 'c:a': 'aac'}
                        ).overwrite_output().run()

        if os.path.getsize(output_file_name) <= vid_size:
            return output_file_name
        return output_file_name
    except Exception as e:
        print(f'Error processing video: {e}')
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resize', methods=['POST'])
def resize():
    try:
        width = int(request.form.get('width', 700))
        height = int(request.form.get('height', 566))
        
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        results = []
        errors = []
        
        for file in files:
            if file and file.filename.endswith('.mp4'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                output_file = resize_video(app.config['UPLOAD_FOLDER'], filename, size=[width, height])
                
                if output_file:
                    results.append(os.path.basename(output_file))
                    # Clean up uploaded file
                    os.remove(filepath)
                else:
                    errors.append(f'Failed to process {filename}')
            else:
                errors.append(f'{file.filename} is not an MP4 file')
        
        response = {
            'success': len(results) > 0,
            'processed': results,
            'errors': errors,
            'total': len(results)
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/list_outputs')
def list_outputs():
    files = [f for f in os.listdir(app.config['OUTPUT_FOLDER']) if f.endswith('.mp4')]
    return jsonify({'files': files})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
