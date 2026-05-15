# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Install (local dev):**
```bash
pip install -e ".[dev]"
# or via conda:
conda env create -f environment.yml && conda activate app_environment
```

**Lint:**
```bash
ruff check src/
ruff format src/
```

**Run Snowflake object setup** (one-time pipeline, requires `.env`):
```bash
cd src && python run_setup.py
```

**Run Streamlit/Git integration setup** (deploys app to Snowflake, requires `.env` with `pat`):
```bash
cd src && python run_streamlit_setup.py
```

**Run interactive Claude CLI** (direct Anthropic SDK, requires `.env` with `claude_api_key`):
```bash
cd src && python run_claude_sdk.py
```

**Streamlit app** (`streamlit_app.py`) runs *inside* Snowflake as a Streamlit in Snowflake (SiS) app — it cannot be run locally because it uses `_snowflake` and `get_active_session()`.

## Environment Variables (`.env`)

| Variable | Purpose |
|---|---|
| `ACCOUNT` | Snowflake account identifier |
| `USER` | Snowflake username |
| `PASSWORD` | Snowflake password |
| `pat` | GitHub Personal Access Token (for Git integration setup) |
| `claude_api_key` | Anthropic API key (for `run_claude_sdk.py`) |
| `ANTHROPIC_MODEL` | Model override (default: `claude-sonnet-4-5`) |

## Architecture

This project builds an "Intelligent Sales Assistant" that answers questions about a synthetic bikes/skis dataset by routing between two retrieval methods within a Snowflake Cortex Agent.

### Two Distinct Execution Modes

**1. Snowflake Cortex Agent path (`streamlit_app.py`)**
- Runs as a Streamlit in Snowflake app; calls `/api/v2/cortex/agent:run` via `_snowflake.send_snow_api_request`
- The agent model is `claude-3-5-sonnet` and is given two tools:
  - `cortex_analyst_text_to_sql` ("Sales Analyst") — converts natural language to SQL using a semantic model YAML file staged at `@SEMANTIC_FILES/semantic_search.yaml`
  - `cortex_search` ("Docs and Images Search") — searches `DASH_CORTEX_AGENTS_SUMMIT.PUBLIC.DOCUMENTATION_TOOL`, which is the Cortex Search service built over `DOCS_CHUNKS_TABLE`
- Responses are SSE-streamed JSON; `process_sse_response()` extracts text, SQL, and citations
- Citations referencing `.jpeg` files are rendered as images via presigned URLs; citations referencing `.pdf` files render the relevant chunk text

**2. Direct Anthropic SDK path (`src/run_claude_sdk.py`)**
- Local interactive REPL; sends messages directly to the Anthropic API
- `src/utils/utils_claude.py` manages conversation history and injects system prompts
- `src/utils/claude_skills/persona_detect.py` detects persona instructions (e.g., "act as a teacher") in the user message via regex and maps them to system prompt templates

### Snowflake Data Pipeline (`src/run_setup.py` + `src/utils/`)

The setup pipeline builds the retrieval layer used by the Cortex Agent:

1. **`setup.sql`** — bootstraps roles, databases (`DASH_CORTEX_AGENTS.DATA`), the `DOCS` stage, Git integration, and an email notification procedure
2. **`cortex_setup.py`** — orchestrates:
   - `AI_PARSE_DOCUMENT` → extracts text from PDFs into `RAW_TEXT`
   - `CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER` → chunks text into `DOCS_CHUNKS_TABLE` (1512-token chunks, 256-token overlap, markdown format)
   - `AI_CLASSIFY` → tags each chunk as `Bike` or `Snow`
   - `AI_COMPLETE('claude-4-sonnet', ...)` → generates descriptions for `.jpeg` images and inserts them into `DOCS_CHUNKS_TABLE`
   - Creates `CORTEX SEARCH SERVICE DOCS` over `DOCS_CHUNKS_TABLE`
3. **`semantic_tables.py`** — creates and populates `DIM_ARTICLE` (8 products), `DIM_CUSTOMER` (5,000 generated rows), and `FACT_SALES` (10,000 generated rows)
4. **`stage_setup.py`** — uploads `semantic.yaml` and `semantic_search.yaml` to the `SEMANTIC_FILES` stage
5. Creates `CORTEX SEARCH SERVICE ARTICLE_NAME_SEARCH` over `DIM_ARTICLE.ARTICLE_NAME`

### Semantic Models

There are two nearly identical semantic model YAML files that differ only in the target Snowflake database/schema:

| File | Database | Schema | Used by |
|---|---|---|---|
| `semantic.yaml` | `DASH_CORTEX_AGENTS` | `DATA` | Local dev / testing |
| `semantic_search.yaml` | `DASH_CORTEX_AGENTS_SUMMIT` | `PUBLIC` | `streamlit_app.py` (SiS) |

Both define the same star schema: `FACT_SALES` joined to `DIM_ARTICLE` and `DIM_CUSTOMER`. The `semantic_search.yaml` version also includes a `cortex_search_service` reference on `ARTICLE_NAME` for fuzzy product name lookup.

### Key Snowflake Objects

- **Database/Schema**: `DASH_CORTEX_AGENTS.DATA` (local) / `DASH_CORTEX_AGENTS_SUMMIT.PUBLIC` (SiS)
- **Stages**: `DOCS` (PDFs + images), `SEMANTIC_FILES` (YAML files)
- **Tables**: `DOCS_CHUNKS_TABLE`, `DIM_ARTICLE`, `DIM_CUSTOMER`, `FACT_SALES`
- **Cortex Search Services**: `DOCS`, `ARTICLE_NAME_SEARCH`
- **Role**: `SNOWFLAKE_INTELLIGENCE_ADMIN` is required for pipeline setup; `ACCOUNTADMIN` for initial SQL bootstrapping
