# Personal AI Agent - Agente Conversacional Inteligente

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)
![Tests](https://img.shields.io/badge/tests-178%20passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-success.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Descripción del Proyecto

**Personal AI Agent** es un sistema de agente conversacional inteligente desarrollado en Python que combina capacidades avanzadas de procesamiento de lenguaje natural, recuperación aumentada por generación (RAG) y gestión conversacional multi-turno. El sistema está diseñado para mantener conversaciones contextuales, extraer información estructurada de manera progresiva y proporcionar respuestas informadas basadas en una base de conocimiento.

### Características Principales

- 🤖 **Conversación Multi-turno**: Mantiene contexto completo de la conversación por sesión
- 📊 **Extracción Estructurada**: Recopila y valida datos (order_id, category, description, urgency)
- 🔍 **RAG con FAISS**: Sistema de recuperación de información con vectores
- 🌍 **Multilenguaje**: Soporte para español e inglés con detección automática
- 😊 **Análisis de Sentimiento**: Adapta el tono según las emociones del usuario
- 📝 **Resúmenes Automáticos**: Genera resúmenes cuando se completa la información
- 💾 **Persistencia JSON**: Almacenamiento completo de conversaciones
- 🎤 **STT/TTS**: Interfaces para reconocimiento y síntesis de voz
- 🔒 **Seguridad**: Autenticación mediante API keys, validación robusta
- ✅ **Suite de Tests Completa**: 178 tests unitarios y de integración (100% passing)

---

## 🚀 Instrucciones de Setup

### Prerrequisitos

- **Python 3.11 o superior**
- **pip** (gestor de paquetes de Python)
- **Cuenta de OpenAI** (o proveedor alternativo de LLM)
- **8 GB RAM** recomendados
- **Linux/macOS/Windows** con terminal

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd personal-ai-agent-api
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate

# En Windows:
# venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
# Instalar todas las dependencias
pip install -r src/requirements.txt

# Si usas el archivo congelado (versiones exactas):
# pip install -r requirements_freeze.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la carpeta `src/`:

```bash
cd src
touch .env
```

Contenido mínimo del archivo `.env`:

```bash
# Configuración de la aplicación
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

# Proveedor de LLM (openai, anthropic, local)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# API Keys (¡IMPORTANTE! Añade tu clave)
OPENAI_API_KEY=sk-tu-api-key-aqui
# ANTHROPIC_API_KEY=sk-ant-tu-clave  # Si usas Anthropic

# Embeddings
EMBEDDINGS_PROVIDER=openai
EMBEDDINGS_MODEL=text-embedding-3-large

# Base de Conocimiento
KB_PATH=../kb

# Vector Store
VECTORSTORE_PATH=./data/vectorstore
VECTORSTORE_INDEX_NAME=faiss_index

# RAG Configuration
RAG_TOP_K=5
RAG_SCORE_THRESHOLD=0.7
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Conversaciones
MAX_CONVERSATION_TURNS=50
CONVERSATION_STORAGE_PATH=./data/conversations

# Seguridad
API_KEY_ADMIN=cambia-esta-clave-en-produccion

# Idiomas
DEFAULT_LANGUAGE=es
SUPPORTED_LANGUAGES=es,en

# TTS/STT
TTS_ENABLED=false
TTS_PROVIDER=gtts
STT_ENABLED=false
STT_PROVIDER=none
```

### 5. Ingestar la Base de Conocimiento

Antes de iniciar las conversaciones, es recomendable crear el índice vectorial. Se puede hacer mediante su endpoint.

### 6. Iniciar el Servidor

```bash
# Iniciar servidor FastAPI
python MAIN.py
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **Documentación interactiva**: http://localhost:8000/
- **ReDoc**: http://localhost:8000/redoc

### 7. Verificar Instalación

```bash
# En otra terminal, verificar health check
curl http://localhost:8000/api/v1/health

# Respuesta esperada:
# {"status":"ok","version":"1.0.0"}
```

---

## 🏗️ Arquitectura del Sistema

### Visión General

El sistema está organizado en capas bien definidas que separan responsabilidades:

```
┌─────────────────────────────────────────────────────────┐
│                   Usuario / Cliente                      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP REST API
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Server Layer                        │
│  • Routing (chat, admin, health)                        │
│  • Validación (Pydantic)                                │
│  • Autenticación (API Keys)                             │
│  • CORS & Middleware                                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│          Conversation Service (Orquestador)              │
│  • Gestión de flujo conversacional                      │
│  • Coordinación de servicios                            │
│  • Detección de idioma                                  │
│  • Análisis de sentimiento                              │
└───┬────────┬────────┬────────┬────────┬────────┬────────┘
    │        │        │        │        │        │
    │        │        │        │        │        │
┌───▼───┐ ┌─▼──┐ ┌───▼───┐ ┌──▼──┐ ┌──▼───┐ ┌──▼────┐
│Memory │ │RAG │ │Extract│ │Sum. │ │Store │ │STT/TTS│
│Manager│ │Svc │ │Service│ │Svc  │ │Svc   │ │Svc    │
└───┬───┘ └─┬──┘ └───┬───┘ └──┬──┘ └──┬───┘ └───────┘
    │       │        │        │       │
┌───▼───────▼────────▼────────▼───────▼──────────────────┐
│              LangChain Layer                             │
│  • LLM Chains (extraction, response, summary)           │
│  • ConversationBufferMemory                             │
│  • Retrieval Chain                                      │
│  • Prompt Templates (ES/EN)                             │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼───┐   ┌───▼────┐  ┌───▼────┐
    │ LLM   │   │ FAISS  │  │ JSON   │
    │OpenAI │   │Vector  │  │Storage │
    │/Claude│   │Store   │  │        │
    └───────┘   └────────┘  └────────┘
```

### Componentes Principales

#### 1. **FastAPI Server** (`src/server/`)
- Expone endpoints REST para chat, administración y health checks
- Maneja autenticación mediante API keys
- Validación automática con Pydantic
- Documentación OpenAPI generada automáticamente

#### 2. **Conversation Service** (`src/services/conversation.py`)
Orquestador central que coordina:
- Detección de idioma
- Análisis de sentimiento
- Gestión de memoria conversacional
- Extracción de datos estructurados
- Consulta a la base de conocimiento (RAG)
- Generación de respuestas
- Creación de resúmenes
- Persistencia de datos

#### 3. **Memory Manager** (`src/llm/memory.py`)
- Implementa `ConversationBufferMemory` de LangChain
- Mantiene historial por `session_id`
- Límite configurable de turnos (default: 50)
- Almacenamiento en memoria RAM

#### 4. **Extraction Service** (`src/services/extraction.py`)
- Extracción mediante LLM con prompts estructurados
- Validación robusta de campos:
  - `order_id`: Formato alfanumérico 6-12 caracteres
  - `category`: Enum (shipping, billing, technical, other)
  - `description`: Texto con longitud mínima
  - `urgency`: Enum (low, medium, high)
- Acumulación incremental de datos por sesión

#### 5. **RAG System** (`src/rag/`)
- **Ingesta**: Carga documentos Markdown → Chunking → Embeddings → FAISS Index
- **Retrieval**: Búsqueda por similitud vectorial
- **Store**: Persistencia del índice en disco

#### 6. **Storage Service** (`src/services/storage.py`)
- Persistencia en archivos JSON
- Un archivo por sesión: `data/conversations/{session_id}.json`
- Estructura: metadata, turnos, datos extraídos, resumen

#### 7. **Sentiment Analysis** (`src/core/sentiment.py`)
- Análisis con TextBlob
- Clasificación: negative/neutral/positive
- Ajusta tono de respuestas según sentimiento

---

## 🎯 Decisiones de Diseño Clave

### 1. **¿Por qué LangChain?**

**Ventajas:**
- **Abstracciones robustas**: Simplifica integración con LLMs, gestión de memoria y RAG
- **Multi-provider**: Fácil cambio entre OpenAI, Anthropic, modelos locales
- **Chains composables**: Permite construir pipelines complejos de forma modular
- **Comunidad activa**: Gran ecosistema y documentación

**Trade-offs:**
- Overhead de abstracción (más capas de indirección)
- Curva de aprendizaje inicial

**Conclusión**: Los beneficios superan los costos, especialmente la flexibilidad multi-provider y la velocidad de desarrollo.

### 2. **¿Por qué FAISS para Vector Store?**

**Alternativas consideradas**: Pinecone, Weaviate, Chroma, Qdrant

**Razones para FAISS:**
- **Local-first**: No dependencias de servicios cloud externos
- **Alto rendimiento**: Optimizado para CPU, búsquedas rápidas
- **Gratuito**: Sin costos de API
- **Simplicidad**: Persistencia directa a disco
- **Portabilidad**: Índices fáciles de distribuir

**Limitaciones:**
- Sin filtrado complejo por metadata
- Escalabilidad limitada vs. soluciones cloud
- No distribuido nativamente

**Conclusión**: Ideal para volúmenes pequeños/medios y deployments que priorizan control y costos.

### 3. **¿Por qué Almacenamiento JSON?**

**Alternativas**: PostgreSQL, MongoDB, SQLite

**Razones:**
- **Simplicidad**: No requiere instalación de DB
- **Portabilidad**: Archivos planos transportables
- **Inspección manual**: Fácil debug y auditoría
- **Suficiente para el scope**: Adecuado para <10,000 sesiones

**Limitaciones:**
- Consultas complejas difíciles
- Concurrencia limitada
- Escalabilidad horizontal complicada

**Migración futura**: Considerar PostgreSQL cuando el volumen supere 10K sesiones o se necesiten búsquedas complejas.

### 4. **Extracción Incremental vs. Todo de Una Vez**

**Decisión**: Extracción incremental acumulativa

**Razones:**
- Usuario puede no saber toda la información al inicio
- Experiencia conversacional más natural
- Permite validación progresiva
- Reduce frustración del usuario

**Implementación**: Cache de `ExtractedData` en memoria por sesión, merge en cada turno.

### 5. **Análisis de Sentimiento**

**Decisión**: TextBlob (simple) en lugar de modelos complejos

**Razones:**
- Suficiente para ajustes básicos de tono
- Ligero y rápido
- Sin dependencias de modelos pesados

**Mejora futura**: Fine-tuning de modelo específico del dominio si se requiere mayor precisión.

### 6. **Arquitectura de Capas**

**Patrón**: Separación estricta de responsabilidades

```
Routes → Services → LLM/RAG → Data Layer
```

**Ventajas:**
- Código testeable (fácil mock de dependencias)
- Mantenibilidad (cambios localizados)
- Reutilización (servicios compartidos)
- Claridad (responsabilidades bien definidas)

### 7. **Configuración con Pydantic Settings**

**Decisión**: `.env` + Pydantic en lugar de hardcoding

**Ventajas:**
- Type-safe configuration
- Validación automática en startup
- Documentación viva
- Fácil override por ambiente (dev/prod)

---

## 🔧 Mejoras Potenciales

### Corto Plazo (1-3 meses)

#### 1. **Cache de Embeddings**
**Problema**: Embeddings se recalculan para queries frecuentes
**Solución**: Redis cache con TTL
**Impacto**: Reducción de 50-80% en latencia para FAQs comunes

```python
# Implementación sugerida
from functools import lru_cache
from redis import Redis

cache = Redis(host='localhost', port=6379)

def get_embedding_cached(text: str) -> List[float]:
    key = f"emb:{hash(text)}"
    cached = cache.get(key)
    if cached:
        return json.loads(cached)
    
    embedding = embeddings_model.embed_query(text)
    cache.setex(key, 3600, json.dumps(embedding))  # TTL 1h
    return embedding
```

#### 2. **Retry Logic con Exponential Backoff**
**Problema**: Llamadas a LLM fallan ocasionalmente (rate limits, timeouts)
**Solución**: Decorador retry con backoff exponencial

```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3)
)
def call_llm(prompt: str) -> str:
    return llm.invoke(prompt)
