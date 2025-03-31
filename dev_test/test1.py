import yt_dlp
import time
import subprocess

url = 'https://www.youtube.com/watch?v=6-8E4Nirh9s'


def test1() -> str:
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',

        "extract_flat": "in_playlist",
        "usenetrc": True,
        "no_color": True,
    }

    _ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

    data = _ytdl.extract_info(url, download=False)

    return data['url']

def test2(cmd: str) -> str:
    def execute(cmd):
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                 universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        error = popen.stderr.read()
        yield "\n" + error + "\n"
        popen.stdout.close()
        popen.stderr.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    data = list(execute(cmd))

    return data[0]

def test3():
    INFO_FILE = 'path/to/video.info.json'

    with yt_dlp.YoutubeDL() as ydl:
        error_code = ydl.download_with_info_file(INFO_FILE)

    print('Some videos failed to download' if error_code
          else 'All videos successfully downloaded')



if __name__ == '__main__':
    st1 = time.time()
    print(test1())
    print(f'test1 took {time.time() - st1} seconds\n')

    # st2 = time.time()
    # print(test2(f'yt-dlp -g {url}'))
    # print(f'test2 took {time.time() - st2} seconds\n')
    #
    # st3 = time.time()
    # print(test2('yt-dlp -f bestaudio --get-url ' + url))
    # print(f'test3 took {time.time() - st3} seconds\n')


