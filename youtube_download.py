import pytubefix
import subprocess
import os
import concurrent.futures
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

def progress_function(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    print(f'Download Progress: {percentage_of_completion:.2f}%')

def complete_function(stream, file_path):
    print(f'Download Complete! File saved to {file_path}')
def download_video(link:str):
    try:
        # object creation using YouTube
        yt = pytubefix.YouTube(link,on_progress_callback=progress_function,on_complete_callback=complete_function)
        mp4_streams = yt.streams.filter(file_extension='mp4', type='video', progressive=True).order_by(
            'resolution').desc()
        mp4_streams=[stream for stream in mp4_streams if (stream.filesize/1_000_000_000)<=1]
        d_video: pytubefix.streams.Stream = mp4_streams[0]
        d_video.download(output_path=COM_PATH)
    except Exception as e:
        # to handle exception
        print(e)

def download_multiple(videos_you_want):
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        executor.map(download_video, videos_you_want)

def download_playlist(playlist_url):
    download_multiple(pytubefix.Playlist(playlist_url))

if __name__ == '__main__':
    playlist_url=gmail.get_playlist_url(youtube,DOWNLOAD_PLAYLIST)
    download_playlist(playlist_url)
    return_check=0
    # for file in [os.path.join(COM_PATH,file) for file in os.listdir(COM_PATH)]:
        # return_check+=transfer_file_to_device(file,PHONE_PATH,False)
    # if return_check==0:
    #     gmail.empty_playlist(youtube, DOWNLOAD_PLAYLIST)