```

#### 3. **Rate Limiting por Usuario/Sesión**
**Problema**: Abuso potencial del API
**Solución**: Middleware con `slowapi`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: ChatRequest):
    ...
```

#### 4. **Webhooks para Sesiones Completadas**
**Problema**: Cliente debe polling para saber si hay resumen
**Solución**: Webhook configurable cuando `summary_ready=true`

```python
# En conversation.py, cuando summary_ready:
if settings.webhook_url:
    requests.post(
        settings.webhook_url,
        json={
            "session_id": session_id,
            "summary": summary,
            "extracted": extraction_result.extracted.dict()
        }
    )
```

### Medio Plazo (3-6 meses)

#### 5. **Migración a Memoria Distribuida (Redis)**
**Problema**: Memoria conversacional se pierde en restart
**Solución**: Redis como backend para memoria

```python
from langchain.memory import RedisChatMessageHistory

def get_memory(session_id: str):
    message_history = RedisChatMessageHistory(
        session_id=session_id,
        url="redis://localhost:6379"
    )
    return ConversationBufferMemory(chat_memory=message_history)
```

**Beneficios**:
- Persistencia entre deployments
- Compartida entre instancias (horizontal scaling)
- TTL automático para limpiar sesiones viejas

#### 6. **Structured Outputs (GPT-4)**
**Problema**: Parsing JSON a veces falla con prompts
**Solución**: Usar `response_format` de OpenAI

