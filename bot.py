from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot import asyncio_filters
import utils
import keyboards
import asyncio

import time
import hashlib
import urllib.request
import os
import json
from config import BOT_TOKEN, BOT_LINK

import datetime
import multiprocessing

import logging

logging.basicConfig(level=logging.INFO)

state_storage = StateMemoryStorage()
bot = AsyncTeleBot(BOT_TOKEN, parse_mode='HTML', state_storage=state_storage)

# CUSTOM FILTERS
class PlaylistStates(StatesGroup):
  typing_playlist_name = State()

class ArrowStates():
  is_press = State()

# CLASSES
class User():
  def __init__(self, id, name):
    self.id = id
    self.name = name

class Music():
  def __init__(self, id, file_id, title, artists, download_url):
    self.id = id
    self.file_id = file_id
    self.title = title
    self.artists = artists
    self.download_url = download_url
    
class Playlist():
  def __init__(self, id, title):
    self.id = id
    self.title = title

  # CREATE NEW PLAYLIST
  async def new_playlsit(playlist, user: User):
    data = f'{playlist}:{user.id}'
    hash_playlist = hashlib.sha256()
    hash_playlist.update(data.encode('utf-8'))

    if os.path.exists(f'./data/users/{user.name}') == False:
      os.mkdir(f'./data/users/{user.name}')

    with open(f'./data/playlists.json', 'r', encoding='utf-8') as file:
      info = json.load(file)
      if hash_playlist.hexdigest()[:16] not in [playlist_id for playlist_id, playlist_info in info.items()]:
        info[hash_playlist.hexdigest()[:16]] = {
          "title": playlist,
          "user": user.name,
          "creation_time": str(time.time())
        }
      else:
        await bot.send_message(user.id, 'Сожалею, но вы не можете создать плейлист с таким именем...\nВозможно, у вас уже есть плейлист с таким именем')
        return

    with open(f'./data/playlists.json', 'w', encoding='utf-8') as file:
      json.dump(info, file, indent=2, ensure_ascii=False)

    local_info = {"title": playlist}
    with open(f'./data/users/{user.name}/{hash_playlist.hexdigest()[:16]}.json', 'w', encoding='utf-8') as file:
      json.dump(local_info, file, indent=2, ensure_ascii=False)

    if os.path.exists(f'./data/users/{user.name}/playlists.json') == False:
      with open(f'./data/users/{user.name}/playlists.json', 'w', encoding='utf-8') as file:
        json.dump({}, file, indent=2, ensure_ascii=False)

    with open(f'./data/users/{user.name}/playlists.json', 'r', encoding='utf-8') as file:
      data = json.load(file)
    data[hash_playlist.hexdigest()[:16]] = {
      "title": playlist,
      "creation_time": str(time.time())
    }
    with open(f'./data/users/{user.name}/playlists.json', 'w', encoding='utf-8') as file:
      json.dump(data, file, indent=2, ensure_ascii=False)

    await bot.send_message(user.id, f'Плейлист "{playlist}" создан!', reply_markup=await keyboards.main())

  async def add_track(music: Music, user: User, hash_playlist):
    with open(f'./data/users/{user.name}/{hash_playlist}.json', 'r', encoding='utf-8') as file:
      data = json.load(file)

    data[music.id] = {"file_id": music.file_id,
                      "title": music.title,
                      "artists": music.artists,
                      "download_url": music.download_url}

    with open(f'./data/users/{user.name}/{hash_playlist}.json', 'w', encoding='utf-8') as file:
      json.dump(data, file, indent=2, ensure_ascii=False)

  async def share_playlist(main_user, user: User, playlist_id):
    with open(f'./data/users/{main_user}/{playlist_id}.json', 'r', encoding='utf-8') as file:
      share_playlist = json.load(file)

    title_share = share_playlist['title']
    data = f'{title_share}:{user.id}'
    hash_playlist = hashlib.sha256()
    hash_playlist.update(data.encode('utf-8'))

    if os.path.exists(f'./data/users/{user.name}') == False:
      os.mkdir(f'./data/users/{user.name}')

    with open(f'./data/playlists.json', 'r', encoding='utf-8') as file:
      info = json.load(file)
      if hash_playlist.hexdigest()[:16] not in [playlist_id for playlist_id, playlist_info in info.items()]:
        info[hash_playlist.hexdigest()[:16]] = {
          "title": title_share,
          "user": user.name,
          "creation_time": str(time.time())
        }
      else:
        await bot.send_message(user.id, 'Сожалею, но вы не можете создать плейлист с таким именем...\nВозможно, у вас уже есть плейлист с таким именем')
        return
    
    with open(f'./data/playlists.json', 'w', encoding='utf-8') as file:
      json.dump(info, file, indent=2, ensure_ascii=False)

    with open(f'./data/users/{user.name}/{hash_playlist.hexdigest()[:16]}.json', 'w', encoding='utf-8') as file:
      json.dump(share_playlist, file, indent=2, ensure_ascii=False)

    if os.path.exists(f'./data/users/{user.name}/playlists.json') == False:
      with open(f'./data/users/{user.name}/playlists.json', 'w', encoding='utf-8') as file:
        json.dump({}, file, indent=2, ensure_ascii=False)

    with open(f'./data/users/{user.name}/playlists.json', 'r', encoding='utf-8') as file:
      data = json.load(file)
    data[hash_playlist.hexdigest()[:16]] = {
      "title": title_share,
      "creation_time": str(time.time())
    }
    with open(f'./data/users/{user.name}/playlists.json', 'w', encoding='utf-8') as file:
      json.dump(data, file, indent=2, ensure_ascii=False)

    await bot.send_message(user.id, f'Плейлист "{title_share}" был добавлен в твои плейлисты!', reply_markup=await keyboards.main())

  # STATES GROUPS

