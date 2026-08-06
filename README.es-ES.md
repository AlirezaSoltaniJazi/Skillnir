

# Skillnir

[![CI - Tests](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/run-tests.yml/badge.svg)](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/run-tests.yml)
[![CI - Style](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/check-style.yml/badge.svg)](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/check-style.yml)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Inyecta habilidades de programación con IA en el directorio de configuración de cualquier herramienta.

## Descripción General

Skillnir genera, gestiona e inyecta habilidades de IA específicas de dominio en los directorios de configuración de múltiples herramientas de programación con IA. Una única habilidad funciona en Claude Code, Cursor, GitHub Copilot, Gemini, Codex, Windsurf y Cline.

Las habilidades son archivos markdown estructurados que enseñan a los asistentes de IA patrones, convenciones y flujos de trabajo específicos del proyecto. Skillnir analiza tu proyecto, genera habilidades con IA y crea enlaces simbólicos hacia la ubicación esperada por cada herramienta.

## Stack Tecnológico

| Componente      | Tecnología                                                                                                             |
| -------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Lenguaje       | Python 3.14+                                                                                                           |
| Construcción   | hatchling + uv (gestor de paquetes)                                                                                       |
| CLI            | argparse + questionary (interactivo)                                                                                   |
| Interfaz Web   | NiceGUI 2.0+ (framework web para Python basado en Quasar/Vue)                                                                   |
| Generación IA  | claude-agent-sdk + subprocess (Claude, Cursor, Gemini, Copilot)                                                        |
| i18n           | Módulo personalizado, 9 idiomas (EN, DE, NL, PL, FA, UK, SQ, FR, AR), soporte RTL                                           |
| Análisis Config| PyYAML (frontmatter de SKILL.md)                                                                                          |
| Pruebas        | pytest + pytest-asyncio                                                                                                |
| Linting        | Black (-S), Pylint, Autoflake, Bandit, Prettier                                                                        |
| Pre-commit     | 12 hooks (espacios en blanco, EOF, YAML, archivos grandes, AST, conflictos de fusión, seguridad, bandit, autoflake, pylint, black, prettier) |

## Características

- **Generación de habilidades multi-backend** -- genera habilidades usando Claude Code, Cursor, Gemini o GitHub Copilot
- **37 ámbitos (scopes) de habilidades** -- backend, frontend, android, ios, infra, testing, js, python, test-design, general-system, y más
- **Inyección entre herramientas** -- una habilidad, enlazada simbólicamente en `.claude/`, `.cursor/`, `.github/`, `.gemini/`, `.codex/`, `.agents/`, y más
- **Interfaz Web** -- panel de control basado en NiceGUI para todas las operaciones
- **CLI** -- conjunto completo de comandos para scripting y automatización
- **Sincronización consciente de versiones** -- actualiza habilidades entre proyectos con comparación de versiones
- **Generación de documentación IA** -- genera `agents.md` con instrucciones de programación específicas del proyecto
- **Generación de reglas para Cursor** -- genera archivos de reglas `.mdc` para Cursor
- **Investigación IA** -- busca y resume noticias de ingeniería con IA, organizadas por tema
- **Eventos IA** -- busca próximas conferencias, meetups y talleres de IA en 12 países con banderas y filtrado por gratuitos/de pago
- **Benchmarks IA** -- compara los principales modelos de IA en 7 categorías de benchmark con precios y ventanas de contexto
- **Vulnerabilidades de seguridad** -- busca CVEs, zero-days y avisos en 10 categorías y 8 fuentes
- **Compresión de prompts** -- reducción de tokens del 30-50% basada en reglas para prompts de pipelines
- **Notificaciones multi-proveedor** -- alertas por webhook a Google Chat, Slack, Discord, Teams, Telegram, Zoho Cliq al completar tareas
- **Gestión de archivos de ignorado** -- crea andamio e inyecta archivos de ignorado específicos de herramienta (.claudeignore, .cursorignore, etc.)
- **Interfaz multiidioma** -- 9 idiomas (inglés, alemán, neerlandés, polaco, persa, ucraniano, albanés, francés, árabe) con soporte RTL

