# 🎶✨ MeguBeats — El Bot Musical de Megumin

¡Bienvenido a **MeguBeats**, el bot de música para Discord comandado por la archimaga **Megumin**! 💥  
Reproduce audio de YouTube, gestiona colas de reproducción y, como toda gran magia, ¡está en constante evolución!

---

## 📖 Índice

1. [🌟 Funcionalidades](#-funcionalidades)  
2. [📜 Comandos Disponibles](#-comandos-disponibles)  
3. [⚙️ Instalación & Configuración](#️-instalación--configuración)  
4. [🚀 Ejemplos de Uso](#-ejemplos-de-uso)  
5. [🔍 Cómo Funciona la Cola](#-cómo-funciona-la-cola)  
6. [📦 Estructura del Proyecto](#-estructura-del-proyecto)  
8. [🔒 Buenas Prácticas de Seguridad](#-buenas-prácticas-de-seguridad)    
9. [🧙 Autor & Créditos](#-autor--créditos)  

---

## 🌟 Funcionalidades

- 🔊 **Reproducción de audio** desde YouTube (URLs o búsquedas por texto).  
- 🎵 **Sistema de cola** por servidor (guild).  
- ⏭️ **Skip** de pistas en cualquier momento.  
- 🔌 **Conexión/Desconexión** automática al canal de voz del usuario.  
- 🧪 Comandos de prueba: `!ping`, `!hola`.  
- 💾 Integración con **yt-dlp**, **FFmpeg** y **dotenv** para manejar secretos.  
- 🚧 En constante desarrollo: próximamente más magia.

---

## 📜 Comandos Disponibles

| Comando                 | Descripción                                                                       |
|-------------------------|-----------------------------------------------------------------------------------|
| `!play <query>`         | Añade una canción (URL o texto) a la cola; reproduce inmediatamente si está libre. |
| `!skip`                 | Salta la canción actual y reproduce la siguiente de la cola.                      |
| `!conectar`             | Invoca a MeguBeats al canal de voz donde estés tú.                                |
| `!desconectar`          | Expulsa a MeguBeats del canal de voz.                                             |
| `!ping`                 | Test de latencia: responde “pong”.                                               |
| `!hola`                 | Respuesta de prueba: “mundo”.                                                     |

> ⚠️ **Nota:** Se menciona `is_paused()` en el flujo, pero los comandos `!pause` y `!resume` aún no están disponibles.

---

## ⚙️ Instalación & Configuración

1. **Clona el repositorio**  
   ```bash
   git clone https://github.com/TU_USUARIO/MeguBeats.git
   cd MeguBeats

## 🚀 Ejemplos de Uso

Usuario: !play Never Gonna Give You Up
MeguBeats: ▶️ Reproduciendo: **Rick Astley – Never Gonna Give You Up**

Usuario: !play https://youtu.be/dQw4w9WgXcQ
MeguBeats: 🎵 Canción añadida a la cola.

Usuario: !skip
MeguBeats: ⏭️ Canción saltada.

Usuario: !desconectar
MeguBeats: ¡Adiós mundo cruel!

## 🔍 Cómo Funciona la Cola

1️⃣ Inicialización
   - 🎶 !play inicia de inmediato si no hay nada reproduciéndose.
2️⃣ Añadir a la cola
   - ➕ !play agrega al final si ya hay música.
3️⃣ Reproducción automática
   - 🔁 El callback `after` invoca `_reproducir_siguiente`.
4️⃣ Final de cola
   - ✅ “La cola ha terminado.”

## 📦 Estructura del Proyecto
BotDiscord/
├── BotMegu.py            # Lógica principal del bot
├── webserver.py          # Keep-alive para hosting en plataformas gratuitas
├── requirements.txt      # Dependencias (discord.py, yt-dlp, python-dotenv…)
├── .gitignore
├── .env.example
└── README.md