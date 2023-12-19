import json
import requests
import time
from colorama import init, Fore, Back, Style
init(autoreset=True)
import discord
from discord.ext import commands
from config import config
import os
import asyncio

bot = commands.Bot(command_prefix='unknown_prefix', intents=discord.Intents.all())

def box(text, box_color=Back.BLACK, text_color=Fore.WHITE):
    print(f"{box_color}{text_color}{text}{Style.RESET_ALL} {box_color}")

class StockBot(commands.Cog):
    def __init__(self):
        self.API_URL = "https://api-internal.sellix.io/v1/shops/sirmeme"
        self.ALLOWED_TO_SEND = True
        self.AMOUNT_TIMES_CHECKED_FALSE = 0
        self.AMOUNT_TIMES_CHECKED_TRUE = 0

    async def setup_ui(self):
        os.system("cls || clear")

        #box("[--------------------------]", Back.WHITE)
        box(f"Name ({bot.user.name})       ", Back.GREEN)
        box(f"UserID ({bot.user.id})", Back.BLUE)
        #box("[--------------------------]", Back.WHITE)

        print("\n")

        box(f"Denied: {self.AMOUNT_TIMES_CHECKED_FALSE}", Back.RED)
        box(f"Approved: {self.AMOUNT_TIMES_CHECKED_TRUE}", Back.GREEN)

    async def create_embed(self, stock_status, price, title, currency, type_payed, uniqid, positive, negative):
        embed = discord.Embed(
            title="**ELECTRON IS IN STOCK**",
            description=f'```json\n"information": '+'{'+f'\n   "stock": "{stock_status}",\n   "title": "{title}",\n   "price": "{price}",\n   "currency": "{currency}",\n   "type": "{type_payed}",\n   "uniqid": "{uniqid}"\n\n   "feedback": '+'{'+f'\n      "positive": "{positive}",\n      "negative": "{negative}"\n   '+'},\n}\n``` https://nocap.land/purchases.html',
            colour=discord.Colour.blue()
        )
        return embed

    async def send_notification(self, stock_status, price, title, currency, type_payed, uniqid, positive, negative):
        self.AMOUNT_TIMES_CHECKED_TRUE += 1
        await self.setup_ui()  # Use the existing instance to update the UI
        for guild in bot.guilds:
            channel = discord.utils.get(guild.channels, name='electron-stock')
            if channel:
                await channel.send(embed=await self.create_embed(stock_status, price, title, currency, type_payed, uniqid, positive, negative))
            else:
                print(f"{Fore.RED}[-] 'electron-stock' channel not found in {guild.name}{Style.RESET_ALL}")


    async def check_stock_and_notify(self):
        while True:
            GUILD_AMOUNT = len(bot.guilds)
            RUNNING_VERSION = "V.1.3"
            stream_status = discord.Streaming(
                name=f"| {RUNNING_VERSION} | {str(GUILD_AMOUNT)} Guilds |", 
                url="https://www.twitch.tv/ninja"
            )
            await bot.change_presence(activity=stream_status)
            response = requests.get(self.API_URL)

            if response.status_code == 200:
                data = response.json()

                stock_status = data['data']['products'][0]['stock']
                price = data['data']['products'][0]['price']
                title = data['data']['products'][0]['title']
                currency = data['data']['products'][0]['currency']
                type_payed = data['data']['products'][0]['type']
                uniqid = data['data']['products'][0]['uniqid']
                positive = data['data']['products'][0]['feedback']['positive']
                negative = data['data']['products'][0]['feedback']['negative']

                if stock_status is not None and stock_status > 1 and self.ALLOWED_TO_SEND:
                    self.ALLOWED_TO_SEND = False
                    await self.send_notification(stock_status, price, title, currency, type_payed, uniqid, positive, negative)
                elif stock_status is not None and stock_status <= 1 and not self.ALLOWED_TO_SEND:
                    self.ALLOWED_TO_SEND = True
                else:
                    self.AMOUNT_TIMES_CHECKED_FALSE += 1
                    await self.setup_ui()  # Use the same instance to update the UI
            else:
                print(f"{Fore.RED}[-] Unable to fetch data. Status code: {response.status_code}")
            await asyncio.sleep(30)


    async def create_electron_stock_channel(self, guild):
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel('electron-stock', overwrites=overwrites)
        print(f"{Fore.GREEN}[+] 'electron-stock' channel created in {guild.name}{Style.RESET_ALL}")

@bot.event
async def on_ready():
    for guild in bot.guilds:
        channel = discord.utils.get(guild.channels, name='electron-stock')
        if channel:
            pass
        else:
            stock_bot_instance = StockBot()
            await stock_bot_instance.create_electron_stock_channel(guild)
            print(f"{Fore.GREEN}[+] 'electron-stock' channel created in {guild.name}{Style.RESET_ALL}")

    stock_bot_instance = StockBot()
    await stock_bot_instance.setup_ui()
    bot.loop.create_task(stock_bot_instance.check_stock_and_notify())


@bot.event
async def on_guild_join(guild):
    channel = discord.utils.get(guild.channels, name='electron-stock')
    if channel:
        print(f"{Fore.GREEN}[+] 'electron-stock' channel already exists in {guild.name}{Style.RESET_ALL}")
    else:
        stock_bot_instance = StockBot()
        await stock_bot_instance.create_electron_stock_channel(guild)
        print(f"{Fore.GREEN}[+] 'electron-stock' channel created in {guild.name}{Style.RESET_ALL}")

bot.run(config.read()['token'])
