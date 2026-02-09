## Slack bot integration (Data Engineer workflow) using this repo’s Cortex assets

This repo already creates two Cortex Search services:

- `DOCS` over `DOCS_CHUNKS_TABLE.chunk` (unstructured retrieval with `relative_path` + `category`)
- `ARTICLE_NAME_SEARCH` over `DIM_ARTICLE.ARTICLE_NAME` (structured “entity lookup” / fuzzy matching)

It also uploads semantic model YAML files to the `SEMANTIC_FILES` stage:

- `semantic.yaml` (core semantic model over `DIM_ARTICLE`, `DIM_CUSTOMER`, `FACT_SALES`)
- `semantic_search.yaml` (semantic model that *references* a Cortex Search service for `ARTICLE_NAME`)

Below is a practical pattern for a **Slack bot** that uses these objects outside Snowsight.

---

## Recommended architecture

**Slack (Events API / Slash command)** → **Bot service (Python/Node)** → **Snowflake**

In Snowflake, the bot uses:

- **Cortex Search** (retrieval) for doc/runbook questions (RAG-style answers with citations)
- **Semantic model (Cortex Analyst-style patterns)** for structured Q&A (NL → governed SQL → results)

---

## Authentication & governance (what a DE should insist on)

- **Snowflake auth**
  - Prefer **key-pair auth** or **OAuth** for the bot service (avoid user/password in a `.env`).
  - Use a dedicated role (least privilege) that can:
    - query the required tables/views
    - query the required Cortex Search services
    - write bot audit logs (optional)
- **Slack auth**
  - Use Slack’s **signing secret** verification.
  - Use a **bot token** with the minimum scopes needed (e.g., read messages, post messages).
- **Data governance**
  - If sensitive data exists, only expose **secured views** to the semantic model.
  - Enforce row access policies / masking policies as normal—bot should never bypass them.

---

## Bot workflow (high signal, cost-aware)

### 1) Receive a user question

Inputs to capture:

- question text
- Slack user/channel/thread
- optional “mode” hint: `docs:` vs `data:` (helps routing)

### 2) Route the question (unstructured vs structured)

Two common routes:

- **Docs route (Cortex Search `DOCS`)**
  - Use when user asks “how do I…”, “where is the SOP…”, “what’s the runbook for…”, etc.
- **Data route (semantic model / governed SQL)**
  - Use when user asks about metrics, trends, counts, “top N”, “by region”, etc.

In this repo’s setup, the “data route” is grounded by the semantic model describing:

- tables, joins, dimensions, synonyms, sample values

### 3) Execute Snowflake calls with guardrails

**Docs route** (Cortex Search):

- Query `DOCS` and retrieve the top-k chunks (keep k small, e.g., 3–5)
- Post answer + citations back to Slack (include `relative_path` and a short excerpt)

**Data route** (semantic model):

- Convert question → SQL using your semantic layer rules (and/or Analyst capabilities if enabled)
- Execute SQL with:
  - timeouts
  - row limits
  - “explain”/dry-run in non-prod if needed
- Post a small table + the SQL used (or a link) back to Slack

### 4) Log for audit + improvement (optional, but recommended)

Create an audit table for bot interactions:

```sql
CREATE TABLE IF NOT EXISTS DATA.BOT_QUERY_LOG (
  ts TIMESTAMP_NTZ,
  slack_user STRING,
  slack_channel STRING,
  slack_thread STRING,
  route STRING, -- 'docs' | 'data'
  question STRING,
  executed_sql STRING,
  result_summary STRING
);
```

This gives you:

- quality evaluation data
- debugging breadcrumbs
- governance traceability

---

## Cost management questions to answer up front (DE checklist)

- **Cortex Search**
  - What is the expected row count in `DOCS_CHUNKS_TABLE` and how fast does it grow?
  - What is the average chunk length (and how does overlap inflate total tokens)?
  - Do we really need `TARGET_LAG = '1 hour'`, or can we relax freshness to cut cost?
- **SQL compute**
  - What warehouse runs the “data route” queries? Should bot queries use a smaller warehouse?
  - Do we need result caching / pre-aggregations for common questions?
- **Bot behavior**
  - Rate limits per Slack user/channel to prevent runaway cost
  - Hard caps (top-k for retrieval, max rows for SQL results, max runtime)

---

## How this repo’s objects map into the Slack bot

- **Unstructured (docs/runbooks/SOPs)**
  - Stored as chunks in `DOCS_CHUNKS_TABLE.chunk`
  - Retrieved via Cortex Search service `DOCS`
  - Cited via `relative_path` (and optionally filtered via `category`)

- **Structured (business tables)**
  - Modeled in `semantic.yaml` as governed dimensions/facts across:
    - `DIM_ARTICLE`, `DIM_CUSTOMER`, `FACT_SALES`
  - Entity resolution enhancement:
    - `semantic_search.yaml` ties `DIM_ARTICLE.ARTICLE_NAME` to a search service so the system can map fuzzy names to canonical values.

---

## Implementation notes (intentionally high-level)

Slack bots are typically implemented with:

- **Python**: Slack Bolt + Snowflake Python Connector/Snowpark
- **Node**: Bolt JS + Snowflake SDKs

To query Cortex Search outside Snowsight, use one of:

- **SQL from your connector** (preferred operationally)
- **The `service_query_url`** (returned by `DESCRIBE CORTEX SEARCH SERVICE`) from a backend service

See Snowflake docs for the latest query interface details:

- `https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview`
- `https://docs.snowflake.com/en/sql-reference/sql/desc-cortex-search`

