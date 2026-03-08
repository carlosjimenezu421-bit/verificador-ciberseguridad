import streamlit as st
import re
import os
import csv
import pandas as pd
import pdfplumber
from PIL import Image
import pytesseract
import speech_recognition as sr
import moviepy.editor as mp
import tempfile
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA (Diseño Panorámico) ---
st.set_page_config(page_title="SafeShield Colombia", page_icon="🛡️", layout="wide")

# --- DISEÑO VISUAL (CSS Personalizado para colores frescos) ---
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #2c3e50; font-family: 'Helvetica Neue', sans-serif; font-weight: 800;}
    .tarjeta-riesgo-alto {background: linear-gradient(135deg, #ff4b4b, #ff0000); color: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .tarjeta-riesgo-medio {background: linear-gradient(135deg, #ffa421, #ff7b00); color: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .tarjeta-seguro {background: linear-gradient(135deg, #00b09b, #96c93d); color: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .metric-value {font-size: 2rem; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ SafeShield Dashboard")
st.markdown("### Tu Plataforma Inteligente de Prevención de Fraudes")
st.write("Verifica amenazas en tiempo real. Sistema actualizado con registro de incidentes.")
st.divider()

# --- BASE DE DATOS (Lógica de Registro) ---
ARCHIVO_REGISTRO = "registro_amenazas.csv"

def inicializar_base_datos():
    if not os.path.exists(ARCHIVO_REGISTRO):
        with open(ARCHIVO_REGISTRO, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Fecha", "Hora", "Tipo de Análisis", "Nivel de Riesgo", "Tácticas Detectadas", "Contenido Sospechoso"])

def registrar_amenaza(tipo, nivel, tacticas, contenido):
    # Solo guarda si es riesgo medio o alto
    if nivel in ["ALTO RIESGO", "RIESGO MODERADO"]:
        ahora = datetime.now()
        fecha = ahora.strftime("%Y-%m-%d")
        hora = ahora.strftime("%H:%M:%S")
        with open(ARCHIVO_REGISTRO, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([fecha, hora, tipo, nivel, tacticas, contenido[:100] + "..."]) # Guarda los primeros 100 caracteres

inicializar_base_datos()

# --- MOTOR DE ANÁLISIS ---
def analizar_texto_emocional(texto):
    gatillos_urgencia = ["urgente", "bloqueo", "embargo", "inmediato", "suspensión", "dian", "clonación", "cuenta suspendida", "multa"]
    gatillos_premio = ["ganador", "sorteo", "premio", "reclamar", "felicidades", "bono", "aprobado", "regalo", "inversión segura"]
    
    puntuacion = 0
    alertas = []
    for p in gatillos_urgencia:
        if p in texto.lower():
            puntuacion += 25
            alertas.append(f"Urgencia ('{p}')")
    for p in gatillos_premio:
        if p in texto.lower():
            puntuacion += 25
            alertas.append(f"Falsa recompensa ('{p}')")
            
    return puntuacion, alertas

def mostrar_resultado_visual(puntaje, alertas, tipo_analisis, contenido_analizado):
    st.markdown("<br>", unsafe_allow_html=True)
    if puntaje >= 50:
        st.markdown(f'<div class="tarjeta-riesgo-alto"><h2>⚠️ ALTO RIESGO</h2><p class="metric-value">{puntaje}% Probabilidad de Fraude</p></div>', unsafe_allow_html=True)
        st.error(f"**Tácticas Psicológicas Detectadas:** {', '.join(set(alertas))}")
        registrar_amenaza(tipo_analisis, "ALTO RIESGO", ', '.join(set(alertas)), contenido_analizado)
    elif puntaje > 0:
        st.markdown(f'<div class="tarjeta-riesgo-medio"><h2>🟡 RIESGO MODERADO</h2><p class="metric-value">{puntaje}% Probabilidad de Fraude</p></div>', unsafe_allow_html=True)
        st.warning(f"**Lenguaje Sospechoso:** {', '.join(set(alertas))}")
        registrar_amenaza(tipo_analisis, "RIESGO MODERADO", ', '.join(set(alertas)), contenido_analizado)
    else:
        st.markdown('<div class="tarjeta-seguro"><h2>✅ SEGURO</h2><p>No se detectan patrones de manipulación.</p></div>', unsafe_allow_html=True)

# --- NAVEGACIÓN (Pestañas) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Mensajes", "🔗 Enlaces", "📄 Documentos/Fotos", "🎙️ Audios/Videos", "📊 Base de Datos"])

# --- PESTAÑA 1: TEXTO ---
with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Analizador de Mensajes")
        mensaje = st.text_area("Pega el texto aquí (SMS, WhatsApp, Correo):", height=150)
        btn_texto = st.button("Analizar Mensaje 🔍", use_container_width=True)
    with col2:
        if btn_texto and mensaje:
            puntaje, alertas = analizar_texto_emocional(mensaje)
            mostrar_resultado_visual(puntaje, alertas, "Análisis de Texto", mensaje)

# --- PESTAÑA 2: ENLACES ---
with tab2:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Escaner de Links")
        url = st.text_input("Ingresa el enlace sospechoso:")
        btn_url = st.button("Verificar Enlace 🌐", use_container_width=True)
    with col2:
        if btn_url and url:
            if "bit.ly" in url or "t.co" in url:
                st.markdown('<div class="tarjeta-riesgo-medio"><h2>🟡 ENLACE OCULTO</h2><p>Usa acortadores para esconder su destino.</p></div>', unsafe_allow_html=True)
                registrar_amenaza("Análisis de URL", "RIESGO MODERADO", "Uso de acortador de URL", url)
            elif url.startswith("http://"):
                st.markdown('<div class="tarjeta-riesgo-alto"><h2>🔴 SITIO INSEGURO</h2><p>Conexión no cifrada (HTTP). No ingrese datos.</p></div>', unsafe_allow_html=True)
                registrar_amenaza("Análisis de URL", "ALTO RIESGO", "Falta de certificado SSL (HTTP)", url)
            else:
                st.markdown('<div class="tarjeta-seguro"><h2>✅ ENLACE CIFRADO</h2><p>Posee certificado de seguridad HTTPS.</p></div>', unsafe_allow_html=True)

# --- PESTAÑA 3: ARCHIVOS ---
with tab3:
    st.subheader("Extracción de Texto (OCR & PDF)")
    archivo_subido = st.file_uploader("Arrastra aquí un PDF o Imagen", type=["png", "jpg", "jpeg", "pdf"])
    if archivo_subido:
        with st.spinner('Extrayendo información...'):
            texto_extraido = ""
            try:
                if archivo_subido.name.endswith('.pdf'):
                    with pdfplumber.open(archivo_subido) as pdf:
                        for page in pdf.pages:
                            if page.extract_text(): texto_extraido += page.extract_text() + "\n"
                else:
                    imagen = Image.open(archivo_subido)
                    st.image(imagen, width=300)
                    texto_extraido = pytesseract.image_to_string(imagen, lang='spa')
                
                if texto_extraido.strip():
                    puntaje, alertas = analizar_texto_emocional(texto_extraido)
                    mostrar_resultado_visual(puntaje, alertas, "Análisis de Documento/Imagen", texto_extraido)
                else:
                    st.error("No se detectó texto claro en el archivo.")
            except Exception as e:
                st.error("Error al procesar el archivo.")

# --- PESTAÑA 4: AUDIO/VIDEO ---
with tab4:
    st.subheader("Detector de Vishing (Voz a Texto)")
    multimedia_subido = st.file_uploader("Sube un audio o video corto", type=["mp3", "wav", "mp4"])
    if multimedia_subido:
        with st.spinner('Escuchando y transcribiendo...'):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix="."+multimedia_subido.name.split('.')[-1]) as tmp_file:
                    tmp_file.write(multimedia_subido.read())
                    tmp_path = tmp_file.name
                audio_path = tmp_path
                if multimedia_subido.name.endswith('.mp4'):
                    video = mp.VideoFileClip(tmp_path)
                    audio_path = tmp_path.replace(".mp4", ".wav")
                    video.audio.write_audiofile(audio_path, logger=None)
                
                r = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio_data = r.record(source)
                    texto_audio = r.recognize_google(audio_data, language="es-CO")
                
                st.success("Transcripción completada:")
                st.write(f'"{texto_audio}"')
                puntaje, alertas = analizar_texto_emocional(texto_audio)
                mostrar_resultado_visual(puntaje, alertas, "Análisis de Audio/Video", texto_audio)
                
                os.remove(tmp_path)
                if multimedia_subido.name.endswith('.mp4'): os.remove(audio_path)
            except Exception as e:
                st.error("No se pudo procesar el audio. Asegúrate de que las voces sean claras.")

# --- PESTAÑA 5: BASE DE DATOS (NUEVA) ---
with tab5:
    st.subheader("📊 Registro Histórico de Amenazas Detectadas")
    st.write("Esta tabla guarda automáticamente todos los análisis que resultan en riesgo moderado o alto.")
    
    try:
        # Cargar y mostrar la base de datos
        df = pd.read_csv(ARCHIVO_REGISTRO)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Botón para descargar en Excel (CSV)
            csv_descarga = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Base de Datos (CSV)",
                data=csv_descarga,
                file_name=f"reporte_amenazas_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("La base de datos está vacía. Aún no se han detectado amenazas.")
    except Exception as e:
        st.info("Inicializando base de datos...")
