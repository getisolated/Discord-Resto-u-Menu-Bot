import os
from dotenv import load_dotenv
import discord
import requests
from bs4 import BeautifulSoup
import asyncio
import datetime

load_dotenv()

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
CROUS_WEBSITE = os.environ['CROUS_WEBSITE']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

async def fetch_menu():
    url = CROUS_WEBSITE

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title_element = soup.find('time', class_='menu_date_title')
        title = title_element.get_text(strip=True) if title_element else "Title not found"

        body_element = soup.find('ul', class_='meal_foodies').find('li')
        dishes = []
        for li in body_element.find_all('li'):
            dishes.append(li.get_text(strip=True))

        message_content = f"**__{title}__**\n"
        message_content += "\n".join([f"{dish}" for dish in dishes])

        return message_content

    except requests.exceptions.RequestException as e:
        return f"Erreur en accédant à la page web: {e}"
    except Exception as e:
        return f"Une erreur inattendue s'est produite: {e}"

async def send_daily_menu():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel with ID {CHANNEL_ID} not found.")
        return
    else :
        print(f"Channel {channel.name} linked.")

    while not client.is_closed():
        now = datetime.datetime.now()
        target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)

        if now > target_time:
            target_time += datetime.timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)

        menu_content = await fetch_menu()
        await channel.send(menu_content)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(send_daily_menu())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '/menuchef':
        menu_content = await fetch_menu()
        await message.channel.send(menu_content)

client.run(DISCORD_TOKEN)
