import pytube
import subprocess
import os
import concurrent.futures
import multiprocessing
import gmail
# download tools from here https://developer.android.com/tools/releases/platform-tools
# then windows+x > system > advanced system > Environment variables > system vairables> edit PATH to include platformtoolslatest\platformtools pth
# then plug in phone and run adb devices
_,_,youtube=gmail.main()
def transfer_file_to_device(local_path, device_path,delete=True):
    # Ensure adb is running
    subprocess.run(["adb", "start-server"])

    # Push the file to the device
    result = subprocess.run(["adb", "push", local_path, device_path], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"File successfully transferred to {device_path}")
        if delete:
            os.remove(local_path)

    else:
        print(f"Error transferring file: {result.stderr}")
    return result.returncode

DOWNLOAD_PLAYLIST='Blick'
COM_PATH = r"C:\Youtube"
PHONE_PATH="/storage/emulated/0/Youtube"


def download_video(link:str):
    try:
        # object creation using YouTube
        yt = pytube.YouTube(link)
        mp4_streams = yt.streams.filter(file_extension='mp4', type='video', progressive=True).order_by(
            'resolution').desc()
        mp4_streams=[stream for stream in mp4_streams if (stream.filesize/1_000_000_000)<=1]
        d_video: pytube.streams.Stream = mp4_streams[0]
        d_video.download(output_path=COM_PATH)
    except Exception as e:
        # to handle exception
        print(e)

def download_multiple(videos_you_want):
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        executor.map(download_video, videos_you_want)

def download_playlist(playlist_url):
    download_multiple(pytube.Playlist(playlist_url))

if __name__ == '__main__':
    playlist_url=gmail.get_playlist_url(youtube,DOWNLOAD_PLAYLIST)
    download_playlist(playlist_url)
    return_check=0
    for file in [os.path.join(COM_PATH,file) for file in os.listdir(COM_PATH)]:
        return_check+=transfer_file_to_device(file,PHONE_PATH)
    if return_check==0:
        gmail.empty_playlist(youtube, DOWNLOAD_PLAYLIST)