```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[...],
    response_format={"type": "json_object"},
    tools=[{
        "type": "function",
        "function": {
            "name": "extract_data",
            "parameters": ExtractedData.schema()
        }
    }]
)
```

**Beneficios**: Mayor fiabilidad en extracción, menos parseo manual

#### 7. **Frontend Web (React/Vue)**
**Componentes**:
- Chat interface con historial
- Indicador de campos extraídos en tiempo real
- Visualización de sentimiento
- Export de resúmenes
- Ya desarrollado la primera prueba en https://github.com/Chispasgg/personal-ai-agent-front

**Tech Stack sugerido**:
- React + TypeScript
- TailwindCSS
- Zustand para estado
- React Query para API calls

#### 8. **A/B Testing de Prompts**
**Problema**: No sabemos qué prompts funcionan mejor
**Solución**: Framework de experimentación

```python
class PromptExperiment:
    def __init__(self, variants: Dict[str, str]):
        self.variants = variants
        self.metrics = defaultdict(list)
    
    def get_prompt(self, session_id: str) -> str:
        variant = hash(session_id) % len(self.variants)
        return list(self.variants.values())[variant]
    
    def track_result(self, variant: str, is_complete: bool, turns: int):
        self.metrics[variant].append({"complete": is_complete, "turns": turns})
```

