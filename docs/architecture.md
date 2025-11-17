# Offline AI Assistant – Architecture Overview

## 1. Goals and Design Principles

This project is an offline, modular AI assistant that runs on my own hardware (home server / old laptop). It should:

- Work fully offline once set up.
- Be modular: new features are added as separate services/tools, not by hacking the core.
- Be portable: the whole system can be moved to another machine using Git + Docker.
- Support voice interaction (wake name, speech recognition, custom voice).
- Be extendable to use GPU acceleration for LLMs, vision, and other heavy tasks.

The key idea is: **one brain (assistant-core), many tools (services)**.

---

## 2. High-Level Architecture

At a high level, the system is made of:

- **assistant-core**  
  The “brain” of the assistant. Handles conversations, calls tools, combines results, and generates final answers.

- **llm-service**  
  Wrapper around a local LLM (e.g. via Ollama). The core sends prompts here and gets back model responses.

- **tools/** (microservices)
  - **stt-service** – Speech-to-text (voice → text), e.g. Whisper.
  - **tts-service** – Text-to-speech (text → audio), e.g. Piper or other TTS.
  - **vision-service** – Camera/room analysis, object/person detection, etc.
  - **turret-service** – Talks to Nerf turret hardware (pan/tilt, fire) via ESP32/Arduino.
  - **knowledge-service** – RAG / search over Wikipedia, PDFs, notes, etc.
  - **memory-service** – Stores long-term facts, user preferences, and configuration in a database.

- **voice gateway / room node** (client layer)
  - Listens to the microphone, detects the assistant’s wake name, sends audio to STT, forwards text to assistant-core, sends replies to TTS, and plays audio back to speakers.
  - This can run on the same machine or on another device in the room.

- **automation / events (future)**  
  A small service that subscribes to events (e.g. “guard mode on”, “person detected”) and runs rules (e.g. notify me, or control turret). This keeps long-running behaviours out of assistant-core.

- **Docker + Git**  
  Used to containerize services and version the entire system so it can be deployed on any machine.

---

## 3. Request Flows

### 3.1 Text Chat Flow (simplest path)

1. A client (CLI, web UI, or test script) sends a POST request to `assistant-core`:
   - `/chat` with `{ "user_id": "matheus", "input_text": "Analyze my room." }`

2. `assistant-core`:
   - Loads the tool registry from `configs/tools.yaml`.
   - Sends the conversation context + available tools to `llm-service`.
   - The LLM decides whether to answer directly or call one or more tools (e.g. `vision.analyze_room`).

3. If a tool call is needed:
   - `assistant-core` validates the tool arguments against the tool’s JSON schema.
   - Sends an HTTP request to the tool’s endpoint (e.g. `vision-service`).
   - Receives the structured JSON response.

4. `assistant-core` sends the tool result back into the LLM to get a final natural-language reply.

5. The final reply is returned to the client as text.

From the core’s point of view, each tool is just: **name + JSON input + JSON output**.

---

### 3.2 Voice Flow (wake name + speech)

The voice interaction runs through a **voice gateway** (room node). The core still only sees text.

1. The voice gateway continuously listens to the microphone.
2. It detects the assistant’s wake name (e.g. “Apollo”) using either:
   - A wake-word engine, or
   - A simple STT prefix check (start with this for simplicity).

3. After hearing the wake name, the gateway:
   - Records the spoken command.
   - Sends audio to `stt-service` (speech-to-text API).
   - Receives transcribed text.

4. The gateway sends the text to `assistant-core` via `/chat`.

5. `assistant-core` runs the normal text chat flow (including tools).

6. The gateway receives the reply text and sends it to `tts-service` (text-to-speech API).

7. `tts-service` returns audio, and the gateway plays it on speakers.

In this design, **assistant-core never touches raw audio**. All audio handling is done in the voice gateway + STT/TTS tools.

---

## 4. Tools and the Tool Registry

Tools are independent services under `tools/`. Each has its own API and runs as a container.

### 4.1 Tool Registry (configs/tools.yaml)

The assistant does not hard-code knowledge of each tool. Instead, it reads a config file like:

- Tool name (e.g. `"vision.analyze_room"`)
- Description (for the LLM)
- HTTP endpoint (e.g. `"http://vision-service:8000/analyze_room"`)
- Input JSON schema
- Output JSON schema

Example (conceptual):

```yaml
tools:
  - name: "vision.analyze_room"
    description: "Analyze the room from the main camera and detect people and objects."
    endpoint: "http://vision-service:8000/analyze_room"
    input_schema:
      type: object
      properties:
        camera_id:
          type: string
      required: ["camera_id"]
    output_schema:
      type: object
      properties:
        people:
          type: array
          items: { type: string }
        objects:
          type: array
          items: { type: string }
        notes:
          type: string


