import pytube
import subprocess
import os
import concurrent.futures
def transfer_file_to_device(local_path, device_path):
    # Ensure adb is running
    subprocess.run(["adb", "start-server"])

    # Push the file to the device
    result = subprocess.run(["adb", "push", local_path, device_path], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"File successfully transferred to {device_path}")
    else:
        print(f"Error transferring file: {result.stderr}")

# Example usage
# local_file_path = "path/to/your/local/file.txt"
# device_file_path = "/sdcard/Download/file.txt"  # The path on your device

# transfer_file_to_device(local_file_path, device_file_path)


# where to save
SAVE_PATH = r"C:\Users\jamel\Downloads"
# SAVE_PATH = r"This PC\jamel's S21\Internal storage\Youtube"
videos_you_want=tuple()
# link of the video to be downloaded
link = "https://www.youtube.com/live/1_eLAj-ptPU?si=STVOxcWRn9qYBics"

def download_video(link:str,download_path:str):
    try:
        # object creation using YouTube
        yt = pytube.YouTube(link)
        mp4_streams = yt.streams.filter(file_extension='mp4', type='video', progressive=True).order_by(
            'resolution').desc()
        mp4_streams=[stream for stream in mp4_streams if stream.filesize/1_000_000_000<=1]
        d_video: pytube.streams.Stream = mp4_streams[0]
        d_video.download(output_path=SAVE_PATH)
    except Exception as e:
        # to handle exception
        print(e)

with concurrent.futures.ProcessPoolExecutor() as executor:
    executor.map(download_video, videos_you_want,)


# download_in_chunks(d_video,SAVE_PATH,3)
# downloading the video
# d_video.download(output_path=SAVE_PATH)
