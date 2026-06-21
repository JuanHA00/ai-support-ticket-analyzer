# AI Support Ticket Analyzer

Analizador de tickets de soporte con limpieza de datos, enriquecimiento mock de IA, API en FastAPI y dashboard en Streamlit.

El proyecto procesa `tickets.csv`, normaliza datos inconsistentes, genera campos enriquecidos y expone los resultados para consulta desde una API y una interfaz visual.

## Funcionalidades

- Carga y limpieza de tickets desde CSV.
- Normalizacion de edades, prioridades, tipos de ticket, fechas, emails, productos y canales.
- Deteccion de inconsistencias temporales entre primera respuesta y resolucion.
- Enriquecimiento mock de IA:
  - categoria sugerida
  - prioridad sugerida
  - resumen corto
  - sentimiento/urgencia
  - equipo responsable
- API con FastAPI.
- Endpoint `/ask` para preguntas basicas en lenguaje natural usando tickets procesados y una base de conocimiento.
- Dashboard con KPIs, filtros, tabla y visualizaciones.

## Estructura

```text
.
├── app/
│   ├── ask.py
│   ├── data_processing.py
│   ├── knowledge_base.md
│   ├── main.py
│   └── metrics.py
├── dashboard/
│   └── dashboard.py
├── scripts/
│   └── process_data.py
├── code.ipynb
├── tickets.csv
├── processed_tickets.csv
├── requirements.txt
└── README.md
```

## Instalacion

Crear y activar un entorno virtual:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Procesar datos

Generar `processed_tickets.csv`:

```powershell
python scripts/process_data.py
```

Este comando lee `tickets.csv`, aplica limpieza, genera enriquecimiento mock de IA y guarda el CSV procesado.

## Ejecutar API

Desde la raiz del proyecto:

```powershell
python -m uvicorn app.main:app --reload
```

Abrir documentacion interactiva:

```text
http://127.0.0.1:8000/docs
```

## Ejecutar dashboard

En otra terminal, con la API corriendo:

```powershell
python -m streamlit run dashboard/dashboard.py
```

Streamlit abrira una URL local, normalmente:

```text
http://localhost:8501
```

## Ejecutar con Docker

Docker es opcional, pero permite levantar API y dashboard con un solo comando.

Requisito: tener Docker Desktop instalado y abierto.

El comando se ejecuta desde PowerShell o la terminal de VS Code, ubicado en la raiz del proyecto:

```powershell
docker compose up --build
```

Servicios:

```text
API:       http://localhost:8000/docs
Dashboard: http://localhost:8501
```

En Docker, el dashboard usa la variable `API_URL=http://api:8000` para comunicarse con el backend dentro de la red de Compose.

Para detener los servicios:

```powershell
docker compose down
```

## Endpoints principales

### `GET /health`

Verifica que la API este activa.

### `GET /tickets`

Lista tickets procesados y enriquecidos.

Parametro opcional:

- `limit`: cantidad de tickets a devolver.

Ejemplo:

```text
http://127.0.0.1:8000/tickets?limit=20
```

### `GET /summary`

Devuelve metricas agregadas:

- total de tickets
- tickets abiertos
- tickets altos/criticos
- prioridades desconocidas
- inconsistencias temporales
- distribucion por prioridad, tipo, estado, equipo responsable y productos principales

### `POST /ask`

Permite hacer preguntas basicas en lenguaje natural sobre los tickets.

Ejemplo de body:

```json
{
  "question": "Que equipo tiene mas carga de tickets?"
}
```

El endpoint usa:

- tickets procesados
- metricas agregadas
- `app/knowledge_base.md`

Actualmente responde con reglas mock.

## Variables de entorno

No se requieren variables de entorno para ejecutar esta version.

No se usa API key externa. El sistema corre en modo mock para que pueda evaluarse localmente sin costos.

## Decisiones tecnicas

- **Python + pandas**: se eligio por su fortaleza para limpieza, transformacion y analisis de datos.
- **FastAPI**: permite exponer los tickets procesados, metricas y `/ask` como servicio backend.
- **Streamlit**: permite construir rapidamente un dashboard funcional para explorar resultados.
- **Modo mock de IA**: evita dependencia de API keys y permite ejecutar el proyecto en cualquier maquina.
- **Base de conocimiento Markdown**: mantiene reglas de negocio simples y editables.

## Limpieza de datos

Se encontraron y trataron problemas como:

- 6 duplicados exactos eliminados.
- `Customer Age` con valores invalidos (`0`, `-3`, `200`, `999`) y texto (`thirty`, `veinticinco`).
- `Ticket Priority` con valores inconsistentes (`urgent`, `alta`, `baja`, `P1`, `P2`, etc.).
- Valores numericos aislados de prioridad (`1`, `2`, `3`, `4`) tratados como ambiguos.
- Fechas de compra en formatos mixtos, incluyendo meses en espanol.
- Nulos esperados en resolucion y satisfaccion para tickets abiertos o pendientes.
- 68 registros donde la resolucion aparece antes de la primera respuesta.

## IA y arquitectura

La integracion de IA esta encapsulada en:

- `enrich_with_mock_ai()` en `app/data_processing.py`
- `answer_question()` en `app/ask.py`

Actualmente ambas usan reglas mock. La arquitectura permite reemplazarlas por un proveedor real como Ollama, OpenAI, Gemini o un modelo LLaMA sin modificar la limpieza, las metricas, los endpoints ni el dashboard.

Ejemplo de evolucion:

```text
enrich_with_mock_ai()
↓
enrich_with_ollama()
↓
enrich_with_openai()
```

## Limitaciones conocidas

- `/ask` usa reglas simples, no un LLM real.
- El enriquecimiento mock no entiende contexto profundo ni sarcasmo.
- La metrica de tiempos de resolucion requiere filtrar inconsistencias temporales antes de usarse como KPI final.
- No hay persistencia en base de datos; los datos se cargan desde CSV.
- El dashboard depende de que la API este corriendo.

## Mejoras futuras

- Integrar Ollama o OpenAI para enriquecimiento real.
- Guardar tickets procesados en SQLite.
- Agregar paginacion y filtros directamente en `/tickets`.
- Mejorar `/ask` con recuperacion de contexto desde tickets relevantes.
- Agregar tests unitarios para limpieza y metricas.

## Uso de IA durante el desarrollo

Se uso ChatGPT/Codex como asistente de desarrollo para:

- interpretar el enunciado tecnico
- razonar decisiones de limpieza de datos
- documentar supuestos en el notebook
- migrar logica exploratoria a modulos Python
- estructurar API, dashboard y README

Las decisiones de limpieza fueron validadas manualmente revisando salidas del notebook, conteos, distribuciones y ejemplos de registros problematicos.
