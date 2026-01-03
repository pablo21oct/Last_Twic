import requests
import zipfile
import os
import io
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
from pathlib import Path

# --- CONFIGURACIÓN ---
TWIC_START_DATE = datetime(1994, 9, 17)
TWIC_START_NUMBER = 1
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def get_latest_real_twic():
    """Busca la última edición real para evitar errores 404"""
    est_latest = (datetime.now() - TWIC_START_DATE).days // 7 + TWIC_START_NUMBER
    print(f"🔍 Sincronizando con TWIC... (Estimado: {est_latest})")
    for num in range(est_latest + 1, est_latest - 15, -1):
        try:
            r = requests.head(f"https://theweekinchess.com/zips/twic{num}g.zip", headers=HEADERS, timeout=5)
            if r.status_code == 200: return num
        except: continue
    return 1625

def get_twic_range(year, month=None):
    """Calcula el rango de números para fechas"""
    start_date = datetime(year, month if month else 1, 1)
    if month:
        if month == 12: end_date = datetime(year, 12, 31)
        else: end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    else: end_date = datetime(year, 12, 31)
    
    s = (start_date - TWIC_START_DATE).days // 7 + TWIC_START_NUMBER
    e = (end_date - TWIC_START_DATE).days // 7 + TWIC_START_NUMBER
    return max(1, s), e

def process_downloads(start, end, limit, output_dir):
    real_end = min(end, limit) # No pasarse del último existente
    all_pgn_content = []
    
    print(f"\n🚀 Procesando TWIC {start} al {real_end}...")
    
    for num in range(start, real_end + 1):
        url = f"https://theweekinchess.com/zips/twic{num}g.zip"
        print(f"  📥 Descargando {num}...", end=' ', flush=True)
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                    pgn_name = next((f for f in z.namelist() if f.lower().endswith('.pgn')), None)
                    if pgn_name:
                        content = z.read(pgn_name).decode('utf-8', errors='ignore')
                        all_pgn_content.append(content)
                        print("✅")
            else: print("❌ (No disponible)")
        except: print("⚠️ Error")
    
    if all_pgn_content:
        # AQUÍ ESTÁ EL CAMBIO DEL NOMBRE QUE PEDISTE
        filename = f"{start}_{real_end}.pgn"
        full_path = os.path.join(output_dir, filename)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            for pgn in all_pgn_content:
                f.write(pgn + "\n\n")
        
        print(f"\n✨ ¡Éxito! Archivo consolidado creado: {filename}")
        return full_path
    return None

def main():
    root = tk.Tk(); root.withdraw() # Ocultar ventana base de Windows
    
    latest = get_latest_real_twic()
    print(f"✅ Última edición disponible: {latest}\n")

    print("1. Descargar AÑO completo")
    print("2. Descargar MES específico")
    print("3. Descargar última edición")
    opc = input("\nSelecciona opción: ")

    # Pedir carpeta visualmente
    folder = filedialog.askdirectory(title="¿Dónde guardar el PGN consolidado?")
    if not folder: return

    if opc == '1':
        year = int(input("Año: "))
        s, e = get_twic_range(year)
        process_downloads(s, e, latest, folder)
    elif opc == '2':
        year = int(input("Año: "))
        month = int(input("Mes (1-12): "))
        s, e = get_twic_range(year, month)
        process_downloads(s, e, latest, folder)
    elif opc == '3':
        process_downloads(latest, latest, latest, folder)

if __name__ == "__main__":
    main()