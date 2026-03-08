from urllib.parse import urlparse
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
st.image("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80", use_container_width=True)

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
        st.image("https://images.unsplash.com/photo-1563013544-824ae1b704d3?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", width=250)
        mensaje = st.text_area("Pega el texto aquí (SMS, WhatsApp, Correo):", height=150)
        btn_texto = st.button("Analizar Mensaje 🔍", use_container_width=True)
    with col2:
        if btn_texto and mensaje:
            puntaje, alertas = analizar_texto_emocional(mensaje)
            mostrar_resultado_visual(puntaje, alertas, "Análisis de Texto", mensaje)
# --- PESTAÑA 2: ENLACES, NOTICIAS Y REDES ---
with tab2:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Escáner de Noticias y Redes (Colombia)")
        url = st.text_input("Ingresa el enlace (Noticia, Perfil de red social o Web):").strip()
        btn_url = st.button("Verificar Enlace 🌐", use_container_width=True)
    with col2:
        if btn_url and url:
            # Desarmar el enlace para analizarlo
            dominio = urlparse(url).netloc.lower()
            ruta = urlparse(url).path.lower()
            
            # Base de datos de Medios Colombianos y sus usuarios oficiales de redes
            medios_colombia = {
                "eltiempo.com": "eltiempo",
                "elespectador.com": "elespectador",
                "semana.com": "revistasemana",
                "noticiascaracol.com": "noticiascaracol",
                "caracol.com.co": "caracolradio",
                "canalrcn.com": "canalrcn",
                "noticiasrcn.com": "noticiasrcn",
                "rcnradio.com": "rcnradio",
                "wradio.com.co": "wradioco",
                "bluradio.com": "bluradioco",
                "larepublica.co": "larepublica_co",
                "portafolio.co": "portafolioco",
                "elcolombiano.com": "elcolombiano", # Medellín
                "elpais.com.co": "elpaiscali", # Cali
                "elheraldo.co": "elheraldoco", # Barranquilla
                "vanguardia.com": "vanguardiacom", # Bucaramanga
                "pulzo.com": "pulzo",
                "infobae.com": "infobaecolombia"
            }

            redes_sociales = ["instagram.com", "facebook.com", "twitter.com", "x.com", "tiktok.com", "youtube.com", "kwai.com"]
            palabras_suplantacion = ["soporte", "ayuda", "oficial", "admin", "banco", "servicio", "premio", "reembolso", "regalo", "urgente"]

            # 1. ¿Es un enlace acortado? (Alto riesgo de ocultar virus o Fake News)
            if "bit.ly" in url or "t.co" in url or "tinyurl" in url or "is.gd" in url:
                st.markdown('<div class="tarjeta-riesgo-medio"><h2>🟡 ENLACE OCULTO</h2><p>Usa un acortador para esconder su destino real. Mucho cuidado antes de abrirlo.</p></div>', unsafe_allow_html=True)
                registrar_amenaza("Verificación de Enlace", "RIESGO MODERADO", "Uso de acortador", url)
            
            # 2. ¿Es una Red Social?
            elif any(red in dominio for red in redes_sociales):
                es_medio_oficial = False
                nombre_del_medio = ""
                
                # Verificamos si el usuario de la red social coincide con nuestros medios oficiales
                for medio, usuario in medios_colombia.items():
                    if f"/{usuario}" in ruta or f"@{usuario}" in ruta:
                        es_medio_oficial = True
                        nombre_del_medio = medio
                        break
                
                if es_medio_oficial:
                    st.markdown(f'<div class="tarjeta-seguro"><h2>✅ CUENTA DE MEDIO OFICIAL</h2><p>Este perfil coincide con las redes sociales oficiales de <b>{nombre_del_medio}</b>. Sin embargo, confirma siempre que tenga la insignia de verificación.</p></div>', unsafe_allow_html=True)
                elif any(palabra in ruta for palabra in palabras_suplantacion):
                    st.markdown('<div class="tarjeta-riesgo-alto"><h2>⚠️ POSIBLE CUENTA FALSA / PHISHING</h2><p>El perfil usa palabras típicas de suplantadores para engañarte. ¡No entregues tus datos!</p></div>', unsafe_allow_html=True)
                    registrar_amenaza("Verificación de Red Social", "ALTO RIESGO", "Patrón de suplantación", url)
                else:
                    st.markdown('<div class="tarjeta-riesgo-medio"><h2>ℹ️ PERFIL ESTÁNDAR / NO VERIFICADO</h2><p>Es un enlace de red social normal. No pertenece a un medio oficial reconocido de Colombia. Verifica la fuente con precaución.</p></div>', unsafe_allow_html=True)

            # 3. ¿Es la página web de una Noticia Oficial?
            elif any(medio in dominio for medio in medios_colombia.keys()):
                st.markdown('<div class="tarjeta-seguro"><h2>📰 MEDIO CONFIABLE COLOMBIANO</h2><p>El enlace pertenece a la página web de un medio de comunicación nacional o regional reconocido.</p></div>', unsafe_allow_html=True)
            
            # 4. ¿No tiene seguridad?
            elif url.startswith("http://"):
                st.markdown('<div class="tarjeta-riesgo-alto"><h2>🔴 SITIO INSEGURO</h2><p>Conexión no cifrada (HTTP). Un portal de noticias real jamás usaría esto hoy en día. Tus datos corren peligro.</p></div>', unsafe_allow_html=True)
                registrar_amenaza("Verificación de Enlace", "ALTO RIESGO", "Falta SSL (HTTP)", url)
            
            # 5. Blogs o páginas desconocidas (Posible Fake News)
            else:
                st.markdown('<div class="tarjeta-riesgo-medio"><h2>🟡 FUENTE NO RECONOCIDA</h2><p>Este sitio web no está en nuestra lista de medios oficiales de Colombia. Podría tratarse de desinformación, una cadena falsa o un blog no verificado. Lee con espíritu crítico.</p></div>', unsafe_allow_html=True)
                registrar_amenaza("Verificación de Enlace", "RIESGO MODERADO", "Fuente de noticias no verificada", url)

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