class PlaylistStates(StatesGroup):
  typing_playlist_name = State()
  add_to_playlist = State()
  select_page = State()

# FUNCTIONS
async def FindTrack(title, user: User):
  data = await utils.FindMusic.FindByName(title)
  with open('./data/tracks.json', 'r', encoding='utf-8') as file:
    track = json.load(file)

  if data["id"] in [i for i, k in track.items()]:
    file_id = track[data["id"]]["file_id"]
    artists = track[data["id"]]["artists"]
    title = track[data["id"]]["title"]
    await bot.send_audio(user.id,
                         file_id,
                         performer=f'{", ".join(artists)}',
                         title=title,
                         reply_markup=await keyboards.add_to_playlist(data['id']))

  else:
    urllib.request.urlretrieve(data["download_url"], f'./data/cache/tracks/{data["id"]}.mp3')
    msg = await bot.send_audio(user.id, open(f'./data/cache/tracks/{data["id"]}.mp3', 'rb'),
                               performer=f"{', '.join(data['artists'])}",
                               title=data['title'],
                               reply_markup=await keyboards.add_to_playlist(data['id']))
    os.remove(f'./data/cache/tracks/{data["id"]}.mp3')
    track[data['id']] = {
        "title": data['title'],
        "artists": data['artists'],
        "download_url": data['download_url'],
        "duration": data['duration'],
        "file_id": msg.audio.file_id
      }
    with open('./data/tracks.json', 'w', encoding='utf-8') as file:
      json.dump(track, file, indent=2, ensure_ascii=False)

async def MainMenu(user: User):
  await bot.send_message(user.id, "Главное меню", reply_markup=await keyboards.main())

async def SelectPage(user: User, playlist, hash_playlist, plus):
  async with bot.retrieve_data(user.id, user.id) as data:
    call_message_id = data['call_message_id']

  await bot.edit_message_reply_markup(user.id, call_message_id, reply_markup=await keyboards.show_playlist(playlist, hash_playlist, plus))

# CMDS
@bot.message_handler(commands=['start', 'menu'])
async def Start(message: Message):
  if len(message.text.split()) > 1:
    playlist_id = message.text.split()[1]
    with open(f'./data/playlists.json', 'r', encoding='utf-8') as file:
      data = json.load(file)
    
    playlist = data[playlist_id]
    main_user = playlist['user']
    user = User(message.chat.id, message.from_user.username)
    
    await Playlist.share_playlist(main_user, user, playlist_id)
  else:
    await MainMenu(user=User(message.chat.id, message.from_user.username))
  if message.text == '/start':
    with open(f'./data/all_users.json', 'r', encoding='utf-8') as file:
      data = json.load(file)
    data[user.id] = user.name
    with open(f'./data/all_users.json', 'r', encoding='utf-8') as file:
      json.dump(data, file, indent=2, ensure_ascii=False)