### Largo Plazo (6+ meses)

#### 9. **Integración con CRM**
**Sistemas**: Salesforce, HubSpot, Zendesk

**Flujo**:
```
Sesión completa → Webhook → CRM API
                  ↓
            Crear ticket con:
            - Datos extraídos
            - Resumen
            - Transcripción
            - Sentimiento
```

#### 10. **Fine-tuning de Modelo de Extracción**
**Proceso**:
1. Recopilar 500-1000 ejemplos etiquetados
2. Fine-tune `gpt-x` o `llama-X`
3. Evaluación en conjunto de test
4. Deploy como modelo dedicado

**Beneficios**: Costos reducidos, mayor precisión, menor latencia

#### 11. **Multi-tenant Architecture**
**Requisitos**:
- Aislamiento de datos por tenant
- Personalización de prompts por tenant
- Límites de uso por tenant
- Base de conocimiento separada

**Esquema DB**:
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR,
    api_key VARCHAR,
    config JSONB
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants,
    session_id VARCHAR,
    data JSONB,
    created_at TIMESTAMP
);
```

#### 12. **Observabilidad Avanzada**
**Stack**:
- **Logs**: ELK (Elasticsearch, Logstash, Kibana)
- **Métricas**: Prometheus + Grafana
- **Tracing**: OpenTelemetry + Jaeger
- **Alerting**: PagerDuty

**Dashboards clave**:
- Latencia P50/P95/P99 por endpoint
- Tasa de completitud de sesiones
- Distribución de sentimiento
- Costo por sesión (tokens consumidos)
- Errores de extracción

#### 13. **STT/TTS Real**
**Problema**: Actual es solo stub/gTTS básico

**Soluciones**:
- **STT**: Whisper API (OpenAI) o Deepgram
- **TTS**: ElevenLabs, Azure Speech, o Coqui TTS

**Implementación**:
```python
# STT con Whisper
import openai

