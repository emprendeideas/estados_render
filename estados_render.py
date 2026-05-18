import os
import time
import random
import threading
import asyncio
import requests

from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask

from telethon import TelegramClient
from telethon.sessions import StringSession

from telethon.tl.functions.stories import SendStoryRequest

from telethon.tl.types import (
    InputPrivacyValueAllowAll,
    InputMediaUploadedPhoto
)

from pymongo import MongoClient

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# =========================================
# 🔹 VARIABLES RENDER
# =========================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SESSION = os.getenv("SESSION_STRING")

MONGO_URI = os.getenv("MONGO_URI")

# =========================================
# 🔹 VALIDACIONES
# =========================================

if not SESSION:
    raise ValueError("❌ SESSION_STRING no configurada")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI no configurado")

print("✅ SESSION cargada:", bool(SESSION))

# =========================================
# 🔹 TELEGRAM CLIENT
# =========================================

telegram = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)

telegram.parse_mode = "md"

# =========================================
# 🔹 MONGODB
# =========================================

mongo_client = MongoClient(MONGO_URI)

db = mongo_client["telegram_states"]

collection = db["stories"]

try:

    mongo_client.admin.command("ping")

    print("✅ MongoDB conectado")

except Exception as e:

    print("❌ Error MongoDB:", e)

# =========================================
# 🔹 FLASK PARA RENDER
# =========================================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot de Stories activo 🚀"

def run_web():

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )

def iniciar_web():

    t = threading.Thread(
        target=run_web,
        daemon=True
    )

    t.start()

# =========================================
# 🔹 FECHA
# =========================================

MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

# =========================================
# 🔹 SCHEDULER
# =========================================

scheduler = AsyncIOScheduler(
    event_loop=telegram.loop,
    timezone="America/La_Paz"
)

# =========================================
# 🔹 RANDOM HORARIO
# =========================================

def obtener_hora_random():

    # Entre 9:30 AM y 10:30 AM
    hora = random.choice([9, 10])

    minuto = random.randint(0, 59)

    # Si es 9 -> desde 9:30
    if hora == 9 and minuto < 30:
        minuto = 30

    # Si es 10 -> hasta 10:30
    if hora == 10 and minuto > 30:
        minuto = 30

    return hora, minuto

# =========================================
# 🔹 FUNCIÓN PUBLICAR STORY
# =========================================

