import os
import streamlit as st
import base64
from openai import OpenAI

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Configure the page layout and appearance
st.set_page_config(page_title="Análisis de Imagen 🤖🏞️", layout="centered", initial_sidebar_state="collapsed")

# Title and brief description
st.title("Análisis de Imagen con IA 🤖🏞️")
st.markdown("Sube una imagen y obtén un análisis detallado en español.")

# Input section for OpenAI API key
api_key_input = st.text_input('🔑 Ingresa tu clave de OpenAI API:', type="password")
os.environ['OPENAI_API_KEY'] = api_key_input

# File uploader for the image
uploaded_file = st.file_uploader("📂 Sube una imagen", type=["jpg", "png", "jpeg"])

# Display the uploaded image
if uploaded_file:
    st.image(uploaded_file, caption=f"Imagen seleccionada: {uploaded_file.name}", use_column_width=True)

# Toggle for additional details about the image
show_details = st.checkbox("📝 ¿Deseas agregar detalles sobre la imagen?", value=False)

if show_details:
    additional_details = st.text_area("Añade más contexto sobre la imagen aquí:")

# Button for analyzing the image
st.markdown("---")
analyze_button = st.button("🔍 Analizar Imagen")

# Initialize OpenAI client
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key) if api_key else None

# Analysis logic
if analyze_button:
    if not api_key:
        st.error("🔑 Por favor, ingresa tu clave de API antes de continuar.")
    elif not uploaded_file:
        st.error("📂 Por favor, sube una imagen para analizar.")
    else:
        with st.spinner("Analizando la imagen, por favor espera..."):
            try:
                # Encode the image
                base64_image = encode_image(uploaded_file)

                # Construct the prompt
                prompt_text = "Describe lo que ves en la imagen en español."
                if show_details and additional_details:
                    prompt_text += f"\n\nDetalles adicionales proporcionados por el usuario:\n{additional_details}"

                # Construct the message payload
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"},
                        ],
                    }
                ]

                # Display the response while streaming
                full_response = ""
                message_placeholder = st.empty()
                for completion in client.chat.completions.create(
                    model="gpt-4-vision-preview", messages=messages, max_tokens=1200, stream=True
                ):
                    if completion.choices[0].delta.content is not None:
                        full_response += completion.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")

                # Final display update
                message_placeholder.markdown(full_response)

            except Exception as e:
                st.error(f"❌ Ha ocurrido un error: {e}")
