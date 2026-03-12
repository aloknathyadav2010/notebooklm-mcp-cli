# Project Vision: Context Orchestration Layer (ContextBridge)

## Purpose

This document defines a high-level vision for extending `notebooklm-mcp-cli` into a broader **context orchestration layer** that can ingest, index, and retrieve knowledge across multiple providers while preserving local-first defaults.

---

## 1. Vision & Core Insight

### Core Insight
Standard LLM workflows often fail at deep reasoning over PDFs, videos, and long documents due to:
- context window constraints,
- retrieval noise,
- inconsistent extraction pipelines.

### Goal
Build a middleware **Context Store** exposed through MCP that automates ingestion and retrieval of complex data sources.

### Philosophy
- **Local-first** for privacy and developer control.
- **Scalable** enough for enterprise workloads.
- **Distribution-ready** through MCP for coding assistants and AI tools.

---

## 2. Technical Pillars

### A) Hybrid Provider Architecture

1. **Google NotebookLM**
   - Primary high-capacity reasoning backend (1M+ token context handling).

2. **Open-Notebook (lfnovo)**
   - Open-source alternative for fully self-hosted deployments.
   - Integration path:
     - Use `content-core` for robust file/content extraction.
     - Use `esperanto` for unified model/provider interfacing.

3. **Local Agentic RAG (Lite mode)**
   - Internal zero-infra fallback using:
     - `smolagents`
     - `LanceDB`

### B) High-Throughput Ingestion

- **Parallel Uploads:** Async fan-out (`asyncio`) to process multiple files concurrently.
- **Auto-MIME Routing:** Intelligent parser/handler selection inspired by `content-core` to support 50+ file types (video, audio, PPT, PDFs, docs, etc.).

---

## 3. Functional Requirements

### Parallel Processing Pipeline

- **Concurrency Control:** semaphore-based limit (default target: `5`) to reduce OOM and API rate limiting.
- **Batch Embedding:** chunk aggregation into efficient batch sizes.
- **Status Tracking:** expose a polling tool such as `get_ingest_status` for background jobs.

### Agentic Retrieval (Local Mode)

- **Self-Correction:** if retrieval score is below threshold (`0.6`), reformulate query and retry.
- **Contextual Reranking:** Cross-Encoder reranking for top-N chunk prioritization.

---

## 4. MVP Scope (Current Phase)

### Distribution
- MCP server compatibility for:
  - Claude Desktop
  - Cursor

### Core Toolset
- `upload_batch(paths)`
  - Start parallel ingestion across selected files.
- `ask_knowledge_base(query)`
  - Unified retrieval across active providers (NotebookLM / Open-Notebook / Local).
- `get_context_summary()`
  - Return concise “Context Cards” for indexed sources.

---

## 5. Architectural Constraints

- **Privacy by default:** data remains local/self-hosted unless a remote provider is explicitly selected.
- **Reference architecture alignment:** follow patterns from `lfnovo/open-notebook` for:
  - SurrealDB migration structure,
  - LangGraph state management.

---

## 6. Acceptance Criteria & Guardrails

- [ ] **Atomic Indexing:** partial failures are surfaced while successful files remain indexed.
- [ ] **Deduplication:** identical file hashes must not be reprocessed.
- [ ] **Metadata Citation:** every response includes:
  - `{source: string, page_or_timestamp: string, confidence: float}`
- [ ] **Auto-Discovery:** MCP startup scans local data directory and registers existing context.

---

## 7. Optioning Note ("Second Option")

This vision assumes a **hybrid strategy**, where NotebookLM remains the primary path while Open-Notebook and Local Agentic RAG are introduced as first-class alternatives. In practice:

- **Option 1:** NotebookLM-only execution path (minimal complexity, fastest delivery).
- **Option 2:** Hybrid orchestration path (**recommended strategic direction**) with provider abstraction and graceful fallback.

The current document captures **Option 2** as the target architecture, while still allowing Option 1 for incremental rollout.
