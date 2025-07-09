import os, sys
import discord
from discord.ext import commands
from discord.utils import get
import yt_dlp
import webserver
import asyncio
from dotenv import load_dotenv
import functools
import subprocess

# Auto-update yt-dlp on startup
def actualizar_yt_dlp():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], check=True)
        print("✅ yt-dlp actualizado correctamente")
    except subprocess.CalledProcessError:
        print("⚠️ No se pudo actualizar yt-dlp")

actualizar_yt_dlp()

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Bot setup
token = DISCORD_TOKEN
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# FFmpeg & yt-dlp options
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
}

# Storage
desconexion_timers = {}  # guild_id -> asyncio.Task
music_queues = {}

# Auto-disconnect after inactivity
def iniciar_temporizador_desconexion(ctx):
    async def desconectar_si_inactivo():
        await asyncio.sleep(1200)  # 20 min
        voz = get(bot.voice_clients, guild=ctx.guild)
        if voz and voz.is_connected():
            await voz.disconnect()
            await ctx.send("⏱️ Me desconecté por inactividad de 20 minutos.")
    # Cancel existing
    anterior = desconexion_timers.get(ctx.guild.id)
    if anterior:
        anterior.cancel()
    # Start a new
    tarea = asyncio.create_task(desconectar_si_inactivo())
    desconexion_timers[ctx.guild.id] = tarea

# Events and commands
@bot.event
async def on_ready():
    print("Estoy viva, EXPLOSIÓN")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def hola(ctx):
    await ctx.send("mundo")

@bot.command()
async def conectar(ctx):
    canal = ctx.author.voice.channel if ctx.author.voice else None
    if not canal:
        return await ctx.send("No estás conectado a ningún canal de voz")
    voz = get(bot.voice_clients, guild=ctx.guild)
    if voz and voz.is_connected():
        await voz.move_to(canal)
    else:
        await canal.connect()
        await ctx.send("¡Me conecté al canal de voz!")
    iniciar_temporizador_desconexion(ctx)

@bot.command()
async def desconectar(ctx):
    voz = get(bot.voice_clients, guild=ctx.guild)
    # cancel timer
    if ctx.guild.id in desconexion_timers:
        desconexion_timers[ctx.guild.id].cancel()
        del desconexion_timers[ctx.guild.id]
    if voz and voz.is_connected():
        await voz.disconnect()
        await ctx.send("¡Adiós mundo cruel!")
    else:
        await ctx.send("¡No estoy conectado a ningún canal de voz!")

@bot.command(name='play')
async def play(ctx, *, query: str):
    voz = get(bot.voice_clients, guild=ctx.guild)
    if not voz or not voz.is_connected():
        if ctx.author.voice:
            voz = await ctx.author.voice.channel.connect()
        else:
            return await ctx.send("¡Debes estar en un canal de voz!")
    music_queues.setdefault(ctx.guild.id, [])
    if not query.startswith("http"):
        query = f"ytsearch:{query}"
    music_queues[ctx.guild.id].append(query)
    if voz.is_playing() or voz.is_paused():
        await ctx.send("🎵 Canción añadida a la cola.")
        iniciar_temporizador_desconexion(ctx)
        return
    await _reproducir_siguiente(ctx, voz)

@bot.command()
async def skip(ctx):
    voz = get(bot.voice_clients, guild=ctx.guild)
    if not voz or not voz.is_connected():
        return await ctx.send("❌ No estoy conectado a ningún canal de voz.")
    if not voz.is_playing():
        return await ctx.send("❌ No hay nada reproduciéndose.")
    voz.stop()
    await ctx.send("⏭️ Canción saltada.")
    iniciar_temporizador_desconexion(ctx)

async def _reproducir_siguiente(ctx, voice_client):
    queue = music_queues.get(ctx.guild.id, [])
    if not queue:
        await ctx.send("✅ La cola ha terminado.")
        iniciar_temporizador_desconexion(ctx)
        return
    url = queue.pop(0)
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = await loop.run_in_executor(None, functools.partial(ydl.extract_info, url, False))
    if 'entries' in info:
        info = info['entries'][0]
    stream_url = info.get('url')
    titulo = info.get('title', 'Desconocido')
    if not stream_url:
        await ctx.send("❌ No se pudo obtener una URL válida.")
        iniciar_temporizador_desconexion(ctx)
        return
    audio_source = await discord.FFmpegOpusAudio.from_probe(stream_url, **FFMPEG_OPTIONS)
    audio_source = discord.PCMVolumeTransformer(audio_source, volume=0.06)
    voice_client.stop()
    voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(_reproducir_siguiente(ctx, voice_client), bot.loop))
    await ctx.send(f"▶️ Reproduciendo: **{titulo}**")
    iniciar_temporizador_desconexion(ctx)

# Inicio del bot
if __name__ == "__main__":
    webserver.keep_alive()
    bot.run(token)


  