## Inicio Rápido

### Instalación

```bash
# Clonar el repositorio
git clone git@github.com:AlirezaSoltaniJazi/Skillnir.git
cd skillnir

# Instalar con uv
uv sync

# Verificar instalación
uv run skillnir --help
```

### Generar una habilidad

```bash
uv run skillnir generate-skill
```

### Instalar habilidades en un proyecto

```bash
uv run skillnir install
```

### Iniciar la interfaz web

```bash
uv run skillnir ui
```

### Ejecutar pruebas

```bash
uv run pytest
```

### Ejecutar verificaciones de estilo

```bash
# Todas las verificaciones a la vez (vía pre-commit)
uv run pre-commit run --all-files

# Verificaciones individuales
black --check -S src/ tests/
autoflake --check --remove-all-unused-imports --remove-unused-variables -r src/ tests/
pylint -rn --rcfile=.pylintrc src/skillnir/
bandit -lll -iii -r src/
```

## Comandos CLI

| Comando            | Descripción                                                                   |
| ------------------ | ----------------------------------------------------------------------------- |
| `install`          | Sincroniza habilidades e inyecta enlaces simbólicos en directorios de herramientas de IA (predeterminado)            |
| `install-ignore`   | Instala archivos de ignorado en directorios de herramientas de IA                                 |
| `update`           | Sincroniza solo habilidades (comparación de versiones, sin cambios en enlaces simbólicos)                     |
| `generate-docs`    | Genera `agents.md` con análisis del proyecto potenciado por IA                         |
| `generate-skill`   | Genera un `SKILL.md` específico de dominio con IA                                 |
| `generate-rule`    | Genera archivos de reglas de Cursor (`.mdc`) con IA                                   |
| `generate-wiki`    | Genera wiki del proyecto (`llms.txt` + `docs/`) con IA                          |
| `compress-docs`    | Compresión basada en reglas + tono IA de toda la documentación relacionada con IA                       |
| `optimize-docs`    | Audita y (opcionalmente) corrige inconsistencias en documentación de IA + referencias cruzadas                |
| `check-skill`      | Valida patrones de habilidades instaladas vía backend de IA                              |
| `init-skill`       | Crea un andamio de habilidad predeterminado con archivos de marcador de posición                        |
| `init-docs`        | Crea una plantilla predeterminada de `agents.md` con enlaces simbólicos de herramientas                      |
| `delete-skill`     | Elimina habilidad(es) de un proyecto                                                |
| `delete-docs`      | Elimina documentos de IA de un proyecto                                                 |
| `delete-wiki`      | Elimina la wiki del proyecto (`llms.txt` + `docs/`) de un proyecto                     |
| `ask`              | Hazle una pregunta a la IA sobre un proyecto (solo lectura)                                 |
| `plan`             | Obtén un plan de implementación detallado de la IA                                    |
| `research`         | Busca las últimas noticias de ingeniería con IA y genera resúmenes                      |
| `testing-research` | Busca las últimas noticias de pruebas/CA (manual, automatización, IA en pruebas, rendimiento, a11y) |
| `events`           | Busca próximos eventos y conferencias de IA en todo el mundo                           |
| `config`           | Gestiona la configuración del backend y del modelo                                        |
| `sound`            | Gestiona los hooks de notificación sonora de Claude Code                                   |
| `ui`               | Inicia la interfaz web                                                      |

## Estructura del Proyecto

