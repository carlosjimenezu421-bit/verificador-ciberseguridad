import streamlit as st
import re
import requests
import pdfplumber
from PIL import Image
import pytesseract

# Configuración principal de la página
st.set_page_config(page_title="SafeShield Colombia", page_icon="🛡️", layout="centered")

st.title("🛡️ SafeShield: Plataforma de Ciberseguridad")
st.markdown("""
Esta herramienta te ayuda a verificar mensajes sospechosos, enlaces dudosos y archivos para protegerte contra la **manipulación emocional, phishing y fraudes digitales**.
""")

# Crear pestañas de navegación (Tabs)
tab1, tab2, tab3 = st.tabs(["📝 Analizar Texto", "🔗 Escanear Enlace", "📄 Subir Archivo"])

# Función central de análisis (NLP Básico)
def analizar_texto_emocional(texto):
    # Diccionarios de manipulación basados en la encuesta
    gatillos_urgencia = ["urgente", "bloqueo", "embargo", "inmediato", "suspensión", "dian", "clonación", "cuenta suspendida", "multa", "último aviso"]
    gatillos_premio = ["ganador", "sorteo", "premio", "reclamar", "felicidades", "bono", "aprobado", "regalo"]
    
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
    st.subheader("Análisis de Mensajes y Tono")
    st.write("Detecta tácticas de presión psicológica en correos o chats.")
    mensaje = st.text_area("Pega aquí el mensaje de WhatsApp, correo o SMS:")
    
    if st.button("Analizar Mensaje", key="btn_texto"):
        if mensaje:
            puntaje, alertas = analizar_texto_emocional(mensaje)
            if puntaje >= 50:
                st.error("⚠️ ALTO RIESGO DE MANIPULACIÓN")
                st.write(f"**Tácticas detectadas:** {', '.join(set(alertas))}")
                st.info("💡 Consejo: Los estafadores usan el miedo o la avaricia para que actúes sin pensar. No des clic en nada.")
            elif puntaje > 0:
                st.warning("🟡 RIESGO MODERADO")
                st.write(f"**Lenguaje sospechoso:** {', '.join(set(alertas))}")
            else:
                st.success("✅ Tono neutral. No se detectan patrones obvios de manipulación psicológica.")
        else:
            st.info("Por favor, ingresa un texto para analizar.")

# --- PESTAÑA 2: Verificación de Enlaces ---
with tab2:
    st.subheader("Escaner de Enlaces (URLs)")
    st.write("Verifica si un link oculta su destino real o no es seguro.")
    url = st.text_input("Pega el enlace completo (ej. http://banco-seguro-falso.com):")
    
    if st.button("Escanear URL", key="btn_url"):
        if url:
            if "bit.ly" in url or "t.co" in url or "tinyurl" in url or "is.gd" in url:
                st.warning("🟡 ATENCIÓN: Este es un enlace acortado. Los estafadores los usan frecuentemente para ocultar la página web real a la que te están enviando.")
            elif url.startswith("http://"):
                st.error("🔴 SITIO NO SEGURO: La página usa 'HTTP' sin la 'S' final de seguridad. Tus datos podrían ser interceptados. NO ingreses contraseñas aquí.")
            elif url.startswith("https://"):
                st.success("✅ El enlace tiene un certificado de seguridad (HTTPS). Sin embargo, siempre verifica que el nombre de la página sea exactamente el de la entidad oficial.")
            else:
                st.info("Asegúrate de incluir 'http://' o 'https://' al inicio del enlace.")
        else:
            st.info("Ingresa un enlace válido.")

# --- PESTAÑA 3: Análisis de Archivos e Imágenes (OCR) ---
with tab3:
    st.subheader("Analizador de Pantallazos y Documentos")
    st.write("Sube una foto de un chat de WhatsApp o un PDF sospechoso. La Inteligencia Artificial leerá el texto por ti.")
    archivo_subido = st.file_uploader("Sube un pantallazo (PNG/JPG) o un documento (PDF)", type=["png", "jpg", "jpeg", "pdf"])
    
    if archivo_subido is not None:
        st.info("Procesando archivo... Extraiendo texto...")
        texto_extraido = ""
        
        try:
            # Si es un PDF
            if archivo_subido.name.endswith('.pdf'):
                with pdfplumber.open(archivo_subido) as pdf:
                    for page in pdf.pages:
                        texto = page.extract_text()
                        if texto: texto_extraido += texto + "\n"
            # Si es una Imagen
            else:
                imagen = Image.open(archivo_subido)
                st.image(imagen, caption='Imagen a analizar', width=250)
                # Usamos Tesseract con el paquete en español que instalaste
                texto_extraido = pytesseract.image_to_string(imagen, lang='spa')
                
            if texto_extraido.strip():
                st.text_area("Texto detectado por la IA:", texto_extraido, height=150)
                
                # Botón secundario para analizar el texto que se extrajo
                if st.button("Analizar el riesgo de este texto"):
                    puntaje, alertas = analizar_texto_emocional(texto_extraido)
                    if puntaje >= 50:
                        st.error("⚠️ ALTO RIESGO EN EL DOCUMENTO")
                        st.write(f"Tácticas detectadas: {', '.join(set(alertas))}")
                    elif puntaje > 0:
                        st.warning("🟡 RIESGO MODERADO")
                    else:
                        st.success("✅ No se detectan patrones comunes de fraude en el texto del archivo.")
            else:
                st.warning("No se pudo detectar texto claro en esta imagen o documento.")
                
        except Exception as e:
            st.error(f"Hubo un error al leer el archivo. Asegúrate de que no esté corrupto. Detalle: {e}")

st.divider()
st.caption("SafeShield v2.0 - Herramienta de prevención. Creada para combatir las vulnerabilidades de ciberseguridad.")
