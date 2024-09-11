import flet as ft
from pyngrok import ngrok

from asyncio import sleep

async def main(page: ft.Page):
  page.title = 'Googa Beta Bot'
  page.theme_mode = ft.ThemeMode.DARK
  page.bgcolor = '#292929'
  page.vertical_alignment = ft.MainAxisAlignment.CENTER
  page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
  page.font = {"Kelly Slab": "fonts/Kelly Slab.ttf"}
  page.theme = ft.Theme(font_family='Kelly Slab')

  async def ClickPlay(event: ft.ContainerTapEvent):
    play.scale = 0.95
    await page.update_async()
    await sleep(0.15)
    play.scale = 1
    await page.update_async()

  play = ft.Image(
    src="sprites/play.svg",
    color=ft.colors.WHITE,
    width=200,
    height=200,
    fit=ft.ImageFit.CONTAIN,
    scale=1,
    animate_scale=ft.Animation(
      duration=400,
      curve=ft.AnimationCurve.EASE_IN_OUT
    )
  )

  play_container = ft.Container(
    content=play,
    alignment=ft.alignment.center,
    on_click=ClickPlay
  )
  
  await page.add_async(play_container)

public_url = ngrok.connect(8000)
print(f"Ngrok Tunnel URL: {public_url}")

if __name__ == '__main__':
  ft.app(target=main, view=None, assets_dir='app_data', port=8000)