```
skillnir/
├── src/skillnir/          # Paquete Python principal
│   ├── cli.py                # Punto de entrada CLI (argparse + questionary)
│   ├── backends.py           # Configuración del backend
│   ├── benchmarks.py         # Pipeline de búsqueda de benchmarks de modelos IA
│   ├── compressor.py         # Compresión de prompts basada en reglas
│   ├── crypto.py             # Cifrado Fernet para almacenamiento de credenciales
│   ├── events.py             # Pipeline de búsqueda de eventos IA
│   ├── generator.py          # Generación de documentación IA
│   ├── hooks.py              # Gestión de hooks de Claude Code
│   ├── i18n.py               # Internacionalización (9 idiomas)
│   ├── injector.py           # Lógica de inyección de enlaces simbólicos
│   ├── notifications/        # Paquete de webhooks multi-proveedor
│   ├── researcher.py         # Investigación y resumen de noticias IA
│   ├── remover.py            # Eliminación de habilidades y documentos
│   ├── security.py           # Pipeline de búsqueda de vulnerabilidades de seguridad
│   ├── skill_generator.py    # Generación de habilidades multi-backend
│   ├── skills.py             # Descubrimiento y análisis de habilidades
│   ├── syncer.py             # Sincronización de habilidades consciente de versiones
│   ├── tools.py              # Definiciones de herramientas IA (38 herramientas)
│   ├── usage.py              # Seguimiento de uso de tokens
│   ├── locales/              # Archivos de traducción (en, de, nl, pl, fa, uk, sq, fr, ar)
│   ├── ui/                   # Interfaz web NiceGUI
│   └── resources/            # Plantillas HTML y activos estáticos
├── scripts/               # Scripts ejecutores de CI (run_intel.py)
├── .data/
│   ├── skills/               # Directorios fuente de habilidades
│   ├── promptsv1/            # Prompts de generación de habilidades (32 plantillas)
│   ├── research/             # Artículos de investigación (organizados por tema)
│   └── events/               # Datos de eventos IA
├── tests/                    # Suite de pruebas pytest (18 archivos de prueba)
├── pyproject.toml            # Configuración de construcción (hatchling)
└── .pre-commit-config.yaml
```

## Habilidades

Las habilidades son directorios markdown estructurados que enseñan a las herramientas de IA los patrones de tu proyecto:

```
skillName/
├── SKILL.md       # Guía de decisiones (cargado al activar)
├── INJECT.md      # Referencia rápida siempre cargada
├── LEARNED.md     # Correcciones y preferencias acumuladas por sesión
├── references/    # Documentación detallada y ejemplos de código
├── scripts/       # Scripts de validación y utilidades
└── agents/        # Definiciones de sub-agentes
```

### Ámbitos Disponibles (26)

| Categoría                | Ámbitos                                                                 |
| ----------------------- | ---------------------------------------------------------------------- |
| Desarrollo de Aplicaciones | backend, frontend, android, ios, js, python, go, cross-platform-mobile |
| Datos y APIs             | database, api-design, data-science                                     |
| Pruebas y Calidad       | testing, test-design, locator, playwright, wdio, selenium, appium      |
| Operaciones y Seguridad   | infra, security, observability, performance                            |
| Especializados             | chrome-extension, accessibility, migration, general-system             |

## Uso en CI / GitHub Actions

Skillnir puede usarse como biblioteca en pipelines de CI mediante `scripts/run_intel.py`, un ejecutor no interactivo que llama directamente a la API async de Python (evita el CLI interactivo que se quedaría colgado en CI).

### Inicio Rápido (GitHub Actions)

```yaml
- name: Checkout Skillnir
  uses: actions/checkout@v6
  with:
    repository: AlirezaSoltaniJazi/Skillnir
    ref: main
    path: skillnir

- name: Install uv + Python + Skillnir
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv python install 3.14
    cd skillnir && uv venv --python 3.14 .venv
    . .venv/bin/activate && uv pip install -e .

- name: Install Cursor CLI
  run: curl https://cursor.com/install -fsSL | bash

- name: Run research pipeline
  env:
    AI_AGENT_TOOL: cursor
    AI_AGENT_API_KEY: ${{ secrets.AI_AGENT_API_KEY }}
    AI_AGENT_WEBHOOK_URL: ${{ secrets.AI_AGENT_WEBHOOK_URL }}
    AI_AGENT_MODEL: auto
  run: |
    cd skillnir && . .venv/bin/activate
    python scripts/run_intel.py research
```

