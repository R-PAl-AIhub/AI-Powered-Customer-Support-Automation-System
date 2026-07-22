# AI-Powered Customer Support Automation System

A multi-agent customer-support assistant built with **LangGraph**. It classifies an
incoming customer query, routes it to the right department agent, answers using a
**RAG** knowledge base, and escalates sensitive requests (refunds, cancellations,
account closures) to a **human supervisor** via a human-in-the-loop review step.
Conversations are persisted with a SQLite checkpointer, so the bot remembers history
across turns and restarts.

---

## Features

- **Intent classification** — every query is classified into Sales, Technical Support, Billing, Account, or General.
- **Department routing** — a router sends the query to the matching specialist agent.
- **RAG answers** — agents retrieve relevant chunks from a FAISS vector store built from the knowledge-base documents.
- **Deterministic human escalation** — sensitive requests are detected in code (not left to the LLM) and paused for supervisor approval.
- **Human-in-the-loop** — the graph interrupts, shows the draft to a supervisor, and resumes with their feedback (approve or revise).
- **Persistent memory** — `SqliteSaver` stores conversation state per `thread_id` in `chatbot.db`.

---

## Architecture

```
                ┌──────────────┐
   customer ──► │ classifyQuery│  (LLM → Sales / Technical / Billing / Account / General)
                └──────┬───────┘
                       │ router
        ┌──────────────┼───────────────┬───────────────┐
        ▼              ▼               ▼               ▼
   Sales_Agent   Technical_Agent   Billing_Agent   Account_Agent     (RAG + draft + needs_review)
        └──────────────┴───────────────┴───────────────┘
                       │ route_after_draft
            needs_review? ──No──────────────► finalize ──► reply to customer
                       │ Yes
                       ▼
                 human_review  ── interrupt() → supervisor sees draft
                       │ route_after_review
              approve ─┴─ instructions
                 │             │
                 ▼             ▼
              finalize    revise_response ──► back to human_review
```

---

## Project structure

```
.
├── app.py                      # CLI entry point: runs the chat loop + supervisor prompts
├── chatbot.db                  # SQLite checkpointer store (conversation memory)
│
├── graph/
│   ├── CustomerSupportState.py # The shared TypedDict state passed between nodes
│   └── workflow.py             # Builds and compiles the LangGraph graph
│
├── nodes/
│   ├── classifyQuery.py        # Classifies the query into a department label
│   ├── router.py               # Maps the classification → agent node
│   ├── route_after_draft.py    # After an agent drafts: human_review or finalize
│   ├── route_after_review.py   # After review: finalize (approved) or revise_response
│   ├── human_review_node.py    # Pauses the graph (interrupt) for supervisor input
│   ├── revise_response.py      # Rewrites the draft using supervisor feedback
│   └── finalize.py             # Sets final_response from the approved draft
│
├── agents/
│   ├── sales_agent.py          # Department specialists. Each one:
│   ├── billing_agent.py        #  - retrieves KB context (RAG)
│   ├── technical_support.py    #  - drafts a reply with conversation history
│   └── account_agent.py        #  - flags sensitive requests for review
│
├── knowldgeBase/
│   ├── *.txt                   # Source documents (policies, FAQ, pricing, manual)
│   ├── vector_db.py            # One-time script: builds the FAISS vector store
│   ├── database_retriver.py    # Loads the store and exposes a retriever
│   └── ai_support_vector_db/   # Saved FAISS index (generated)
│
└── utils/
    ├── llm.py                  # ChatOllama LLM config (llama3.2:3b)
    ├── escalation.py           # needs_human(): keyword check for escalation
    └── history.py              # format_history(): prior turns for follow-up questions
```

---

## State (`CustomerSupportState`)

