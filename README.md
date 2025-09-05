# 🎧 TTS URL → MP3

Convierte cualquier artículo en **audio MP3** a partir de su URL.  
Solo pega un enlace, elige el idioma y descarga el resultado en segundos.  

👉 **Demo online (gratis, Hugging Face Spaces):**  
[https://huggingface.co/spaces/OussamaSA/tts-url-to-mp3](https://huggingface.co/spaces/OussamaSA/tts-url-to-mp3)

---

## 🚀 Características

- 📑 Extrae texto de artículos con [newspaper3k](https://pypi.org/project/newspaper3k/)  
- 🔊 Convierte texto a voz con [gTTS](https://pypi.org/project/gTTS/)  
- 🎶 Une fragmentos largos en un solo MP3 con [pydub](https://pypi.org/project/pydub/) + `ffmpeg`  
- 🌍 Interfaz web simple con [Flask](https://flask.palletsprojects.com/)  
- ☁️ Desplegado en [Hugging Face Spaces](https://huggingface.co/spaces) con **Docker**

---

## 📷 Captura de pantalla

*(ejemplo, puedes añadir aquí una imagen de tu app ejecutándose en Spaces)*  

![Demo Screenshot](screenshot.png)

---

## 🛠 Instalación local

## 📷 Capturas de pantalla

### Hero section
![Hero Screenshot](assets/screenshot-hero.png)

### Formulario de conversión
![Form Screenshot](assets/screenshot-form.png)
Requisitos:
- Python 3.11+
- `ffmpeg` instalado en tu sistema (`sudo apt install ffmpeg` en Linux)

Clona el repo e instala dependencias:
```bash
git clone https://github.com/Oussama-Samni/tts-url-to-mp3.git
cd tts-url-to-mp3
pip install -r requirements.txt
