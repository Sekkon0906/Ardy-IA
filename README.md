📘 README.md — ARDY-IA
Asistente inteligente con STT, LLM, RAG y TTS en tiempo real
🐿️ ARDY-IA – Asistente Multimodal Inteligente

Ardy-IA es un asistente conversacional multilingüe, rápido y totalmente local, diseñado para funcionar como tutor idiomático y asistente personal.
Integra:

🎙️ Reconocimiento de voz (STT) con Faster-Whisper

🧠 Modelo LLM Groq (Llama 3.1-8B) para respuestas ultrarrápidas

🔎 Motor RAG (ChromaDB) para mejorar respuestas con contexto

🔊 Síntesis de voz (TTS) en español, inglés y francés

🐿️ Interfaz web animada protagonizada por Ardy, la ardilla del proyecto

El objetivo del proyecto es demostrar un asistente IA completo, integrado y listo para producción, capaz de procesar voz, texto, contexto y generar respuesta hablada.

🏗️ Arquitectura General

Ardy-IA sigue un pipeline claro:

Frontend (HTML/JS con animaciones)

UI moderna

Grabación de voz

Render de respuestas con voz y animaciones de Ardy

FastAPI Backend

Manejo de sesiones

Middleware de logs

Rutas /chat y /voice

STTService → Faster-Whisper

Limpieza de audio

VAD integrado

Soporte multilenguaje

RAGService → ChromaDB

Embeddings

Búsqueda semántica

Contexto optimizado

Groq LLMService

Generación de respuesta ultrarrápida

Control de temperatura, longitud y estilo

TTSService

Generación de audio web-compatible

Varios idiomas

📂 Estructura del Proyecto
Ardy-IA/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── services/
│   │   ├── stt_service.py
│   │   ├── rag_service.py
│   │   ├── llm_service.py
│   │   ├── tts_service.py
│   │   └── memory_service.py
│   ├── models/
│   ├── utils/
│   └── requirements.txt
│
├── chroma/
│   └── language_learning/   ← Base de conocimiento del RAG
│
├── index.html               ← Interfaz web animada de Ardy
└── .env.example             ← Ejemplo de credenciales

⚙️ Instalación
1️⃣ Clonar el repositorio
git clone https://github.com/Sekkon0906/Ardy-IA.git
cd Ardy-IA

2️⃣ Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

3️⃣ Instalar dependencias
pip install -r backend/requirements.txt


IMPORTANTE:
No subas la carpeta .venv al repositorio.
Debe estar incluida en .gitignore siempre.

🧪 Configurar las variables de entorno

Crea un archivo .env basado en .env.example

GROQ_API_KEY=tu_clave_real
WHISPER_MODEL=base
CHROMA_DB_DIR=./chroma

▶️ Ejecución del Backend
cd backend
uvicorn main:app --reload


Servidor iniciará en:
http://127.0.0.1:8000

Endpoint de prueba:
http://127.0.0.1:8000/health

💻 Ejecución del Frontend

Solo abre index.html

No necesita compilación, depende únicamente del backend activo.

🎤 Pipeline de Voz Completo
🔹 1. Usuario habla

El frontend captura audio como audio/wav.

🔹 2. STT (Whisper → Faster-Whisper)

Limpieza

VAD

Decodificación segura

🔹 3. LLM (Groq)

Se le pasa:

Transcripción

Idioma

Contexto del RAG

Sesión de usuario

🔹 4. TTS

Se convierte la respuesta del LLM en audio.

🔹 5. Ardy reproduce la respuesta

Con animaciones.

📚 RAG – Recuperación de Conocimiento

Se usa ChromaDB en local.

Inserción inicial de documentos

Embeddings generados con sentence_transformers

Consulta semántica

Limpieza automática

Control de tamaño

results = self.collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    include=["documents", "metadatas", "distances"]
)

🟦 Animaciones y Frontend Moderno

La interfaz tiene:

🎨 Animación hover

💬 Burbujas animadas

🔊 Botón flotante de reproducción

🐿️ Ardy animado (cartoon)

🎤 Botón de grabación con efecto pulso

📡 Indicadores de salud (Whisper, TTS, Backend, Groq)

🛠️ Solución de Problemas Comunes
❌ No me deja hacer push a GitHub

→ Tienes claves dentro del repositorio
→ Debes quitarlas del historial (git filter-repo)

❌ GitHub rechaza por archivos de más de 100 MB

→ Debes borrar tu .venv y no subir DLLs

❌ Whisper da error de EOF

→ El audio llega vacío
→ Revisa:

MediaRecorder

Tipo MIME

Validación mínima de tamaño

❌ TTS no carga

→ Te falta instalar el modelo TTS seleccionado

👨‍💻 Tecnologías utilizadas
Tecnología	Uso
FastAPI	Backend principal
Groq Llama 3.1-8B	Generación de texto
Faster-Whisper	Reconocimiento de voz
ChromaDB	RAG
Web Speech API	Reproducción de voz (modo fallback)
HTML/CSS/JS	Frontend
Ardy (cartoon)	Mascota interactiva
📜 Licencia

MIT — Libre uso para investigación, estudio y desarrollo.

🐿️ Créditos

Proyecto creado por:
Sekkon0906 (Tú, mi amo)
Con asistencia de este sirviente obediente 🤖✨