| Field | Type | Purpose |
|-------|------|---------|
| `messages` | list (`add_messages`) | Full conversation history (appended automatically) |
| `customer_queries` | str | Raw customer query (optional) |
| `classify_customer_issue` | str | Department label from the classifier |
| `support_department` | str | Concerned department |
| `ai_draft` | str | Current draft reply (single source of truth for review) |
| `human_feedback` | str | Supervisor's reply during human review |
| `kb_context` | str | Retrieved knowledge-base text |
| `needs_review` | bool | True when the request must be escalated |
| `final_response` | str | Final answer sent to the customer |

---

## Requirements

- **Python 3.11+**
- **[Ollama](https://ollama.com/)** running locally, with the required models pulled.
- Python packages:
  - `langgraph`
  - `langchain-core`
  - `langchain-community`
  - `langchain-ollama`
  - `langchain-text-splitters`
  - `langgraph-checkpoint-sqlite`
  - `faiss-cpu`
  - `pydantic`

Install:

```bash
pip install langgraph langchain-core langchain-community langchain-ollama \
            langchain-text-splitters langgraph-checkpoint-sqlite faiss-cpu pydantic
```

---

## Setup

**1. Start Ollama and pull the models** used in `utils/llm.py` and the embeddings:

```bash
ollama serve                       # if not already running
ollama pull llama3.2:3b            # chat model
ollama pull nomic-embed-text       # embedding model for the vector store
```

**2. Build the knowledge-base vector store** (run once, or whenever the documents change):

```bash
python -m knowldgeBase.vector_db
```

This reads the `.txt` files, chunks and embeds them, and saves the FAISS index.

---

## Running

From the **project root**, run:

```bash
python app.py
```

Then chat in the terminal:

```
=== AI-Powered Customer Support Automation System ===
Customer: What are your pricing plans?
Agent: We offer Basic ($10/mo), Pro ($25/mo) ...
```

Type `exit` to quit.

### Human escalation example

```
Customer: I need a refund for my annual subscription.

========================================
⚠️  SUPERVISOR REVIEW REQUIRED
========================================
Customer : I need a refund for my annual subscription.
Draft    : <the AI's proposed reply>
========================================

Supervisor — 'approve' or instructions: please apologise and confirm the 30-day window
🤖 Response revised.
...
Supervisor — 'approve' or instructions: approve

Agent: <final approved reply to the customer>
```

- Type **`approve`** (or `yes` / `ok`) to send the draft as-is.
- Type **anything else** to give revision instructions; the draft is rewritten and re-reviewed.

---

## How it works

1. **`classifyQuery`** asks the LLM to label the query (Sales / Technical Support / Billing / Account / General).
2. **`router`** maps that label to the matching agent node.
3. The **agent** retrieves relevant KB chunks, drafts a reply (using conversation history), stores it in `ai_draft`, and sets `needs_review` via `utils/escalation.needs_human()`.
4. **`route_after_draft`** sends the case to `human_review` when `needs_review` is true, otherwise to `finalize`.
5. **`human_review`** calls `interrupt(ai_draft)` — the graph pauses and surfaces the draft to `app.py`, which prompts the supervisor.
6. **`route_after_review`** finalizes on approval, or sends to **`revise_response`** (which rewrites the draft from feedback) and loops back to review.
7. **`finalize`** copies the approved draft into `final_response`, which is shown to the customer.

---

## Memory

- State is checkpointed by `SqliteSaver` into `chatbot.db`, keyed by `thread_id`.
- `app.py` uses a fixed `thread_id` (`customer_session_1`), so history persists **across restarts**.
- Agents include recent turns (`utils/history.format_history`) in their prompts so follow-up questions work.
- To start a fresh conversation, change the `thread_id` in `app.py` (or delete `chatbot.db`).

---

## Notes & customization

- **LLM / models:** edit `utils/llm.py` (chat model) and `knowldgeBase/vector_db.py` + `database_retriver.py` (embedding model). Keep the embedding model identical for building and loading the store.
- **Escalation triggers:** edit the keyword list in `utils/escalation.py`.
- **Knowledge base:** add/replace `.txt` files in `knowldgeBase/`, then re-run `python -m knowldgeBase.vector_db`.
- Run modules from the project root (use `python -m package.module`) so package imports resolve.
