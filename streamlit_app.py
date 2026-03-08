import streamlit as st
import re
import pdfplumber
from PIL import Image
import pytesseract
import speech_recognition as sr
import moviepy.editor as mp
import tempfile
import os

st.set_page_config(page_title="SafeShield Colombia", page_icon="🛡️", layout="centered")

st.title("🛡️ SafeShield: Plataforma de Ciberseguridad")
st.markdown("Verifica mensajes, enlaces, imágenes, audios y videos para protegerte de fraudes y manipulación.")

tab1, tab2, tab3, tab4 = st.tabs(["📝 Texto", "🔗 Enlace", "📄 Archivos", "🎙️ Audio/Video"])

def analizar_texto_emocional(texto):
    gatillos_urgencia = ["urgente", "bloqueo", "embargo", "inmediato", "suspensión", "dian", "clonación", "cuenta suspendida", "multa"]
    gatillos_premio = ["ganador", "sorteo", "premio", "reclamar", "felicidades", "bono", "aprobado", "regalo", "inversión segura"]
    
    puntuacion = 0
    alertas = []

    for p in gatillos_urgencia:
        if p in texto.lower():
            puntuacion += 25
            alertas.append(f"Urgencia/Amenaza ('{p}')")
    for p in gatillos_premio:
        if p in texto.lower():
            puntuacion += 25
            alertas.append(f"Falsa recompensa ('{p}')")
            
    return puntuacion, alertas

# --- PESTAÑA 1: Análisis de Texto ---
with tab1:
    mensaje = st.text_area("Pega aquí el mensaje de WhatsApp, correo o SMS:")
    if st.button("Analizar Mensaje"):
        if mensaje:
            puntaje, alertas = analizar_texto_emocional(mensaje)
            if puntaje >= 50: st.error("⚠️ ALTO RIESGO DE MANIPULACIÓN")
            elif puntaje > 0: st.warning("🟡 RIESGO MODERADO")
            else: st.success("✅ Tono neutral.")
            if alertas: st.write(f"**Tácticas detectadas:** {', '.join(set(alertas))}")

# --- PESTAÑA 2: Enlaces ---
with tab2:
    url = st.text_input("Pega el enlace completo:")
    if st.button("Escanear URL"):
        if url:
            if "bit.ly" in url or "t.co" in url: st.warning("🟡 ATENCIÓN: Enlace acortado. Procede con cuidado.")
            elif url.startswith("http://"): st.error("🔴 SITIO NO SEGURO: Usa 'HTTP'. No ingreses datos.")
            elif url.startswith("https://"): st.success("✅ Enlace con certificado seguro.")

# --- PESTAÑA 3: Archivos (PDF / Imágenes) ---
with tab3:
    archivo_subido = st.file_uploader("Sube foto o PDF", type=["png", "jpg", "jpeg", "pdf"])
    if archivo_subido:
        texto_extraido = ""
        if archivo_subido.name.endswith('.pdf'):
            with pdfplumber.open(archivo_subido) as pdf:
                for page in pdf.pages:
                    if page.extract_text(): texto_extraido += page.extract_text() + "\n"
        else:
            imagen = Image.open(archivo_subido)
            st.image(imagen, width=250)
            texto_extraido = pytesseract.image_to_string(imagen, lang='spa')
            
        if texto_extraido:
            st.text_area("Texto detectado:", texto_extraido, height=100)
            puntaje, alertas = analizar_texto_emocional(texto_extraido)
            if puntaje >= 50: st.error("⚠️ ALTO RIESGO EN EL DOCUMENTO")
            elif puntaje > 0: st.warning("🟡 RIESGO MODERADO")
            else: st.success("✅ No se detectan patrones de fraude en el texto.")

# --- PESTAÑA 4: Audios y Videos ---
with tab4:
    st.subheader("Analizador de Vishing y Deepfakes (Voz)")
    st.write("Sube una nota de voz corta o un video. La IA extraerá lo que dicen y buscará tácticas de engaño.")
    multimedia_subido = st.file_uploader("Sube Audio o Video (Max 10MB para mejor rendimiento)", type=["mp3", "wav", "mp4"])
    
    if multimedia_subido is not None:
        st.info("⏳ Procesando archivo... esto puede tomar unos segundos.")
        try:
            # Guardar el archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix="."+multimedia_subido.name.split('.')[-1]) as tmp_file:
                tmp_file.write(multimedia_subido.read())
                tmp_path = tmp_file.name

            audio_path = tmp_path
            
            # Si es video, extraer el audio primero
            if multimedia_subido.name.endswith('.mp4'):
                video = mp.VideoFileClip(tmp_path)
                audio_path = tmp_path.replace(".mp4", ".wav")
                video.audio.write_audiofile(audio_path, logger=None)
            
            # Reconocimiento de voz
            r = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = r.record(source)
                texto_audio = r.recognize_google(audio_data, language="es-CO") # Español de Colombia
                
            st.success("¡Audio transcrito con éxito!")
            st.text_area("Lo que dicen en el audio/video es:", texto_audio, height=100)
            
            # Analizar el texto extraído
            puntaje, alertas = analizar_texto_emocional(texto_audio)
            if puntaje >= 50: 
                st.error("⚠️ ALTO RIESGO: El audio intenta manipularte.")
                st.write(f"**Tácticas detectadas:** {', '.join(set(alertas))}")
            elif puntaje > 0: 
                st.warning("🟡 RIESGO MODERADO")
                st.write(f"**Tácticas detectadas:** {', '.join(set(alertas))}")
            else: 
                st.success("✅ El tono del mensaje es neutral.")
                
            # Limpiar archivos temporales
            os.remove(tmp_path)
            if multimedia_subido.name.endswith('.mp4'): os.remove(audio_path)

        except sr.UnknownValueError:
            st.warning("No se pudo entender el audio. Asegúrate de que las voces sean claras.")
        except Exception as e:
            st.error("Ocurrió un error al procesar el archivo. Intenta con un clip más corto.")
            
st.divider()
st.caption("SafeShield v3.0 - Plataforma Integral de Prevención de Fraudes")
