import streamlit as st
import re
import requests
from collections import defaultdict
import io

# --- CONFIGURACIÓN Y LOGICA INTERNA (Tu código original adaptado) ---
FILE_ID = '1Trc-xwyr8y-FcPzzyrP92lWzLsMt9MlQ'

def get_pgn_stream():
    url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            return response
    except:
        return None
    return None

def buscar_jugadores_web(termino):
    response = get_pgn_stream()
    if not response: return {}
    
    jugadores = defaultdict(int)
    # Leemos línea a línea para no colapsar la memoria del servidor
    for line in response.iter_lines():
        linea = line.decode('utf-8', errors='ignore')
        if linea.startswith('[White "') or linea.startswith('[Black "'):
            match = re.match(r'\[(White|Black) "([^"]+)"\]', linea)
            if match:
                nombre = match.group(2)
                if termino.lower() in nombre.lower():
                    jugadores[nombre] += 1
    return dict(sorted(jugadores.items(), key=lambda x: x[1], reverse=True))

def cumple_filtros(partida_dict, jugador, color, año_min, año_max):
    # Lógica de filtrado idéntica a la tuya
    blancas = partida_dict.get('White', '')
    negras = partida_dict.get('Black', '')
    
    if color == "Blancas" and jugador != blancas: return False
    if color == "Negras" and jugador != negras: return False
    if not color and jugador != blancas and jugador != negras: return False
    
    fecha = partida_dict.get('Date', '')
    match = re.match(r'(\d{4})', fecha)
    if match:
        año = int(match.group(1))
        if año_min and año < año_min: return False
        if año_max and año > año_max: return False
    elif año_min or año_max:
        return False
        
    return True

# --- INTERFAZ DE USUARIO CON STREAMLIT ---
st.set_page_config(page_title="Filtrador PGN Canaria", page_icon="♟️")

st.title("♟️ Filtrador de Partidas de Ajedrez")
st.markdown("### Base Canaria de Partidas")

# Sidebar para filtros
st.sidebar.header("Opciones de Filtrado")
termino = st.sidebar.text_input("1. Buscar Jugador:", placeholder="Ej: Perez")

if termino:
    # Usamos cache para no buscar en Drive cada vez que cambiamos un filtro
    @st.cache_data(ttl=600)
    def cached_search(t):
        return buscar_jugadores_web(t)
    
    resultados = cached_search(termino)
    
    if resultados:
        jugador_sel = st.selectbox("2. Selecciona el jugador exacto:", list(resultados.keys())[:50])
        
        col1, col2 = st.columns(2)
        with col1:
            color_sel = st.selectbox("Color:", ["Todas", "Blancas", "Negras"])
        with col2:
            años = st.slider("Rango de años:", 1970, 2026, (1990, 2026))
            
        if st.button("🔍 Extraer Partidas"):
            with st.spinner('Procesando base de datos...'):
                response = get_pgn_stream()
                partidas_texto = []
                partida_actual = []
                metadatos = {}
                
                for line in response.iter_lines():
                    linea = line.decode('utf-8', errors='ignore').rstrip()
                    
                    if linea.startswith('[Event '):
                        if partida_actual and cumple_filtros(metadatos, jugador_sel, 
                                                           None if color_sel=="Todas" else color_sel, 
                                                           años[0], años[1]):
                            partidas_texto.append("\n".join(partida_actual))
                        
                        partida_actual = [linea]
                        metadatos = {}
                    else:
                        if linea: partida_actual.append(linea)
                        match = re.match(r'\[(\w+)\s+"([^"]*)"\]', linea)
                        if match:
                            metadatos[match.group(1)] = match.group(2)

                # Última partida
                if partida_actual and cumple_filtros(metadatos, jugador_sel, 
                                                   None if color_sel=="Todas" else color_sel, 
                                                   años[0], años[1]):
                    partidas_texto.append("\n".join(partida_actual))

                if partidas_texto:
                    pgn_final = "\n\n".join(partidas_texto)
                    st.success(f"¡Se han encontrado {len(partidas_texto)} partidas!")
                    
                    # Botón de descarga
                    st.download_button(
                        label="💾 Descargar archivo PGN",
                        data=pgn_final,
                        file_name=f"{jugador_sel.replace(' ', '_')}.pgn",
                        mime="text/plain",
                    )
                else:
                    st.warning("No se encontraron partidas con esos filtros.")
    else:
        st.error("No se encontraron jugadores.")

st.divider()
st.caption("Los datos se extraen en tiempo real de Google Drive.")