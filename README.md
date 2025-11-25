# 📘 README.md — ARDY-IA  
### Asistente inteligente con STT, LLM, RAG y TTS en tiempo real

---

## 🐿️ ARDY-IA – Asistente Multimodal Inteligente

Ardy-IA es un asistente conversacional multilingüe, rápido y totalmente local, diseñado para funcionar como tutor idiomático y asistente personal.

Integra:

- 🎙️ **Reconocimiento de voz (STT)** con *Faster-Whisper*
- 🧠 **Modelo LLM Groq (Llama 3.1-8B)** para respuestas ultrarrápidas
- 🔎 **Motor RAG (ChromaDB)** para mejorar respuestas con contexto real
- 🔊 **Síntesis de voz (TTS)** en español, inglés y francés
- 🐿️ **Interfaz web animada protagonizada por Ardy**, la ardilla del proyecto

El objetivo del proyecto es demostrar un asistente IA completo, integrado y listo para producción, capaz de procesar voz, texto, contexto y generar respuesta hablada.

---

# 🏗️ Arquitectura General

Ardy-IA sigue un pipeline completo:

---

## 🎨 **Frontend (HTML/JS con animaciones)**

- UI moderna, responsiva y animada  
- Grabación de voz con MediaRecorder  
- Render de respuesta con voz  
- Animaciones de Ardy (cartoon)  
- Indicadores de salud del sistema  

---

## ⚙️ **FastAPI Backend**

### 🛠️ Manejo general

- Rutas `/chat` y `/voice`
- Middleware de logging
- Control de sesiones por usuario

---

## 🗣️ **STTService → Faster-Whisper**

- Limpieza de audio  
- VAD (detección de silencio)  
- Soporte multilenguaje  
- Validación mínima de tamaño  
- Carga optimizada del modelo  

---

## 🔍 **RAGService → ChromaDB**

- Embeddings  
- Búsqueda semántica  
- Normalización y limpieza de documentos  
- Contexto optimizado por relevancia  

---

## 🧠 **Groq LLM Service**

- Respuestas ultrarrápidas usando Llama 3.1-8B  
- Control de temperatura, longitud y estilo  
- Integración con memoria de sesión  

---

## 🔊 **TTSService**

- Síntesis de voz en español, inglés y francés  
- Formato compatible con navegadores  
- Fallback automático si falla el TTS  

---

# 📂 Estructura del Proyecto

```
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
│   └── language_learning/   ← Base de conocimientos para el RAG
│
├── index.html               ← Interfaz web animada de Ardy
└── .env.example             ← Ejemplo de configuración
```

---

# ⚙️ Instalación

## 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/Sekkon0906/Ardy-IA.git
cd Ardy-IA
```

## 2️⃣ Crear entorno virtual

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3️⃣ Instalar dependencias

```bash
pip install -r backend/requirements.txt
```

⚠️ **IMPORTANTE:**  
❌ Nunca subas `.venv` al repositorio.  
Debe estar en `.gitignore`.

---

# 🧪 Configurar variables de entorno

Crea un archivo `.env` basado en `.env.example`:

```
GROQ_API_KEY=tu_clave_real
WHISPER_MODEL=base
CHROMA_DB_DIR=./chroma
```

---

# ▶️ Ejecución del Backend

```bash
cd backend
uvicorn main:app --reload
```

Servidor disponible en:  
👉 http://127.0.0.1:8000  

Endpoint de prueba:  
👉 http://127.0.0.1:8000/health

---

# 💻 Ejecución del Frontend

No requiere compilación.  
Solo abre:

```
index.html
```

---

# 🎤 Pipeline de Voz Completo

### 🔹 1. Usuario habla  
Frontend graba audio en WAV o WebM.

### 🔹 2. STT → Faster-Whisper  
- Limpieza  
- Detección de silencio (VAD)  
- Decodificación precisa  

### 🔹 3. LLM (Groq)  
Recibe:  
- Transcripción  
- Idioma  
- Contexto del RAG  
- Estado de la sesión  

### 🔹 4. TTS  
Genera audio en el idioma seleccionado.

### 🔹 5. Ardy responde  
Con voz y animaciones.

---

# 📚 RAG – Recuperación de Conocimiento

ChromaDB se usa como base vectorial.

### Proceso:

1. Inserción inicial de documentos  
2. Generación de embeddings (sentence_transformers)  
3. Búsqueda semántica optimizada  
4. Limpieza de duplicados  
5. Recorte por longitud  

Ejemplo real:

```python
results = self.collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    include=["documents", "metadatas", "distances"]
)
```

---

# 🟦 Animaciones y Frontend Moderno

La interfaz incluye:

- 🎨 Animaciones hover  
- 💬 Burbujas animadas  
- 🔊 Botón de reproducción con efecto pulse  
- 🐿️ Ardy animado estilo cartoon  
- 🎤 Botón de grabación con animación  
- 📡 Indicadores de salud del sistema  
- 🌙 Paleta moderna y responsiva  

---

# 🛠️ Solución de Problemas Comunes

### ❌ **No me deja hacer push a GitHub**

➡️ Tienes claves filtradas  
➡️ Debes eliminarlas con `git filter-repo`

---

### ❌ **GitHub rechaza archivos >100 MB**

➡️ No subas `.venv`  
➡️ No subas DLLs  
➡️ Usa `.gitignore`

---

### ❌ **Whisper da error de EOF**

➡️ El audio llega vacío.  
Verifica:

- MediaRecorder  
- Tipo MIME  
- Validación mínima de tamaño

---

### ❌ **TTS no carga**

➡️ Falta instalar el modelo TTS  
➡️ O no existe el directorio configurado  

---

# 👨‍💻 Tecnologías utilizadas

| Tecnología | Uso |
|-----------|-----|
| FastAPI | Backend |
| Groq Llama 3.1-8B | LLM principal |
| Faster-Whisper | STT |
| ChromaDB | Motor RAG |
| Web Speech API | Reproducción de voz |
| HTML/CSS/JS | Interfaz |
| Ardy (cartoon) | Mascota del proyecto |

---

# 📜 Licencia

MIT — Libre para estudio, investigación y desarrollo.

---

# 🐿️ Créditos

Proyecto creado por:  
**Sekkon0906**

