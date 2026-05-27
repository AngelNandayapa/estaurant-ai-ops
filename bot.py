import telebot
import os
import time
import json
import pandas as pd
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv


load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RUTA_JSON_BOT = os.getenv("RUTA_JSON_BOT", "bot-fxyx.json")
NOMBRE_SHEET = os.getenv("NOMBRE_SHEET", "Base_Datos_FXYX")


bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')


if not os.path.exists("archivos_telegram"):
    os.makedirs("archivos_telegram")

prompt = """
Eres un auditor contable experto. Analiza la imagen o documento adjunto.
Usa la siguiente lógica paso a paso antes de extraer los datos:
1. Identifica cuántos recibos/tickets físicos hay en la imagen.
2. Para cada recibo, busca la fecha de compra principal.
3. Identifica si es "Factura" (solo si dice explícitamente RFC, UUID o Uso CFDI) o "Nota" (ticket de caja normal).
4. REGLA DE BALANCE CONTABLE (CRÍTICO): El 'gasto_total_articulo' de la lista de artículos debe sumar exactamente el TOTAL FINAL pagado en el ticket.
   - Si el recibo desglosa impuestos (IVA, IEPS), propinas o comisiones, DEBES agregarlos como un artículo adicional. (Ej. articulo: "IVA 16%", categoria: "Impuestos", gasto_total_articulo: 150.00).
   - Si el recibo tiene DESCUENTOS, DEBES agregarlos como un artículo adicional con un monto NEGATIVO. (Ej. articulo: "Descuento", categoria: "Descuentos", gasto_total_articulo: -50.00).

Devuelve ÚNICAMENTE un JSON válido con esta estructura:
{
  "documentos_encontrados": [
    {
      "tipo_documento": "Factura o Nota",
      "lugar_compra": "Nombre del proveedor",
      "fecha": "YYYY-MM-DD",
      "articulos": [
        {"articulo": "nombre exacto", "categoria": "categoría", "unidades": 1.0, "gasto_total_articulo": 100.0}
      ]
    }
  ]
}
"""

print("FXYX ONLINE - Bot Auditor Iniciado")

@bot.message_handler(commands=['start'])
def enviar_bienvenida(message):
    bot.reply_to(message, "FXYX HERE - Listo para auditar recibos.")

@bot.message_handler(content_types=['photo', 'document'])
def procesar_factura(message):
    mensaje_estado = bot.reply_to(message, "Analizando archivo, esto puede tardar un poco...")

    try:
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            ruta_archivo = f"archivos_telegram/ticket_{message.message_id}.jpg"
        elif message.content_type == 'document':
            file_id = message.document.file_id
            nombre_original = message.document.file_name if message.document.file_name else f"doc_{message.message_id}.pdf"
            ruta_archivo = f"archivos_telegram/{nombre_original}"

        file_info = bot.get_file(file_id)
        archivo_descargado = bot.download_file(file_info.file_path)

        with open(ruta_archivo, 'wb') as f:
            f.write(archivo_descargado)

        archivo_ia = genai.upload_file(path=ruta_archivo)
        response = model.generate_content(
            [prompt, archivo_ia],
            generation_config={"response_mime_type": "application/json"}
        )

        datos = json.loads(response.text.strip())
        if isinstance(datos, list):
            datos = datos[0] if len(datos) > 0 else {}

        lista_documentos = datos.get("documentos_encontrados", [])
        filas_nuevas = []

        for doc in lista_documentos:
            tipo_doc = doc.get("tipo_documento", "Nota")
            lugar = str(doc.get("lugar_compra", "")).upper()
            fecha = doc.get("fecha")

            supermercados = ["SORIANA", "CHEDRAUI", "HEB", "WALMART", "OXXO", "SAMS", "SAM'S", "COSTCO", "BODEGA AURRERA"]
            if any(super_name in lugar for super_name in supermercados):
                tipo_doc = "Nota"

            for art in doc.get("articulos", []):
                filas_nuevas.append({
                    "Fecha": fecha,
                    "Tipo de Documento": tipo_doc,
                    "Lugar de Compra": lugar,
                    "Artículo": art.get("articulo"),
                    "Categoría": art.get("categoria"),
                    "Unidades": art.get("unidades"),
                    "Gasto Total": art.get("gasto_total_articulo")
                })

        if not filas_nuevas:
            bot.edit_message_text("No le entendí al recibo, mándame mensaje para arreglarlo.", chat_id=message.chat.id, message_id=mensaje_estado.message_id)
            return

        bot.edit_message_text("Procesamiento de IA exitoso. Subiendo las cosas a Google Sheets...", chat_id=message.chat.id, message_id=mensaje_estado.message_id)

        df_nuevo = pd.DataFrame(filas_nuevas)
        df_nuevo['Fecha_dt'] = pd.to_datetime(df_nuevo['Fecha'], errors='coerce')

        df_nuevo['Mes_Pestaña'] = df_nuevo['Fecha_dt'].dt.strftime('%Y-%m').fillna('Sin_Fecha')
        dias_es = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
        df_nuevo['Día'] = df_nuevo['Fecha_dt'].dt.dayofweek.map(dias_es).fillna('')
        df_nuevo['Semana'] = df_nuevo['Fecha_dt'].dt.strftime('Sem. %V').fillna('')
        df_nuevo['Fecha'] = df_nuevo['Fecha_dt'].dt.strftime('%Y-%m-%d')

        columnas_ordenadas = ['Fecha', 'Día', 'Semana', 'Tipo de Documento', 'Lugar de Compra', 'Artículo', 'Categoría', 'Unidades', 'Gasto Total', 'Mes_Pestaña']
        df_nuevo = df_nuevo.reindex(columns=columnas_ordenadas).fillna("")

        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credenciales = Credentials.from_service_account_file(RUTA_JSON_BOT, scopes=scopes)
        cliente = gspread.authorize(credenciales)
        sheet_nube = cliente.open(NOMBRE_SHEET)

        for mes, datos_mes in df_nuevo.groupby('Mes_Pestaña'):
            datos_limpios = datos_mes.drop(columns=['Mes_Pestaña'])
            valores_a_insertar = datos_limpios.values.tolist()

            try:
                pestaña = sheet_nube.worksheet(str(mes))
            except gspread.exceptions.WorksheetNotFound:
                print(f"Creando nuevo mes clonando la plantilla para: {mes}")
                plantilla = sheet_nube.worksheet("Plantilla")

                sheet_nube.duplicate_sheet(
                    source_sheet_id=plantilla.id,
                    new_sheet_name=str(mes)
                )
                pestaña = sheet_nube.worksheet(str(mes))

            pestaña.append_rows(valores_a_insertar, value_input_option='USER_ENTERED')

        total_ticket = df_nuevo['Gasto Total'].astype(float).sum()
        bot.edit_message_text(f"✅ Listo. Registré ${total_ticket:,.2f} MXN en la base de datos.", chat_id=message.chat.id, message_id=mensaje_estado.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Ocurrió un error en el servidor:\n{e}", chat_id=message.chat.id, message_id=mensaje_estado.message_id)

bot.infinity_polling()