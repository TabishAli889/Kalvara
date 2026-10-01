<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/logo-dark.svg">
  <img src=".github/assets/logo-light.svg" alt="Kalvara" width="88">
</picture>

# Kalvara

**A production-ready AI chat assistant that thinks locally first.**

Runs your own models through Ollama, and reaches for the cloud only when it has to.
Streaming chat, vision and real-time voice — in one self-hosted stack.

<br>

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-7-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local--first-000000?style=flat-square&logo=ollama&logoColor=white)
![LiveKit](https://img.shields.io/badge/LiveKit-voice-1FD5F9?style=flat-square&logo=livekit&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)

[Quick start](#-quick-start) · [Voice mode](#️-voice-mode) · [Photos](#️-photos) · [Model routing](#-how-model-routing-works) · [Deploying](#-production-checklist)

</div>

---

## ✨ What you get

|  |  |
|---|---|
| 🧠 **Local-first inference** | Every chat tries your installed Ollama models before anything leaves the machine. |
| ☁️ **Five cloud fallbacks** | Anthropic, OpenAI, Google Gemini, xAI Grok and Meta Llama — a provider switches on the moment its key is set. |
| 🎙️ **Real-time voice** | Speech-to-speech over WebRTC with turn detection, noise cancellation and barge-in. Transcripts land back in the chat. |
| 🖼️ **Vision input** | Paste, drop or snap photos. Stripped of metadata, resized in the browser, routed only to models that can see. |
| 🔁 **Automatic failover** | Ollama down? Key out of quota? The next model answers, and the reply says who stepped in. |
| 🎨 **Polished UI** | Streaming Markdown, chat history, search, light and dark themes, keyboard shortcuts, mobile layout. |

---

## 🚀 Quick start

> **Requirements** — Python 3.13 with [uv](https://docs.astral.sh/uv/), Node.js 20.9+, and optionally [Ollama](https://ollama.com).

```bash
# 1 ─ Local models (optional, but the whole point)
ollama pull llama3.2

# 2 ─ API  →  http://localhost:8000/docs
cd api
uv sync
cp .env.example .env            # add cloud API keys here if you have them
uv run fastapi dev app/main.py

# 3 ─ Web  →  http://localhost:3000     (new terminal)
cd web
npm install
cp .env.example .env.local
npm run dev
```

<details>
<summary><b>Prefer Docker?</b></summary>

<br>

```bash
cp api/.env.example api/.env
docker compose up --build
```

Add voice with `docker compose --profile voice up --build` once `agent/.env` is filled in.

</details>

### Project layout

```
Kalvara/
├── api/     FastAPI · Python 3.13 · uv · ruff · pytest · Ollama & provider SDKs
├── web/     Next.js 16 · React 19 · TypeScript 7 · Tailwind CSS 4 · shadcn/ui
└── agent/   LiveKit voice worker · STT → turn detection → LLM → TTS
```

---

## 🎙️ Voice mode

A sound-wave button appears in the composer as soon as the API has LiveKit
credentials. Speech-to-text, text-to-speech, turn detection and noise
cancellation all run on LiveKit Inference, so you will need a
[LiveKit Cloud](https://cloud.livekit.io) project.

```bash
# api/.env and agent/.env — the same three values from your LiveKit project
LIVEKIT_URL=wss://<your-project>.livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
```

```bash
# Start the voice agent (new terminal; the API must already be running)
cd agent
uv sync
uv run python voice_agent.py dev
```

- Replies use the model picked in the dropdown, with the same fallback as text chat — and the agent names the model that answered.
- Talking over the assistant interrupts it. So do **Stop** and **Esc**.
- Transcripts are saved into the chat tagged *Spoken*, so you can start by voice and carry on by typing.
- Nothing fails silently: a broken model is announced out loud, and if the agent is not running the UI says so after 20 seconds.

<details>
<summary><b>How a session flows</b></summary>

<br>

```
Browser ──POST /api/voice/session──► API: new room + token that dispatches the agent
   │                                     (remembers the chosen model and earlier chat)
   └──WebRTC (mic + speaker)──► LiveKit ◄── agent: STT → turn detection → reply → TTS
                                                │
                                   POST /api/voice/chat  (same model dropdown,
                                   Ollama first, cloud fallback as text chat)
```

</details>

<details>
<summary><b>Voice tuning knobs</b></summary>

<br>

In `agent/.env`: `VOICE_STT_MODEL`, `VOICE_STT_LANGUAGE`, `VOICE_TTS_MODEL`,
`VOICE_TTS_VOICE`, `VOICE_GREETING`, `VOICE_INSTRUCTIONS`,
`VOICE_NOISE_CANCELLATION`, and `VOICE_LLM` (`app`, or a LiveKit Inference
model id to bypass the app entirely).

Offer users a choice of voices with `VOICE_VOICES` in `api/.env`.

</details>

> [!WARNING]
> Anyone who can reach `/api/voice/session` can start a **billed** voice session.
> Put it behind your login before going public, and set a matching
> `VOICE_AGENT_TOKEN` in `api/.env` and `agent/.env` so only the agent can call
> `/api/voice/chat`.

---

## 🖼️ Photos

Add images with the **+** button, by pasting, or by dropping them anywhere on
the page — up to 5 per message (JPEG, PNG, WebP or GIF, 10 MB each). The browser
scales them to 2048 px on the long edge and re-encodes them, which strips
metadata such as GPS location along the way. HEIC is not supported yet; the app
explains how to share a JPEG instead.

Photos need a model that can see them — `ollama pull gemma3` (or `llava`,
`qwen2.5vl`), or any cloud key. The model menu marks these **"Sees images"**,
Auto picks one whenever a chat contains photos, and a text-only model shows a
notice with a one-click switch. The line under the input always tells you
whether a photo stays on this computer or which provider receives it.

Images live in the browser (IndexedDB) beside the chat history, and any photo
no chat still uses is cleaned up after a day. Limits are configurable in
`api/.env` — see [`api/README.md`](api/README.md).

---

## 🔁 How model routing works

The model dropdown shows three groups:

| Option | Behaviour |
|---|---|
| **Auto** *(default)* | First installed Ollama model; if none, the first cloud provider holding a key |
| **Local · Ollama** | Every chat model you have pulled, with size and parameter count |
| **Cloud (fallback)** | A sub-menu per provider whose API key is set, listing its live models |

If the chosen model fails *before replying* — Ollama stopped, model deleted, key
out of quota — the API quietly tries the next option, and the reply carries a
small note naming the model that answered instead. Set
`ALLOW_CLOUD_FALLBACK=false` in `api/.env` to turn that off.

Cloud order comes from `CLOUD_PRIORITY`, and each provider's preferred fallback
model from `*_MODEL` (e.g. `OPENAI_MODEL`). Model lists are fetched live from
each provider, so new releases appear without a code change.

---

## ✅ Quality checks

```bash
cd api && uv run ruff check . && uv run ruff format --check . && uv run pytest
cd web && npm run typecheck && npm run build
```

---

## 📦 Production checklist

- [ ] Put both services behind **HTTPS** (reverse proxy or your platform's load balancer), and keep response buffering **off** for `/api/chat` so replies stream.
- [ ] Set `ENVIRONMENT=production` (hides `/docs`) and a real `CORS_ORIGINS` if the API is called from another domain.
- [ ] Add **authentication and rate limiting** before exposing the API — cloud calls cost money.
- [ ] Set a shared `VOICE_AGENT_TOKEN` so only the agent can reach `/api/voice/chat`.
- [ ] Move chat history out of the browser and into a **database** when you add user accounts.

---

<div align="center">
<sub>Built with FastAPI, Next.js and LiveKit.</sub>
</div>
