
from flask import Flask, render_template_string, request, send_file
from gtts import gTTS   
from newspaper import Article
from pydub import AudioSegment
from pathlib import Path
import re


app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Convierte cualquier texto a MP3</title>

  <!-- Tipografías -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Poppins:wght@700&display=swap" rel="stylesheet">

  <style>
    :root{
      --bg:#0b0b10;
      --muted:#a4a4b5;
      --text:#f2f2f7;
      --primary:#8b5cf6;
      --primary-600:#7c3aed;
      --ring: rgba(139,92,246,.45);
      --fade: 0; /* 0 → hero visible, 1 → hero oculto */
    }
    *{ box-sizing:border-box }
    html,body{ height:100% }
    body{
      margin:0;
      background:
        radial-gradient(1200px 600px at 10% -10%, rgba(139,92,246,.25), transparent 60%),
        radial-gradient(1200px 600px at 110% 110%, rgba(139,92,246,.2), transparent 60%),
        var(--bg);
      color:var(--text);
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
      line-height:1.5;
    }

    .page{ min-height:100svh; }

    /* HERO: ocupa la pantalla y luego se colapsa */
    .hero{
      position:relative;
      height: calc(100svh * (1 - var(--fade)));
      min-height: 0;         /* permite colapsar de verdad */
      overflow: hidden;      /* que no asome nada al colapsar */
      display:grid;
      place-items:center;
      padding: clamp(24px, 4vw, 48px);
    }
    .hero .content{
      text-align:center;
      max-width: 900px;
      opacity: calc(1 - var(--fade));
      transform: translateY(calc(var(--fade) * -16px)) scale(calc(1 - var(--fade) * .04));
      transition: opacity .25s ease, transform .25s ease;
    }
    .brand{
      display:inline-flex; align-items:center; gap:10px;
      color:#c4b5fd; font-weight:600; letter-spacing:.3px;
      background:rgba(139,92,246,.08); border:1px solid rgba(139,92,246,.25);
      padding:6px 10px; border-radius:999px; margin-bottom:14px;
    }
    .title{
      font-family:Poppins, Inter, sans-serif;
      font-weight:700;
      font-size: clamp(28px, 6vw, 56px);
      line-height:1.1;
      margin: 0 0 10px;
      text-wrap: balance;
    }
    .subtitle{
      color:var(--muted);
      font-size: clamp(14px, 2.4vw, 18px);
      margin: 0 auto;
      max-width: 760px;
      text-wrap: pretty;
    }

    /* FORM: sticky + centrado absoluto en viewport cuando aparece */
    .form-wrap{
      position: sticky;
      top: 0;                 /* se queda pegada al top */
      min-height: 100svh;     /* ocupa la altura de la ventana */
      display:grid;
      place-items:center;     /* centra la tarjeta */
      padding: clamp(16px, 4vw, 40px) 20px 64px;
    }
    .card{
      width:min(760px, 92vw);
      background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
      border:1px solid rgba(255,255,255,.08);
      border-radius: 20px;
      box-shadow: 0 10px 30px rgba(0,0,0,.35);
      padding: clamp(18px, 3.5vw, 28px);
      transform: translateY(calc((1 - var(--fade)) * 10px)); /* ligera subida */
      transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
    }
    .card:hover{ box-shadow: 0 14px 40px rgba(0,0,0,.45); border-color: rgba(255,255,255,.12); }

    form{ display:grid; gap:16px; width:100%; }
    label{ font-weight:600; font-size:.95rem; display:block; margin-bottom:6px; }
    .input, select{
      width:100%;
      background:#0f0f17;
      color:var(--text);
      border:1px solid rgba(255,255,255,.12);
      border-radius:12px;
      padding:12px 14px;
      outline:none;
      transition:.2s border, .2s box-shadow;
    }
    .input::placeholder{ color:#9aa0a6 }
    .input:focus, select:focus{
      border-color:var(--primary);
      box-shadow:0 0 0 4px var(--ring);
    }
    .row{
      display:grid;
      grid-template-columns: 1fr 170px;
      gap:12px;
    }
    button{
      margin-top: 24px;
      background: linear-gradient(135deg, var(--primary), var(--primary-600));
      color:white;
      border:none;
      padding:13px 16px;
      border-radius:12px;
      font-weight:700;
      letter-spacing:.2px;
      cursor:pointer;
      transition: transform .06s ease, box-shadow .2s ease, filter .2s ease;
      box-shadow:0 8px 22px rgba(139,92,246,.35);
      width:100%;
      height:100%;
    }
    button:hover{ filter:brightness(1.05) }
    button:active{ transform: translateY(1px) }

    .hint{ color:var(--muted); font-size:.9rem; margin-top:4px; }
    .alert{
      margin-top:12px; padding:10px 12px; border-radius:10px;
      background: rgba(220, 38, 38, .12); border:1px solid rgba(220, 38, 38, .3); color:#fecaca;
    }
    .footer{ color:var(--muted); font-size:.85rem; text-align:center; padding: 36px 16px 28px; }

    @media (prefers-reduced-motion: reduce){
      .hero .content, .card { transition:none }
    }
  </style>
</head>
<body>
  <main class="page">
    <!-- HERO -->
    <section class="hero" aria-labelledby="t">
      <div class="content">
        <div class="brand">🎧 Texto → Voz</div>
        <h1 id="t" class="title">Convierte cualquier texto a MP3</h1>
        <p class="subtitle">
          Pega la URL de un artículo, elige el idioma y <strong>crea</strong> tu audio en segundos.
          La interfaz te guía paso a paso, sin distracciones.
        </p>
      </div>
    </section>

    <!-- FORMULARIO -->
    <section class="form-wrap" aria-label="Crear MP3">
      <div class="card">
        <form method="post"
          onsubmit="this.querySelector('button').disabled=true; this.querySelector('button').textContent='Creando…';">
          <div>
            <label for="url">URL del artículo</label>
            <input id="url" name="url" class="input" type="url" placeholder="https://..." required>
            <div class="hint">Sugerencia: prueba con un texto corto en inglés (p. ej. example.com).</div>
          </div>

          <div class="row">
            <div>
              <label for="lang">Idioma de la voz</label>
              <select id="lang" name="lang" class="input">
                <option value="es" selected>Español (es)</option>
                <option value="en">English (en)</option>
                <option value="pt">Português (pt)</option>
                <option value="fr">Français (fr)</option>
              </select>
            </div>
            <div style="align-self:end">
              <button type="submit">Crear MP3</button>
            </div>
          </div>

          {% if error %}
            <div class="alert">⚠️ {{ error }}</div>
          {% endif %}
        </form>
      </div>
    </section>

    <p class="footer">gTTS + newspaper3k • diseño pensado para el usuario</p>
  </main>

  <!-- Script: calcula cuánto colapsa/desvanece el hero -->
  <script>
    (function(){
      function onScroll(){
        const h = Math.max(1, window.innerHeight);
        const y = Math.min(h, window.scrollY);
        const fade = Math.max(0, Math.min(1, y / h));
        document.documentElement.style.setProperty('--fade', fade.toFixed(3));
      }
      window.addEventListener('scroll', onScroll, {passive:true});
      window.addEventListener('resize', onScroll);
      onScroll();
    })();
  </script>
</body>
</html>
"""



@app.route("/", methods=["GET", "POST"])

def index():
    if request.method == "GET":
        return render_template_string(HTML)
    
    # 1. Recoger datos del formulario
    url = request.form.get("url")
    lang = request.form.get("lang", "es")
        

    try:
        #2. Extraer el texto
        titulo, texto = extraer_texto(url, language=lang)
        # 3. Trocear (Para articulos muy largos)
        chunks = trocear_texto(texto, 3000)

        # Nombre final basado en titulo
        nombre_final = slugify(titulo) + ".mp3"

        # 4.Generar MP3 por partes
        rutas = []
        for i, ch in enumerate(chunks, 1): 
            nombre = f"{i:03d}.mp3"
            ruta = texto_a_voz(ch, nombre, lang)
            rutas.append(ruta)

        # 5. Unir las partes en un solo MP3
        final = unir_mp3_pydub(rutas, nombre_final)

        #6. Enviar el archivo al usuario
        return send_file(final, mimetype="audio/mpeg", as_attachment=True, download_name=nombre_final)
    except Exception as e:
        return render_template_string(HTML, error=str(e))


def extraer_texto(url: str, language: str = "es") -> tuple[str, str]:
    
    a = Article(url, language=language)
    a.download()
    a.parse()
    texto = " ".join(a.text.split())
    if not texto:
        raise ValueError("No se pudo extraer texto del artículo. Verifique la URL y el idioma.")
    return a.title, texto 

def trocear_texto(texto: str, max_length: int = 3000) -> list[str]:
    # Dividir el texto en fragmentos más pequeños si es necesario
    if len(texto) <= max_length:
        return [texto]
    
    frases = re.split(r"(?<=[.!?])\s+", texto)
    trozos = []
    trozo_actual = ""
    
    for frase in frases:
        if len(trozo_actual) + len(frase) + 1 <= max_length:
            trozo_actual += (" " if trozo_actual else "") + frase
        else:
            if trozo_actual:
                trozos.append(trozo_actual)
            trozo_actual = frase
    
    if trozo_actual:
        trozos.append(trozo_actual)
    
    return trozos

def texto_a_voz(texto: str, out: str = "salida.mp3", language: str = "es") -> str:
    # 0. Crear el objeto gTTS
    if not texto:
        raise ValueError("Texto vacío: no hay nada que convertir a voz.")
    
    tts = gTTS(text=texto, lang=language)  # "es", "en", "pt", etc.
    tts.save(out)
    return out


def unir_mp3_pydub(partes: list[str], salida: str = "articulo.mp3") -> str:
    
    # 3. Unir los archivos MP3 en uno solo
    if not partes:
        raise ValueError("Lista de partes vacía: no hay archivos para unir.")
    audio = AudioSegment.empty()
    for parte in partes:
        audio += AudioSegment.from_mp3(parte)
    audio.export(salida, format="mp3")
    return salida

def slugify(s: str) -> str:
    # Elimina caracteres que no son letras/numeros/espacios/guiones
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    # Reemplaza espacios y guiones múltiples por un solo guion
    s = re.sub(r"[-\s]+", "-", s.strip())
    return s.lower()

# Ejemplo de uso 
if __name__ == "__main__":
       app.run(debug=True)
    