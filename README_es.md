[English](./README.md) | **Español** | [中文](./README_zh.md)

<div align="center">

<img src="assets/banner.svg" alt="SuearchHermes" width="720"/>

# SuearchHermes

**Búsqueda Google gratis para Hermes Agent — Sin API Key, Sin Costo, Resultados Reales de Google**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Hermes](https://img.shields.io/badge/Hermes-Agent-6E40C9?style=flat&logo=gnometerminal&logoColor=white)](https://github.com/NousResearch/hermes-agent)
[![agy](https://img.shields.io/badge/Antigravity%20CLI-agy-4285F4?style=flat&logo=google&logoColor=white)](https://github.com/google-antigravity/antigravity-cli)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](./LICENSE)
[![Cost](https://img.shields.io/badge/Costo-Gratis%20%E2%80%A2%20Sin%20API%20Key-brightgreen?style=flat)]()

[Características](#-características) · [Por qué](#-por-qué) · [Demo](#-demo) · [Instalación](#-instalación-rápida) · [Ejemplos](#-ejemplos) · [Arquitectura](#-arquitectura) · [Roadmap](#-roadmap) · [Contribuir](#-contribuir)

</div>

---

## 📰 Noticias

- **2026-07-14** 🚀 **v1.0.0 lanzada**: Primer release público. Plugin de búsqueda Google via Antigravity CLI (agy) para Hermes Agent. Gratis, sin API key, Google Search Grounding via Gemini. Incluye instalador de un comando, implementación completa del ABC `WebSearchProvider` de Hermes, y configuración automática. ([Notas del release](https://github.com/leonardo-ferioli/SuearchHermes/releases/tag/v1.0.0))

---

## 🎯 Por qué?

Hermes Agent incluye soporte para `web_search`, pero los backends integrados tienen problemas:

| Backend | Costo | API Key | Calidad | Problema |
|---|---|---|---|---|
| **Firecrawl** | 💰 Pago | Requerida | ⭐⭐⭐⭐ | Billing por request |
| **Tavily** | 💰 Pago | Requerida | ⭐⭐⭐⭐ | Free tier limitado |
| **Exa** | 💰 Pago | Requerida | ⭐⭐⭐ | API key requerida |
| **Brave (free)** | ⚠️ Limitado | Requerida | ⭐⭐⭐ | 2,000 queries/mes |
| **DDGS** | ✅ Gratis | Ninguna | ⭐ | Calidad pobre, rate-limited |
| **SuearchHermes** | ✅ Gratis | **Ninguna** | ⭐⭐⭐⭐⭐ | **Usa Google via Gemini** |

---

## ✨ Características

- 🔍 **Google Search real** — via Gemini Search Grounding, no scraping
- 🆓 **Sin costo** — sin API key, sin billing, sin tarjeta de crédito
- 🧠 **Respuestas sintetizadas** — Gemini lee los resultados y da una respuesta concisa con fuentes
- 🔌 **Plugin drop-in** — implementa el ABC `WebSearchProvider` de Hermes
- ⚡ **Instalación de un comando** — `./install.sh` hace todo
- 🌐 **Dominios limpios** — devuelve `github.com`, no URLs de redirect opacos
- 🖥️ **Multiplataforma** — Linux, macOS

---

## 🎬 Demo

```
> busca la última versión de rust

Hermes: La última versión estable de Rust es 1.97.0, lanzada el 9 de julio de 2026.
         Fuentes: rust-lang.org, releases.rs
```

```
> investiga sobre rust9x

Hermes: Rust9x es un fork no oficial del compilador de Rust que restaura
         compatibilidad para Windows 9x/ME/NT/2000/XP/Vista.
         Fuentes: github.com, seri.tools, reddit.com
```

---

## 🚀 Instalación Rápida

### Prerrequisitos

1. **Hermes Agent** instalado (`~/.hermes/hermes-agent/`)
2. **Antigravity CLI** (`agy`) instalado y autenticado:

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
agy  # autenticar con tu cuenta de Google
```

### Instalar

```bash
git clone https://github.com/leonardo-ferioli/SuearchHermes.git
cd SuearchHermes
./install.sh
```

El script:
- ✅ Copia el plugin a `~/.hermes/hermes-agent/plugins/web/agy/`
- ✅ Verifica que `agy` esté instalado
- ✅ Agrega `web.search_backend: agy` a `~/.hermes/config.yaml`

### Usar

Solo pídele a Hermes que busque algo:

```
> busca la última versión de rust
> investiga sobre rust9x
> busca esto: mejores frameworks de Python 2026
```

---

## 📝 Ejemplos

### Ejemplo 1: Check de versión

```
> busca la última versión estable de rust
```

**Resultado:**
```json
{
  "success": true,
  "data": {
    "web": [
      {"title": "Rust 1.97.0 lanzada el 9 julio 2026", "url": "rust-lang.org", "description": "...", "position": 1},
      {"title": "releases.rs", "url": "https://releases.rs", "description": "", "position": 2}
    ]
  }
}
```

### Ejemplo 2: Investigación

```
> investiga rust9x windows xp fork
```

**Resultado:**
```json
{
  "success": true,
  "data": {
    "web": [
      {"title": "Rust9x es un fork no oficial...", "url": "github.com", "description": "...", "position": 1},
      {"title": "seri.tools", "url": "https://seri.tools", "description": "", "position": 2}
    ]
  }
}
```

---

## 🏛️ Arquitectura

```
SuearchHermes/
├── install.sh              # Instalador
├── plugins/
│   └── web/
│       └── agy/
│           ├── __init__.py  # Registro del plugin
│           └── provider.py  # AgYWebSearchProvider
└── assets/
    └── banner.svg          # Logo
```

El plugin implementa el ABC `WebSearchProvider` de Hermes y llama `agy -p` para cada búsqueda. La respuesta se normaliza al formato esperado por Hermes: `{"web": [{"title", "url", "description", "position"}]}`.

---

## 🛣️ Roadmap

- [x] v1.0.0 — Plugin core, instalador, docs
- [ ] **v1.1.0** — Soporte de extracción (contenido de páginas via agy)
- [ ] **v1.2.0** — Plantilla de prompt configurable
- [ ] **v1.3.0** — Cache de respuestas
- [ ] **v2.0.0** — Integración directa con Gemini API (sin agy CLI)

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Ver [CONTRIBUTING.md](./CONTRIBUTING.md).

Para agentes de IA que contribuyan, ver [AGENT_CONTRIBUTOR_GUIDE.md](./AGENT_CONTRIBUTOR_GUIDE.md).

---

## 📋 Requisitos

| Requisito | Versión | Notas |
|---|---|---|
| Hermes Agent | cualquier versión con plugin system | `~/.hermes/hermes-agent/` |
| Antigravity CLI | 1.1.0+ | `curl -fsSL https://antigravity.google/cli/install.sh \| bash` |
| Python | 3.10+ | viene con Hermes |
| OS | Linux, macOS | donde `agy` funcione |
| Cuenta Google | cualquiera | para OAuth de agy (gratis) |

---

## 📄 Licencia

MIT — ver [LICENSE](./LICENSE)

---

## 👤 Autor

**Leonardo Ferioli** — [@leonardo-ferioli](https://github.com/leonardo-ferioli)

---

<div align="center">

**SuearchHermes** — Búsqueda Google, gratis, para Hermes Agent.

Construido porque scraping de DuckDuckGo y APIs pagas de SERP no son suficientes.

Si este proyecto te sirvió, considera ⭐ darle star al repo.

</div>
