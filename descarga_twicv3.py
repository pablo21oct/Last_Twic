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

# --- CSS PERSONALIZADO CON TEMA DE AJEDREZ ---
st.markdown("""
<style>
    /* Fondo estilo tablero de ajedrez sutil */
    .stApp {
        background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
    }
    
    /* Patrón de tablero sutil en el fondo */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0.03;
        background-image: 
            repeating-linear-gradient(45deg, #000 0px, #000 20px, transparent 20px, transparent 40px),
            repeating-linear-gradient(-45deg, #000 0px, #000 20px, transparent 20px, transparent 40px);
        z-index: -1;
        pointer-events: none;
    }
    
    /* Tarjetas con estilo tablero */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        border: 2px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    
    /* Título principal estilo ajedrez */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2c3e50 0%, #000000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Estadísticas estilo casillas de ajedrez */
    .stat-box {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 0.5rem;
        border: 3px solid #bdc3c7;
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Botones estilo ajedrez */
    .stButton>button {
        background: linear-gradient(135deg, #2c3e50 0%, #000000 100%);
        color: white;
        border: 2px solid #34495e;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
    }
    
    /* Progress bar estilo ajedrez */
    .stProgress > div > div {
        background: linear-gradient(90deg, #2c3e50 0%, #000000 100%);
    }
    
    /* Success message estilo victoria */
    .success-box {
        background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1rem 0;
        border: 3px solid #1e8449;
    }
    
    /* Download button destacado */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        font-size: 1.3rem;
        padding: 1.2rem 2rem;
        border-radius: 10px;
        border: 3px solid #a93226;
        width: 100%;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .stDownloadButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 10px 25px rgba(231, 76, 60, 0.4);
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
    }
    
    /* Información adicional */
    .info-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2c3e50;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Selectbox personalizado */
    .stSelectbox label {
        color: #2c3e50;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Header con pieza de ajedrez */
    .chess-header {
        text-align: center;
        padding: 2rem 0;
        background: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #e0e0e0;
    }
    
    /* Iconos de piezas */
    .chess-piece {
        font-size: 4rem;
        margin: 1rem;
        display: inline-block;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));
    }
    
    /* Footer estilo tablero */
    .footer {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 3rem;
        border: 3px solid #bdc3c7;
    }
</style>
""", unsafe_allow_html=True)

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
    downloaded = 0
    
    for i, num in enumerate(range(start, real_end + 1)):
        url = f"https://theweekinchess.com/zips/twic{num}g.zip"
        status_text.markdown(f"""
        <div class='info-card'>
            <strong>♟️ Descargando edición {num} de {real_end}</strong><br>
            <small>Progreso: {i+1}/{total} archivos procesados</small>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                    pgn_name = next((f for f in z.namelist() if f.lower().endswith('.pgn')), None)
                    if pgn_name:
                        content = z.read(pgn_name).decode('utf-8', errors='ignore')
                        all_pgn_content.append(content)
                        downloaded += 1
            progress_bar.progress((i + 1) / total)
        except: 
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    if all_pgn_content:
        return "\n\n".join(all_pgn_content), f"twic_{start}_{real_end}.pgn", downloaded, total
    return None, None, 0, total

# --- INTERFAZ STREAMLIT ---

# Header con piezas de ajedrez
st.markdown("""
<div class='chess-header'>
    <span class='chess-piece'>♔</span>
    <span class='chess-piece'>♕</span>
    <span class='chess-piece'>♖</span>
    <span class='chess-piece'>♗</span>
    <span class='chess-piece'>♘</span>
    <span class='chess-piece'>♙</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>♟️ TWIC DOWNLOADER</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>The Week in Chess | Descarga partidas profesionales desde 1994</p>", unsafe_allow_html=True)

# Calculamos el último número
latest = get_latest_real_twic()

# Estadísticas con estilo tablero
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class='stat-box'>
        <p class='stat-number'>♜ {latest}</p>
        <p class='stat-label'>Última edición</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_years = datetime.now().year - 1994 + 1
    st.markdown(f"""
    <div class='stat-box'>
        <p class='stat-number'>♛ {total_years}</p>
        <p class='stat-label'>Años disponibles</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='stat-box'>
        <p class='stat-number'>♚ 1994</p>
        <p class='stat-label'>Año inicio</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Contenedor principal
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    st.markdown("### ♟️ Selecciona qué descargar")
    opcion = st.selectbox(
        "Opciones de descarga",
        ["📅 Año completo", "📆 Mes específico", "⚡ Última edición"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)

    archivo_final = None
    nombre_archivo = ""
    stats_download = None

    if opcion == "📅 Año completo":
        st.markdown("#### 📅 Descarga de año completo")
        year = st.number_input(
            "Selecciona el año", 
            min_value=1994, 
            max_value=datetime.now().year, 
            value=datetime.now().year
        )
        
        if st.button("♟️ PREPARAR DESCARGA", key="btn_year"):
            with st.spinner("♞ Procesando petición..."):
                s, e = get_twic_range(year)
                archivo_final, nombre_archivo, downloaded, total = process_downloads(s, e, latest)
                stats_download = (downloaded, total)

    elif opcion == "📆 Mes específico":
        st.markdown("#### 📆 Descarga de mes específico")
        col1, col2 = st.columns(2)
        year = col1.number_input(
            "Año", 
            min_value=1994, 
            max_value=datetime.now().year, 
            value=datetime.now().year
        )
        month = col2.number_input(
            "Mes (1-12)", 
            min_value=1, 
            max_value=12, 
            value=datetime.now().month
        )
        
        if st.button("♟️ PREPARAR DESCARGA", key="btn_month"):
            with st.spinner("♞ Procesando petición..."):
                s, e = get_twic_range(year, month)
                archivo_final, nombre_archivo, downloaded, total = process_downloads(s, e, latest)
                stats_download = (downloaded, total)

    elif opcion == "⚡ Última edición":
        st.markdown("#### ⚡ Descarga la edición más reciente")
        st.info(f"♔ La última edición disponible es la **TWIC {latest}**")
        
        if st.button("♟️ PREPARAR DESCARGA", key="btn_latest"):
            with st.spinner("♞ Procesando petición..."):
                archivo_final, nombre_archivo, downloaded, total = process_downloads(latest, latest, latest)
                stats_download = (downloaded, total)

    if archivo_final:
        st.markdown("<div class='success-box'>♔ ¡JAQUE MATE! Archivo listo para descargar</div>", unsafe_allow_html=True)
        
        if stats_download:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("♟️ Archivos procesados", f"{stats_download[0]}/{stats_download[1]}")
            with col2:
                st.metric("📦 Tamaño total", f"{len(archivo_final) / 1024 / 1024:.1f} MB")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="♕ DESCARGAR ARCHIVO PGN",
            data=archivo_final,
            file_name=nombre_archivo,
            mime="text/plain",
            use_container_width=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer estilo tablero
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class='footer'>
    <h3 style='margin: 0 0 1rem 0;'>♚ THE WEEK IN CHESS ♚</h3>
    <p style='margin: 0; opacity: 0.9;'>
        Base de datos profesional de partidas de ajedrez desde 1994<br>
        <small>Desarrollado con ❤️ por la comunidad de ajedrez</small>
    </p>
    <div style='margin-top: 1rem; font-size: 2rem;'>
        ♔ ♕ ♖ ♗ ♘ ♙
    </div>
</div>
""", unsafe_allow_html=True)