@bot.message_handler(commands='add')
async def CmdAddTrack(message: Message):
  playlist = "куку"
  data = f'{playlist}:{message.chat.id}'
  hash_playlist = hashlib.sha256()
  hash_playlist.update(data.encode('utf-8'))
  await Playlist.add_track(music = Music("1540901017",
                                   "CQACAgIAAxkDAAOXZq51J-ofs6CWAAGYsHZ0Y-xvyUZ6AAKsUwACQZRwSXF3srLZgDjuNQQ",
                                   "Микромир (Microcosm)",
                                   ["RasKar", "Noize MC"],
                                   "https://ruo.morsmusic.org/load/1540901017/RasKar_Noize_MC_-_Mikromir_Microcosm_(musmore.org).mp3"),
                      user = User(message.chat.id, message.from_user.username),
                      hash_playlist = hash_playlist.hexdigest()[:16]
  )

@bot.message_handler(commands=['app'])
async def App(message: Message):
  keyboard = InlineKeyboardMarkup()
  keyboard.add(InlineKeyboardButton(text='Приложение',
                                    web_app=WebAppInfo(
                                      url='https://f5db-57-129-1-27.ngrok-free.app'
                                    )))
  await bot.send_message(message.chat.id, 'Приложение', reply_markup=keyboard)

@bot.message_handler(state=PlaylistStates.typing_playlist_name)
async def CmdCreateNewPlaylist(message: Message):
  user = User(message.chat.id, message.from_user.username)
  await Playlist.new_playlsit(message.text, user)
  await bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(state=PlaylistStates.select_page)
async def EnterNumberPage(message: Message):
  async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    if 'plus' not in data:
      data['plus'] = 0
    idle_plus = data['plus']
    playlist = data['playlist_info']
    hash_playlist = data['hash_playlist']
    call_answer_id = data['call_answer_id']

  plus = int(message.text) - 1

  try:
    await SelectPage(User(message.chat.id, message.from_user.username),
                    playlist, hash_playlist, plus)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
      data['plus'] = plus
  except:
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
      data['plus'] = idle_plus

  await bot.delete_messages(message.chat.id, [message.id, call_answer_id])

# TEXT FOUND
@bot.message_handler(content_types=['text'])
async def FindTrackText(message: Message):
  try:
    try:
      await FindTrack(title=message.text, user=User(message.chat.id, message.from_user.username))
    except:
      title = await utils.FindMusic.FindByLirycs(message.text)
      await bot.reply_to(message, f"Shazam распознал ее как \"{title}\"")
      await FindTrack(title, User(message.chat.id, message.from_user.username))
  except:
    await bot.reply_to(message, "Такая песня не найдена")

# SHAZAM
@bot.message_handler(content_types=['voice'])
async def FindTrackVoice(message: Message):
  if not os.path.exists(f'./data/cache/voices/{message.from_user.username}'):
    os.mkdir(f'./data/cache/voices/{message.from_user.username}')
  src = f'./data/cache/voices/{message.from_user.username}/{message.voice.file_unique_id}.ogg'
  file_info = await bot.get_file(message.voice.file_id)
  download_file = await bot.download_file(file_info.file_path)
  with open(src, 'wb') as file:
    file.write(download_file)

  title = await utils.FindMusic.FindByVoice(src)
  await bot.reply_to(message, f'Shazam распознал ее как "{title}"')
  await FindTrack(title, user=User(message.chat.id, message.from_user.username))

# CONVERT TO MP3
@bot.message_handler(content_types=['video'])
async def Convert(message: Message):
  file_unique_id = message.video.file_unique_id
  src = f'./data/cache/videos/{file_unique_id}.mp4'
  file_info = await bot.get_file(message.video.file_id)
  download_file = await bot.download_file(file_info.file_path)
  with open(src, 'wb') as file:
    file.write(download_file)
    
  file_path = await utils.ConvToMP3(src, file_unique_id)
  title = await utils.FindMusic.FindByVoice(file_path)
  await FindTrack(title, user=User(message.chat.id, message.from_user.username))