### Características Soportadas

```bash
python scripts/run_intel.py research     # Artículos de noticias IA
python scripts/run_intel.py events       # Conferencias y meetups IA
python scripts/run_intel.py security     # CVEs y avisos
python scripts/run_intel.py benchmarks   # Rankings de modelos IA
```

### Variables de Entorno

| Variable                        | Requerido | Predeterminado                                 | Descripción                                                                   |
| ------------------------------- | -------- | --------------------------------------- | ----------------------------------------------------------------------------- |
| `AI_AGENT_API_KEY`              | Sí      | —                                       | Clave API para la herramienta de IA (ej. clave API de Cursor)                                 |
| `AI_AGENT_TOOL`                 | No       | `cursor`                                | Qué backend de IA usar                                                       |
| `AI_AGENT_WEBHOOK_URL`          | No       | —                                       | Webhook de Google Chat para notificaciones. Omítelo para omitir                           |
| `AI_AGENT_MODEL`                | No       | `auto`                                  | Nombre del modelo principal                                                            |
| `AI_AGENT_MODEL_FALLBACK`       | No       | —                                       | Modelo de respaldo en caso de fallo del principal                                             |
| `AI_AGENT_RESEARCH_DATE_RANGE`  | No       | —                                       | Filtro de fecha para investigación (ej. `published after 2026-01-01`)                  |
| `AI_AGENT_RESEARCH_TOPICS`      | No       | all                                     | Claves de temas separadas por comas                                                    |
| `AI_AGENT_EVENT_COUNTRIES`      | No       | all                                     | Códigos de país separados por comas (ej. `uk,de`)                                  |
| `AI_AGENT_SECURITY_CATEGORIES`  | No       | all                                     | Claves de categorías separadas por comas                                                 |
| `AI_AGENT_BENCHMARK_TOP_N`      | No       | `10`                                    | Número de modelos principales a obtener                                                 |
| `AI_AGENT_NOTIFY_CHUNK_SIZE`    | No       | `15`                                    | Elementos por tarjeta de Google Chat (dividido para evitar el límite de 32KB)                      |
| `AI_AGENT_NOTIFY_BUTTON_TEXT`   | No       | `View source`                           | Etiqueta para el botón de enlace por elemento                                            |
| `AI_AGENT_NOTIFY_SUBTITLE`      | No       | `{feature} — {count} new item(s)`       | Plantilla de subtítulo del encabezado de la tarjeta. Marcadores de posición: `{feature}`, `{count}`, `{part}` |
| `AI_AGENT_NOTIFY_OVERFLOW_TEXT` | No       | `+{count} more — see workflow artifact` | Texto de pie de página de desbordamiento. Marcador de posición: `{count}`                                  |
| `AI_AGENT_NOTIFY_DESC_MAX`      | No       | `150`                                   | Caracteres máximos para descripciones de elementos (truncado con `...`)                   |

### Notificaciones

Cuando `AI_AGENT_WEBHOOK_URL` está configurado, el ejecutor envía una única tarjeta consolidada de Google Chat que lista todos los nuevos elementos descubiertos en la ejecución. Cada elemento incluye título, descripción y un botón de enlace clicable. La deduplicación es automática mediante archivos de índice en disco; ejecutar la misma característica dos veces produce cero notificaciones duplicadas. El texto de la tarjeta (subtítulo, etiqueta del botón, mensaje de desbordamiento, longitud de la descripción) es personalizable mediante las variables de entorno `AI_AGENT_NOTIFY_*` anteriores.

### Salida

La última línea de stdout es un resumen JSON legible por máquina:

```
SUMMARY {"feature":"research","tool_used":"cursor","new_count":5,"notified":true,"model_used":"auto","fallback_used":false,...}
```

## Contribuir

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para la configuración de desarrollo, estilo de código y directrices de PR.

## Licencia

[MIT](LICENSE)
