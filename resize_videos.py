import os
import sys
import ffmpeg

def resize_video(input_folder, video_name, filename_suffix='_resized', size=[1,1]):

    video_full_path = os.path.join(input_folder, video_name)
    filename, extension = os.path.splitext(video_name)
    extension = '.mp4'
    output_folder = os.getcwd()+'/resized_videos'
    output_file_name = os.path.join(output_folder, filename + filename_suffix + extension)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    try:
        print(video_full_path, os.path.exists(video_full_path))
        probe = ffmpeg.probe(video_full_path)
        vid_size = float(probe['format']['size'])

        i = ffmpeg.input(video_full_path)
        ffmpeg.output(i, output_file_name,
                        **{'c:v': 'libx264', 's': f'{size[0]}x{size[1]}', 'c:a': 'aac'}
                        ).overwrite_output().run()

        if os.path.getsize(output_file_name) <= vid_size:
            return output_file_name
    except FileNotFoundError as e:
        print('File not found', e)
        return False

if __name__ == '__main__':

    input_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()+'/vids_to_resize'
    
    if os.path.isfile(input_path):
        # Direct file input
        if input_path.endswith('.mp4'):
            input_folder = os.path.dirname(input_path)
            video_name = os.path.basename(input_path)
            print(f'Processing single file: {video_name}')
            resize_video(input_folder, video_name, size=[700, 566])
        else:
            print(f'Error: {input_path} is not an MP4 file')
    elif os.path.isdir(input_path):
        # Folder input - enumerate .mp4 files
        vids_to_compress = [f for f in os.listdir(input_path) if f.endswith('.mp4')]
        print(f'Found {len(vids_to_compress)} MP4 files: {vids_to_compress}')
        for i, vid in enumerate(vids_to_compress):
            print(f'Compressing {i+1}/{len(vids_to_compress)}')
            resize_video(input_path, vid, size=[700, 566])
    else:
        print(f'Error: {input_path} is not a valid file or directory')