# INLINE KEYBOARDS
@bot.callback_query_handler(func=lambda call: call.data == 'main')
async def CallMainMenu(call: CallbackQuery):
  await MainMenu(user=User(call.message.chat.id, call.from_user.username))

@bot.callback_query_handler(func=lambda call: call.data == 'show_playlists')
async def CallShowPlaylists(call: CallbackQuery):
  user = User(call.message.chat.id, call.from_user.username)
  await bot.delete_state(user.id, user.id)
  await bot.edit_message_text('Моя музыка', user.id, call.message.id, reply_markup=await keyboards.show_playlists(user))

@bot.callback_query_handler(func=lambda call: call.data == 'new_playlist')
async def CmdTypingPlaylistName(call: CallbackQuery):
  user = User(call.message.chat.id, call.from_user.username)
  await bot.send_message(user.id, 'Как назвать плейлист?')
  await bot.set_state(user.id, PlaylistStates.typing_playlist_name, user.id)
  
@bot.callback_query_handler(func=lambda call: call.data[:len('add_music:')] == 'add_music:')
async def CallAddToPlaylist(call: CallbackQuery):
  await bot.set_state(call.from_user.id, PlaylistStates.add_to_playlist, call.message.chat.id)
  with open(f'./data/tracks.json', 'r', encoding='utf-8') as file:
    track_info = json.load(file)

  async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
    if 'plus' not in data:
      data['plus'] = 0
    plus = data['plus']
    data['track_id'] = call.data[len('add_music:'):]
    data['track_info'] = track_info[data['track_id']]

  await bot.send_message(call.message.chat.id,
                         'В какой плейлист добавить?',
                         reply_markup=await keyboards.select_playlist(user=User(call.message.chat.id, call.from_user.username),
                                                                      plus=plus))

@bot.callback_query_handler(func=lambda call: call.data[:len('add_to:')] == 'add_to:')
async def CallSelectPlaylist(call: CallbackQuery):
  with open(f'./data/users/{call.from_user.username}/{call.data[len("add_to:"):]}.json', 'r', encoding='utf-8') as file:
    track_info = json.load(file)

  async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
    track_info[data['track_id']] = data['track_info']
    track = f'{", ".join(track_info[data["track_id"]]["artists"])} - {track_info[data["track_id"]]["title"]}'
  with open(f'./data/users/{call.from_user.username}/{call.data[len("add_to:"):]}.json', 'w', encoding='utf-8') as file:
    json.dump(track_info, file, ensure_ascii=False, indent=2)

  await bot.delete_message(call.message.chat.id, call.message.id)
  await bot.send_message(call.message.chat.id,
                         f'<b>Трек</b>: "{track}" добавлен в\n<b>Плейлист</b>: \"{track_info["title"]}\"!',
                         reply_markup=await keyboards.main())
  await bot.delete_state(call.from_user.id, call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data[:len('playlist:')] == 'playlist:')
async def CallShowPlaylists(call: CallbackQuery):
  await bot.delete_state(call.from_user.id, call.message.chat.id)
  await bot.set_state(call.from_user.id, ArrowStates.is_press, call.message.chat.id)
  with open(f'./data/users/{call.from_user.username}/{call.data[len("playlist:"):]}.json', 'r', encoding='utf-8') as file:
    playlist_info = json.load(file)

  title = playlist_info['title']
  del playlist_info['title']

  async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
    data['playlist_info'] = playlist_info
    data['hash_playlist'] = call.data[len("playlist:"):]

  hash_playlist = data['hash_playlist']
  await bot.edit_message_text(title, call.message.chat.id, call.message.message_id,
                              reply_markup=await keyboards.show_playlist(data['playlist_info'], hash_playlist=hash_playlist))
  