def speech_to_text(audio_file: bytes) -> str:
    response = openai.Audio.transcribe("whisper-1", audio_file)
    return response["text"]

# TTS con ElevenLabs
from elevenlabs import generate, play

def text_to_speech(text: str, voice="Bella") -> bytes:
    audio = generate(text=text, voice=voice)
    return audio
```

#### 14. **Analytics y Business Intelligence**
**Features**:
- Dashboard de métricas de negocio
- Análisis de tendencias (categorías más frecuentes)
- Detección de problemas recurrentes
- Time-to-resolution por categoría
- NPS basado en sentimiento

**Herramientas**: Metabase, Superset, o custom dashboard

---

## 📚 API Reference

### Endpoints Principales

#### `POST /api/v1/chat`
Procesa un mensaje del usuario y retorna respuesta con datos extraídos.

**Request:**
```json
{
  "session_id": "session-abc-123",
  "message": "Hola, mi pedido ABC123456 no llegó",
  "language": "es",  // opcional, se detecta automáticamente
  "audio_response": false  // opcional, para recibir respuesta en audio
}
```

**Response:**
```json
{
  "reply": "Entiendo tu preocupación. ¿Podrías indicarme la categoría?",
  "sound_file_base64": null,
  "language": "es",
  "sentiment": "negative",
  "extracted": {
    "order_id": "ABC123456",
    "category": null,
    "description": "Pedido no llegó",
    "urgency": null
  },
  "missing_fields": ["category", "urgency"],
  "summary_ready": false,
  "summary": null,
  "session_id": "session-abc-123",
  "turn_number": 2
}
```

#### `GET /api/v1/health`
Health check del servicio.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

#### `POST /api/v1/admin/ingest` 🔒
Reingesta la base de conocimiento (requiere API key).

**Headers:**
```
X-API-Key: tu-api-key-admin
```

**Request:**
```json
{
  "kb_path": "../kb"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Knowledge base ingested successfully",
  "documents_count": 2,
  "chunks_count": 47
}
```

### Autenticación

Los endpoints administrativos requieren autenticación mediante API key:

```bash
curl -X POST http://localhost:8000/api/v1/admin/ingest \
  -H "X-API-Key: tu-api-key-admin" \
  -H "Content-Type: application/json" \
  -d '{"kb_path": "../kb"}'
```

---

<!-- ## 🐳 Docker

### Construcción y Ejecución

```bash
# Construir imagen
cd docker
docker build -t personal-ai-agent:latest -f Dockerfile ../src

