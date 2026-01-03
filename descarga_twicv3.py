import requests
import zipfile
import os
import io
import streamlit as st
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
TWIC_START_DATE = datetime(1994, 9, 17)
TWIC_START_NUMBER = 1
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def get_latest_real_twic():
    est_latest = (datetime.now() - TWIC_START_DATE).days // 7 + TWIC_START_NUMBER
    for num in range(est_latest + 1, est_latest - 15, -1):
        try:
            r = requests.head(f"https://theweekinchess.com/zips/twic{num}g.zip", headers=HEADERS, timeout=5)
            if r.status_code == 200: return num
        except: continue
    return 1625

def get_twic_range(year, month=None):
    start_date = datetime(year, month if month else 1, 1)
    if month:
        if month == 12: end_date = datetime(year, 12, 31)
        else: end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    else: end_date = datetime(year, 12, 31)
    
    s = (start_date - TWIC_START_DATE).days // 7 + TWIC_START_NUMBER
    e = (end_date - TWIC_START_DATE).days // 7 + TWIC_START_NUMBER
    return max(1, s), e

def process_downloads(start, end, limit):
    real_end = min(end, limit)
    all_pgn_content = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = real_end - start + 1
    for i, num in enumerate(range(start, real_end + 1)):
        url = f"https://theweekinchess.com/zips/twic{num}g.zip"
        status_text.text(f"Descargando edición {num}...")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                    pgn_name = next((f for f in z.namelist() if f.lower().endswith('.pgn')), None)
                    if pgn_name:
                        content = z.read(pgn_name).decode('utf-8', errors='ignore')
                        all_pgn_content.append(content)
            progress_bar.progress((i + 1) / total)
        except: continue
    
    # Limpiar indicadores de progreso al terminar
    progress_bar.empty()
    status_text.empty()
    
    if all_pgn_content:
        return "\n\n".join(all_pgn_content), f"{start}_{real_end}.pgn"
    return None, None

# --- INTERFAZ STREAMLIT ---
st.title("♟️ TWIC Downloader")

# Calculamos el último número en segundo plano para que el código funcione,
# pero ya no mostramos el mensaje st.info()
latest = get_latest_real_twic()

opcion = st.selectbox("¿Qué deseas descargar?", ["Año completo", "Mes específico", "Última edición"])

archivo_final = None
nombre_archivo = ""

if opcion == "Año completo":
    year = st.number_input("Año", min_value=1994, max_value=datetime.now().year, value=datetime.now().year)
    if st.button("Preparar descarga"):
        s, e = get_twic_range(year)
        archivo_final, nombre_archivo = process_downloads(s, e, latest)

elif opcion == "Mes específico":
    col1, col2 = st.columns(2)
    year = col1.number_input("Año", min_value=1994, max_value=datetime.now().year, value=datetime.now().year)
    month = col2.number_input("Mes (1-12)", min_value=1, max_value=12, value=datetime.now().month)
    if st.button("Preparar descarga"):
        s, e = get_twic_range(year, month)
        archivo_final, nombre_archivo = process_downloads(s, e, latest)

elif opcion == "Última edición":
    if st.button("Preparar descarga"):
        archivo_final, nombre_archivo = process_downloads(latest, latest, latest)

if archivo_final:
    st.success("✅ ¡Archivo consolidado listo!")
    st.download_button(
        label="⬇️ Descargar PGN",
        data=archivo_final,
        file_name=nombre_archivo,
        mime="text/plain"
    )