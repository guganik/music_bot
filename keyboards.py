from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
import json
from bot import User

# Стрелочки управления
class Arrows():
  class Playlist():
    next = InlineKeyboardButton('>', callback_data='arrow:playlist:next')
    last_page = InlineKeyboardButton('>>', callback_data='arrow:playlist:last_page')
    back = InlineKeyboardButton('<', callback_data='arrow:playlist:back')
    first_page = InlineKeyboardButton('<<', callback_data='arrow:playlist:first_page')
  class Music():
    next = InlineKeyboardButton('>', callback_data='arrow:music:next')
    last_page = InlineKeyboardButton('>>', callback_data='arrow:music:last_page')
    back = InlineKeyboardButton('<', callback_data='arrow:music:back')
    first_page = InlineKeyboardButton('<<', callback_data='arrow:music:first_page')

# Главное меню
async def main():
  keyboard = InlineKeyboardMarkup()
  keyboard.add(InlineKeyboardButton(text="Мои плейлисты", callback_data='show_playlists'))

  return keyboard

# Показ всех плейлистов
async def show_playlists(user: User, plus: int=0):
  keyboard = InlineKeyboardMarkup()

  if os.path.exists(f'./data/users/{user.name}') == False:
    os.mkdir(f'./data/users/{user.name}')
    
  # Проверка, есть ли файл "playlist.json". Если нет, то создать
  if os.path.exists(f'./data/users/{user.name}/playlists.json') == False:
    with open(f'./data/users/{user.name}/playlists.json', 'w', encoding='utf-8') as file:
      json.dump({}, file, ensure_ascii=False, indent=2)

  # Загрузка плейлистов
  with open(f'./data/users/{user.name}/playlists.json', 'r', encoding='utf-8') as file:
    playlist_list = json.load(file)
  
  # Деление списка всех плейлистов на части по 10 плейлистов
  split_playlist_list = []
  if len(playlist_list) > 10:
    for i in range(0, len(playlist_list), 10): split_playlist_list.append(list(reversed(list(playlist_list.items())))[i:i+10])
  else:
    split_playlist_list.append(list(reversed(list(playlist_list.items()))))
  # Создание кнопок, перебор через все плейлисты
  for playlist_info in split_playlist_list[plus]:
    keyboard.add(InlineKeyboardButton(playlist_info[-1]['title'],
                                      callback_data=f'playlist:{playlist_info[0]}'))

  page = InlineKeyboardButton(f'{plus+1}/{len(split_playlist_list)}', callback_data='select_page:playlist')
    
  # Добавление стрелок
  keyboard.add(Arrows.Playlist.first_page,
               Arrows.Playlist.back,
               page,
               Arrows.Playlist.next,
               Arrows.Playlist.last_page,
               row_width=5)

  keyboard.add(InlineKeyboardButton('Создать новый плейлист', callback_data='new_playlist'))
  
  return keyboard

# Открытие плейлиста, показ музыки
async def show_playlist(playlist, hash_playlist, plus=0):
  keyboard = InlineKeyboardMarkup()
  split_playlist = []
  if len(playlist) > 10:
    for i in range(0, len(playlist), 10): split_playlist.append(list(reversed(list(playlist.items())))[i:i+10])
  else:
    split_playlist.append(list(reversed(list(playlist.items()))))

  for track_info in split_playlist[plus]:
    keyboard.add(InlineKeyboardButton(f"{', '.join(track_info[-1]['artists'])} - {track_info[-1]['title']}",
                                      callback_data='track:' + track_info[0]))

  page = InlineKeyboardButton(f'{plus+1}/{len(split_playlist)}', callback_data='select_page:music')

  # Добавление стрелок
  keyboard.add(Arrows.Music.first_page,
               Arrows.Music.back,
               page,
               Arrows.Music.next,
               Arrows.Music.last_page,
               row_width=5)
  
  keyboard.add(InlineKeyboardButton('Поделиться плейлистом', callback_data=f'share:{hash_playlist}'))
  keyboard.add(InlineKeyboardButton('Назад в плейлисты', callback_data='show_playlists'))

  return keyboard

# Выбрать плейлист для манипуляций
async def select_playlist(user: User, plus):
  keyboard = InlineKeyboardMarkup()

  # Проверка, есть ли файл "playlist.json". Если нет, то создать
  if os.path.exists(f'./data/users/{user.name}/playlists.json') == False:
    with open(f'./data/users/{user.name}/playlists.json', 'w', encoding='utf-8') as file:
      json.dump({}, file, ensure_ascii=False, indent=2)

  # Загрузка плейлистов
  with open(f'./data/users/{user.name}/playlists.json', 'r', encoding='utf-8') as file:
    playlist_list = json.load(file)
  
  # Деление списка всех плейлистов на части по 10 плейлистов
  split_playlist_list = []
  if len(playlist_list) > 10:
    for i in range(0, len(playlist_list), 10): split_playlist_list.append(list(reversed(list(playlist_list.items())))[i:i+10])
  else:
    split_playlist_list.append(list(reversed(list(playlist_list.items()))))

  # Создание кнопок, перебор через все плейлисты
  for playlist_info in split_playlist_list[plus]:
    keyboard.add(InlineKeyboardButton(playlist_info[-1]['title'],
                                      callback_data=f'add_to:{playlist_info[0]}'))

  page = InlineKeyboardButton(f'{plus+1}/{len(split_playlist_list)}', callback_data='select_page')
    
  # Добавление стрелок
  keyboard.add(Arrows.Playlist.first_page,
               Arrows.Playlist.back,
               page,
               Arrows.Playlist.next,
               Arrows.Playlist.last_page,
               row_width=5)
  
  keyboard.add(InlineKeyboardButton('Создать новый плейлист', callback_data='new_playlist'))

  return keyboard

# Кнопка под аудио файлами "Добавить в плейлист"
async def add_to_playlist(track_id):
  keyboard = InlineKeyboardMarkup()
  keyboard.add(InlineKeyboardButton('Добавить в плейлист', callback_data='add_music:' + track_id))

  return keyboard

async def logging():
  keyboard = InlineKeyboardMarkup()
  keyboard.add(InlineKeyboardButton('Да', callback_data='show_playlistss'))

  return keyboard