# Ejecutar contenedor
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/src/data \
  -e OPENAI_API_KEY=tu-key \
  --name ai-agent \
  personal-ai-agent:latest

# Ver logs
docker logs -f ai-agent
```

### Docker Compose

Edita `docker/docker-compose.yml` con tu configuración:

```yaml
version: '3.8'

services:
  api:
    build:
      context: ../src
      dockerfile: ../docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - API_KEY_ADMIN=${API_KEY_ADMIN}
      - APP_ENV=prod
    volumes:
      - ./data:/src/data
      - ./kb:/kb
    restart: unless-stopped
```

Ejecutar:

```bash
docker-compose -f docker/docker-compose.yml up -d
``` -->

---

## 🧪 Testing

### ✅ Suite de Tests Completa

El proyecto cuenta con una **suite completa de 178 tests unitarios y de integración** que cubren todos los módulos del sistema con un **100% de tasa de éxito**.

#### Estadísticas de Tests

- **Total de tests**: 178 ✅
- **Tests pasando**: 178 (100%)
- **Tiempo de ejecución**: ~1.45 segundos
- **Cobertura**: Todos los módulos cubiertos

#### Distribución por Módulos

| Módulo | Tests | Descripción |
|--------|-------|-------------|
| **API Endpoints** | 13 | Tests de endpoints REST (chat, admin, health) |
| **Conversation** | 17 | Servicio de conversación y sesiones |
| **Extraction** | 12 | Servicio de extracción de datos |
| **LLM Chains** | 10 | Chains de LangChain |
| **LLM Memory** | 16 | Gestión de memoria conversacional |
| **Memory** | 17 | Sistema de memoria y persistencia |
| **RAG System** | 19 | Ingesta, almacenamiento y recuperación |
| **Storage** | 15 | Persistencia JSON de conversaciones |
| **Summarization** | 10 | Generación de resúmenes |
| **Sentiment** | 8 | Análisis de sentimiento |
| **Validators** | 10 | Validadores de Order ID y Session ID |
| **JSON I/O** | 18 | Utilidades de lectura/escritura JSON |
| **Utils** | 13 | Utilidades diversas |

### Ejecutar Tests

```bash
# Instalar dependencias de test
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx

# Ejecutar todos los tests (178 tests)
pytest tests/ -v

# Ejecución rápida
pytest tests/ --tb=no -q
# Resultado esperado: 178 passed, 79 warnings in ~1.45s

# Tests específicos por módulo
pytest tests/test_api_endpoints.py -v        # 13 tests de API
pytest tests/test_conversation.py -v         # 17 tests de conversación
pytest tests/test_rag_system.py -v           # 19 tests de RAG
pytest tests/test_extraction.py -v           # 12 tests de extracción

