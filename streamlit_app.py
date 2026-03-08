import streamlit as st
import re

st.set_page_config(page_title="SafeShield Colombia", page_icon="🛡️")

st.title("🛡️ SafeShield: Verificador de Mensajes")
st.markdown("Analiza mensajes sospechosos para detectar **manipulación emocional** o enlaces fraudulentos.")

mensaje = st.text_area("Pega aquí el mensaje o correo que recibiste:")

if st.button("Analizar Nivel de Riesgo"):
    if mensaje:
        gatillos = ["urgente", "bloqueo", "embargo", "inmediato", "suspensión", "dian", "clonación", "cuenta suspendida"]
        puntuacion = 0
        palabras_detectadas = []

        for p in gatillos:
            if p in mensaje.lower():
                puntuacion += 25
                palabras_detectadas.append(p)
        
        if puntuacion >= 50:
            st.error(f"⚠️ ALTO RIESGO DETECTADO")
            st.warning(f"Tácticas de presión detectadas: {', '.join(palabras_detectadas)}")
        elif puntuacion > 0:
            st.warning(f"🟡 RIESGO MODERADO")
            st.write(f"Lenguaje sospechoso: {', '.join(palabras_detectadas)}")
        else:
            st.success("✅ No se detectaron patrones comunes de manipulación emocional.")
    else:
        st.write("Por favor, ingresa un texto para analizar.")
