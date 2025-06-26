import os
import discord
from discord.ext import commands
from discord.utils import get
import yt_dlp
import webserver
import asyncio
from dotenv import load_dotenv
import functools

#Carga Variables de entorno desde el archivo .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") #Token de autenticación para Discord 

#Configuración de intents para recibir contenido de mensajes
intents = discord.Intents.default()
intents.message_content = True
#Se inicializa el bot con el prefijo  "!" y los intents configurados
bot = commands.Bot(command_prefix="!", intents=intents)

# Opciones para FFmpeg: reconexión automatica si falla el stream y sin procesamiento de vídeo
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Opciones para yt-dlp: Elegir la mejor calidad de audio, silencio en consola y sin listas de reproducción
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True
}

# Diccionario de colas de reproducción por servidor (guild_id ---> lista de queries o URLs)
music_queues = {}

#Evento que se dispara cuando el bot esta listó y conectado 
@bot.event
async def on_ready():
    print("Estoy viva, EXPLOSIÓN") #Mensaje en la consola para indicar que el bot esta encendido 

#Evento que se dispara con cada mensaje, evita procesar mensajes de otros bots
@bot.event
async def on_message(message):
    if message.author.bot:
        return  #Ignorar los mensajes del bot para que no se creeen bucles 
    print(f"{message.author}: {message.content}") #Loguea {autor} y {contenido} en la consola
    await bot.process_commands(message)  #Procesa los comandos registrados  
#Comando que responde "pong" cuando envias !ping
@bot.command()
async def ping(ctx):
    await ctx.send("pong")

#Comando que responde "mundo" cuando envias !pong
@bot.command()
async def hola(ctx):
    await ctx.send("mundo")

#Comando para enviar la imagen "lucho.jpg" cuando envias !tarzan
#@bot.command()
#async def tarzan(ctx):
    #with open('lucho.jpg', 'rb') as f:
        #await ctx.send(file=discord.File(f))

#Comando para desconectar el bot del canal de voz
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
#Comando para desconectar el bot del canal de voz
@bot.command()
async def desconectar(ctx):
    voz = get(bot.voice_clients, guild=ctx.guild)
    if voz and voz.is_connected():
        await voz.disconnect()
        await ctx.send("¡Adiós mundo cruel!")
    else:
        await ctx.send("¡No estoy conectado a ningún canal de voz!")

#Comando  !play  acepta  nombre de la cancion o URL y la reproduce
@bot.command(name='play')
async def play(ctx, *, query: str):
    # Conexión automatica al canal de voz si no está conectado 
    voz = get(bot.voice_clients, guild=ctx.guild)
    if not voz or not voz.is_connected():
        if ctx.author.voice:
            voz = await ctx.author.voice.channel.connect()
        else:
            return await ctx.send("¡Debes estar en un canal de voz!")

    # Inicializa la cola si no existe para este servidor 
    music_queues.setdefault(ctx.guild.id, [])

    # Si el parametro no es URL, usa búsqueda  en YouTube con "ytsearch:"
    if not query.startswith("http"):
        query = f"ytsearch:{query}"

    # Añade la búsqueda o URL a la cola del servidor 
    music_queues[ctx.guild.id].append(query)

    # Si ya hay musica sonando o en pausa, solo notifica y no lanza reproducción inmediata 
    if voz.is_playing() or voz.is_paused():
        return await ctx.send("🎵 Canción añadida a la cola.")

    # Si no esta reproduccion nada , inicia la reproduccion del siguiente ítem
    await _reproducir_siguiente(ctx, voz)

#Comando  "skip" salta la cancion actual\@bot.command()
@bot.command()
async def skip(ctx):
    voz = get(bot.voice_clients, guild=ctx.guild)
    if not voz or not voz.is_connected():
        return await ctx.send("❌ No estoy conectado a ningún canal de voz.")
    if not voz.is_playing():
        return await ctx.send("❌ No hay nada reproduciéndose.")
    voz.stop() #Detiene la Reproduccion actual, llama al callback "after"
    await ctx.send("⏭️ Canción saltada.")

#Funcion interna para reproducir el siguiente item de la cola
async def _reproducir_siguiente(ctx, voice_client):
    queue = music_queues.get(ctx.guild.id, [])
    if not queue:
        return await ctx.send("✅ La cola ha terminado.")

    url = queue.pop(0) #Obtiene y elemina el primer elemento de la cola 

    # Extrae informacion de la URL o busqueda en un hilo separdo para que no se bloquee el event loop
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = await loop.run_in_executor(
            None,
            functools.partial(ydl.extract_info, url, download=False)
        )

    # Si la consulta fue una busqueda , toma el primer resultado
    if 'entries' in info:
        info = info['entries'][0]

    stream_url = info.get('url')
    titulo     = info.get('title', 'Desconocido')

    # Detiene cualquier reproduccion previa y reproduce con FFmpeg
    voice_client.stop()
    source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
    voice_client.play(
        source,
        after=lambda e: asyncio.run_coroutine_threadsafe(
            _reproducir_siguiente(ctx, voice_client),
            bot.loop
        )
    )
    #Ajusta volumen de la reproduccion
    voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
    voice_client.source.volume = 0.06
    # Envía un mensaje al canal indicando la canción en reproducción
    await ctx.send(f"▶️ Reproduciendo: **{titulo}**")
    
# Punto de entrada: inicia servidor web de keep-alive y ejecuta el bot
if __name__ == "__main__":
    webserver.keep_alive()
    bot.run(DISCORD_TOKEN)

  