# Con cobertura detallada
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Ver reporte HTML de cobertura
xdg-open htmlcov/index.html  # Linux
# open htmlcov/index.html     # macOS
```

### Características de los Tests

- ✅ **Tests unitarios**: Pruebas aisladas de cada componente
- ✅ **Tests de integración**: Pruebas de flujos completos
- ✅ **Mocking robusto**: LLM, FAISS, y APIs correctamente mockeados
- ✅ **Async testing**: Tests de endpoints FastAPI con async/await
- ✅ **Fixtures compartidos**: Configuración reutilizable en `conftest.py`
- ✅ **Validación Pydantic**: Tests de validación de DTOs
- ✅ **Error handling**: Tests de manejo de errores y edge cases

### Documentación de Tests

Para más información sobre la suite de tests, consulta:

📖 **[tests/TEST_README.md](tests/TEST_README.md)** - Documentación completa de tests

Incluye:
- Guía de ejecución de tests
- Estructura y organización
- Mejores prácticas aplicadas
- Troubleshooting
- Ejemplos de tests

---

## 📖 Estructura de Archivos

```
api/
├── README.md                      # Este archivo
├── requirements_freeze.txt        # Dependencias con versiones exactas
├── lanzar.sh                      # Script de inicio rápido
│
├── kb/                            # Base de conocimiento
│   └── faqs_es.md
│
└── src/                           # Código fuente
    ├── MAIN.py                    # Punto de entrada
    ├── requirements.txt
    ├── __init__.py
    │
    ├── beans/                     # DTOs y schemas
    │   ├── api/
    │   ├── schemas/
    │   └── services/
    │
    ├── config/                    # Configuración
    │   └── settings.py
    │
    ├── core/                      # Utilidades core
    │   ├── i18n.py
    │   └── sentiment.py
    │
    ├── llm/                       # Integración LangChain
    │   ├── chains.py
    │   ├── memory.py
    │   ├── models.py
    │   └── prompts.py
    │
    ├── rag/                       # Sistema RAG
    │   ├── ingest.py
    │   ├── retriever.py
    │   └── store.py
    │
    ├── routes/                    # Endpoints FastAPI
    │   ├── admin/
    │   ├── chat/
    │   └── health/
    │
    ├── server/                    # Servidor FastAPI
    │   └── server.py
    │
    ├── services/                  # Lógica de negocio
    │   ├── conversation.py
    │   ├── extraction.py
    │   ├── storage.py
    │   ├── stt_tts.py
    │   └── summarization.py
    │
    ├── utils/                     # Utilidades
    │   ├── jsonio.py
    │   └── validators.py
    │
    └── tests/                     # Suite de tests (178 tests)
        ├── TEST_README.md         # Documentación de tests
        ├── conftest.py            # Fixtures compartidos
        ├── test_api_endpoints.py  # Tests de API (13)
        ├── test_conversation.py   # Tests de conversación (17)
        ├── test_extraction.py     # Tests de extracción (12)
        ├── test_jsonio.py         # Tests de JSON I/O (18)
        ├── test_llm_chains.py     # Tests de LLM chains (10)
        ├── test_llm_memory.py     # Tests de LLM memory (16)
        ├── test_memory.py         # Tests de memoria (17)
        ├── test_rag_system.py     # Tests de RAG (19)
        ├── test_sentiment.py      # Tests de sentimiento (8)
        ├── test_storage.py        # Tests de storage (15)
        ├── test_summarization.py  # Tests de resúmenes (10)
        └── test_validators.py     # Tests de validadores (10)
```

---

## 🔒 Seguridad

### Best Practices Implementadas

- ✅ **API Keys en .env**: Nunca hardcodeadas en código
- ✅ **Validación robusta**: Pydantic valida todos los inputs
- ✅ **Autenticación admin**: Endpoints protegidos con API key
- ✅ **Sanitización**: Regex y límites de longitud
- ✅ **No logging de secretos**: API keys nunca en logs
<!-- - ✅ **Docker no-root**: Usuario sin privilegios -->

### Recomendaciones para Producción

1. **Usar HTTPS**: Proxy reverso con Nginx + Let's Encrypt
2. **Rate limiting**: Implementar límites por IP/usuario
3. **WAF**: Cloudflare o AWS WAF
4. **Secrets manager**: AWS Secrets Manager / HashiCorp Vault
5. **Auditoría**: Logs de acceso a endpoints admin
6. **Actualizaciones**: Mantener dependencias actualizadas

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

---

## 📞 Soporte

Para preguntas, issues o sugerencias:

- **Issues**: Abre un issue en GitHub

---

## 🙏 Agradecimientos

Construido con:
- [LangChain](https://python.langchain.com/) - Framework LLM
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [FAISS](https://github.com/facebookresearch/faiss) - Vector store
- [Pydantic](https://docs.pydantic.dev/) - Validación de datos
- [TextBlob](https://textblob.readthedocs.io/) - Análisis de sentimiento

---

**Desarrollado con ❤️ byPGG para crear experiencias conversacionales inteligentes**