async def publicar_story():

    try:

        print("\n🚀 INICIANDO PUBLICACIÓN...")
        print(
            "⏰ Hora Bolivia:",
            datetime.now(ZoneInfo("America/La_Paz"))
        )

        # =========================================
        # 🔹 DETECTAR DÍA
        # =========================================

        dia_semana = datetime.now(
            ZoneInfo("America/La_Paz")
        ).weekday()

        # Monday = 0
        # Wednesday = 2
        # Friday = 4

        if dia_semana == 0:

            tipo_elegido = "pagos"

        elif dia_semana == 2:

            tipo_elegido = "fdi"

        elif dia_semana == 4:

            tipo_elegido = "copytrade"

        else:

            print("⛔ Hoy no toca publicar")
            return

        print(f"📅 Tipo seleccionado: {tipo_elegido}")

        # =========================================
        # 🔹 BUSCAR STORIES
        # =========================================

        documentos = list(collection.find({
            "tipo": tipo_elegido,
            "usada": False
        }))

        # =========================================
        # 🔹 REINICIAR SI SE ACABAN
        # =========================================

        if len(documentos) == 0:

            print("♻️ Reiniciando imágenes usadas...")

            collection.update_many(
                {
                    "tipo": tipo_elegido
                },
                {
                    "$set": {
                        "usada": False
                    }
                }
            )

            documentos = list(collection.find({
                "tipo": tipo_elegido,
                "usada": False
            }))

        # =========================================
        # 🔹 ELEGIR RANDOM
        # =========================================

        if len(documentos) == 0:

            print("❌ No hay stories disponibles")
            return

        story = random.choice(documentos)

        tipo = story["tipo"]

        imagen_url = story["imagen"]

        print("🖼️ Imagen elegida")

        # =========================================
        # 🔹 FECHA
        # =========================================

        tz = ZoneInfo("America/La_Paz")

        hoy = datetime.now(tz)

        fecha = f"{hoy.day} de {MESES[hoy.month]}"

        # =========================================
        # 🔹 TEXTOS
        # =========================================

        if tipo == "pagos":

            textos_pagos = [

                f"""
        🎉 Más usuarios adquieren nuestras Herramientas Premium 🚀
         
        🌐 https://beacons.ai/nanomillenial

        Hoy {fecha} seguimos sumando clientes satisfechos ✅
        """,

                f"""
        🚀 Nuevos usuarios están ingresando a nuestras Herramientas Premium 📈

        🌐 https://beacons.ai/nanomillenial

        Hoy {fecha} continúa creciendo la comunidad 🔥
        """,

                f"""
        💎 Más personas están obteniendo acceso a nuestras Herramientas Premium 🚀

        🌐 https://beacons.ai/nanomillenial

        Hoy {fecha} seguimos recibiendo nuevos usuarios ✅
        """
            ]

            texto = random.choice(textos_pagos)

        elif tipo == "fdi":

            textos_fdi = [

                f"""
        💸 Nuevos pagos enviados desde el Fondo de Inversión FDI 📈

        💰 https://t.me/inversionesFDI

        Hoy {fecha} continuamos cumpliendo con la comunidad ✅
        """,

                f"""
        📊 Más resultados del Fondo de Inversión FDI 🚀

        💰 https://t.me/inversionesFDI

        Hoy {fecha} seguimos realizando pagos a inversionistas 💰
        """,

                f"""
        🔥 Nuevos comprobantes de pago del Fondo de Inversión FDI 📈

        💰 https://t.me/inversionesFDI

        Hoy {fecha} continúan llegando resultados para la comunidad ✅
        """
            ]

            texto = random.choice(textos_fdi)

        elif tipo == "copytrade":

            textos_copytrade = [

                f"""
        📈 Nuevos resultados de CopyTrade IA🚀

        🤖 https://t.me/CopyTradePocket

        Hoy {fecha} seguimos mostrando operaciones reales ✅
        """,

                f"""
        🚀 Más operaciones con el sistema CopyTrade 📊

        🤖 https://t.me/CopyTradePocket

        Hoy {fecha} continúan los resultados 🔥
        """,

                f"""
        📊 Nuevas operaciones en CopyTrade IA 📈

        🤖 https://t.me/CopyTradePocket

        Hoy {fecha} seguimos compartiendo resultados reales 🚀
        """
            ]

            texto = random.choice(textos_copytrade)

        else:

            texto = "Story automática"

        # =========================================
        # 🔹 DESCARGAR IMAGEN
        # =========================================

        print("📥 Descargando imagen...")

        response = requests.get(
            imagen_url,
            timeout=20
        )

        with open("story_temp.jpg", "wb") as f:

            f.write(response.content)

        print("✅ Imagen descargada")

        # =========================================
        # 🔹 SUBIR IMAGEN
        # =========================================

        print("📤 Subiendo imagen...")

        file = await telegram.upload_file(
            "story_temp.jpg"
        )

        print("✅ Imagen subida")

        # =========================================
        # 🔹 PUBLICAR STORY
        # =========================================

        print("🚀 Publicando story...")

        await telegram(
            SendStoryRequest(
                peer="me",
                media=InputMediaUploadedPhoto(
                    file=file
                ),
                privacy_rules=[
                    InputPrivacyValueAllowAll()
                ],
                caption=texto,
                pinned=False,
                noforwards=False
            )
        )

        print("✅ STORY PUBLICADA")

        # =========================================
        # 🔹 MARCAR USADA
        # =========================================

        collection.update_one(
            {
                "_id": story["_id"]
            },
            {
                "$set": {
                    "usada": True
                }
            }
        )

        print("✅ Imagen marcada como usada")

    except Exception as e:

        error = str(e)

        if "STORY_SEND_FLOOD" in error:

            print("⛔ Límite semanal de stories alcanzado")
            print(error)

        else:

            print("❌ ERROR PUBLICANDO STORY:")
            print(error)

# =========================================
# 🔹 PROGRAMAR PUBLICACIONES
# =========================================

dias = [
    "mon",
    "wed",
    "fri"
]

async def ejecutar_story():

    await publicar_story()

for dia in dias:

    hora, minuto = obtener_hora_random()

    print(f"📅 {dia} -> {hora}:{minuto:02d}")

    scheduler.add_job(
        ejecutar_story,
        CronTrigger(
            day_of_week=dia,
            hour=hora,
            minute=minuto,
            timezone="America/La_Paz"
        )
    )

# =========================================
# 🔹 MAIN TELEGRAM
# =========================================

def main():

    print("🚀 BOT STORIES ACTIVO EN RENDER")
    print("🔌 Iniciando Telegram...")

    telegram.start()

    print("✅ Telegram conectado:", telegram.is_connected())
    print("✅ Sesión Telegram iniciada correctamente")

    scheduler.start()

    print("✅ Scheduler iniciado")

    iniciar_web()

    telegram.run_until_disconnected()

# =========================================
# 🔹 EJECUTAR
# =========================================

if __name__ == "__main__":

    main()