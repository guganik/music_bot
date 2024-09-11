from shazamio import Shazam
import requests
from bs4 import BeautifulSoup
from config import HEADERS
import os
from moviepy.editor import VideoFileClip

class FindMusic():
  async def FindByVoice(file_path):
    shazam = Shazam()
    out = await shazam.recognize(file_path)
    return f"{out['track']['title']} - {out['track']['subtitle']}"
  
  async def FindByName(track_name):
    punc = '''!()[]{};:'"\\<>./?@#$%^&*_~'''
    for ele in track_name:
      if ele in punc:
        track_name = track_name.replace(ele, "")
    track_name = '+'.join(track_name.split())
    req = f"https://ruo.morsmusic.org/search/{track_name}"

    proxy = {
      "http": "http://23.227.38.253:80",
      "https": "https://23.227.38.253:80"
    }

    request = requests.get(req, headers=HEADERS, proxies=proxy)
    soup = BeautifulSoup(request.text, "lxml")
    info = soup.find(class_="muslist").find(class_="track")
    url = info.find(class_="track-download").get("href")
    id = url.split('/')[-2]
    download_url = f'https://ruo.morsmusic.org{url}'
    artists = [i.text for i in info.find(class_="media-artist").find_all('a')]
    title = info.find(class_="media-name").text.strip()
    duration = sum(x * int(t) for x, t in zip([60, 1], info.find(class_="track__fulltime").text.split(":")))

    return {
      "id": id,
      "title": title,
      "artists": artists,
      "download_url": download_url,
      "duration": duration
    }
  
  async def FindByLirycs(text):
    shazam = Shazam()
    out = await shazam.search_track(query=text, limit=1)
    return f"{out['tracks']['hits'][0]['heading']['subtitle']} - {out['tracks']['hits'][0]['heading']['title']}"

async def ConvToMP3(mp4file, filename):
  src = f'./data/cache/tracks/{filename}.mp3'
  video = VideoFileClip(mp4file)
  audio = video.audio
  filename = video.filename
  audio.write_audiofile(src)
  audio.close()
  video.close()
  os.remove(mp4file)

  return src