@bot.callback_query_handler(func=lambda call: call.data[:len('track:')] == 'track:')
async def CallSendMusicFromPlaylist(call: CallbackQuery):
  track_id = call.data[len('track:'):]
  with open(f'./data/tracks.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
  track_info = data[track_id]
  try:
    file_id = data[track_id]['file_id']
    await bot.send_audio(call.message.chat.id, file_id)
  except:
    urllib.request.urlretrieve(track_info["download_url"], f'./data/cache/tracks/{track_id}.mp3')

    msg = await bot.send_audio(call.message.chat.id, open(f'./data/cache/tracks/{track_id}.mp3', 'rb'),
                               performer=f"{', '.join(track_info['artists'])}",
                               title=track_info['title'])
    os.remove(f'./data/cache/tracks/{track_id}.mp3')
    data[track_id] = {
        "title": track_info['title'],
        "artists": track_info['artists'],
        "download_url": track_info['download_url'],
        "duration": track_info['duration'],
        "file_id": msg.audio.file_id
      }
    with open('./data/tracks.json', 'w', encoding='utf-8') as file:
      json.dump(data, file, indent=2, ensure_ascii=False)

# SHARE PLAYLIST
@bot.callback_query_handler(func=lambda call: call.data[:len('share:')] == 'share:')
async def CallSharePlaylist(call: CallbackQuery):
  hash_playlist = call.data[len('share:'):]
  await bot.send_message(call.message.chat.id, f'<a href="{BOT_LINK}?start={hash_playlist}">Ссылка</a> на мой плейлист')

# ARROWS
@bot.callback_query_handler(func=lambda call: call.data[:len('arrow:')] == 'arrow:')
async def Arrows(call: CallbackQuery):
  await bot.set_state(call.from_user.id, ArrowStates.is_press, call.message.chat.id)
  user = User(call.message.chat.id, call.from_user.username)

  async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
    if 'plus' not in data: data['plus'] = 0
    playlist = data['playlist_info']
    hash_playlist = data['hash_playlist']
    idle_plus = data['plus']

  if call.data[-len('next'):] == 'next':
    plus = data['plus']

    async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
      data['plus'] = plus + 1

  elif call.data[-len('last_page'):] == 'last_page':
    async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
      data['plus'] = (len(playlist)-1)//10

  elif call.data[-len('back'):] == 'back':
    plus = data['plus']
    
    if plus > 0:
      async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['plus'] = plus - 1

  elif call.data[-len('first_page'):] == 'first_page':
    async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
      data['plus'] = 0

  plus = data['plus']

  # Листаем список плейлистов
  try:
    if call.data[:len('arrow:music:')] == 'arrow:music:':
      await bot.edit_message_reply_markup(user.id, call.message.id, reply_markup=await keyboards.show_playlist(playlist, hash_playlist, plus))
    elif call.data[:len('arrow:playlist:')] == 'arrow:playlist:':
      await bot.edit_message_reply_markup(user.id, call.message.id, reply_markup=await keyboards.show_playlists(user, plus))
  except:
    async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
      data['plus'] = idle_plus

# SELECT PAGE
@bot.callback_query_handler(func=lambda call: call.data[:len('select_page:')] == 'select_page:')
async def CallSelectPage(call: CallbackQuery):
  if call.data[-len('music'):] == 'music':
    await bot.set_state(call.from_user.id, PlaylistStates.select_page, call.message.chat.id)

    msg = await bot.send_message(call.message.chat.id, 'Введи желаемую страницу...')
    async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
      data['call_message_id'] = call.message.id
      data['call_answer_id'] = msg.message_id
  elif call.data[-len('playlist'):] == 'playlist':
    await bot.answer_callback_query(call.id, 'Мне лень пока что писать логику выбора страницы для списка плейлистов, сорян)')

bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())

# async def Spam(time_now):
# 	with open('./Users/AllUsers.json', 'r') as file:
# 		all_users = json.load(file)
# 	users_id = [i for i, k in all_users.items()]
# 	for i in users_id:
# 		await bot.send_message(text=f'Уже <u>{time_now}</u>, а бот еще не на хостинге :(\n<blockquote>Чтобы бот быстрее вышел в штатный режим делитесь им со своими знакомыми и если прирост будет удовлетворительным, то будет введена реферальная система!</blockquote>', chat_id=i)

# async def scheduler():
# 	while True:
# 		time_now = datetime.datetime.now().strftime('%H:%M %d.%m.%Y')
# 		if time_now.split(' ')[0] in ['00:00', '12:00', '18:00', '06:00']:
# 			await Spam(time_now)
# 		await asyncio.sleep(60)

# def worker():
# 	asyncio.run((scheduler()))

async def main():
  print("Бот запущен...")
  # process = multiprocessing.Process(target=worker)
  # process.start()
  # process.join()
  await bot.infinity_polling()

if __name__ == "__main__":
  asyncio.run(main())