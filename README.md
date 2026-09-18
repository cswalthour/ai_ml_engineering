# AI/ML Engineering — Intelligent Sales Assistant

Part of [cswalthour/ai_ml_engineering](https://github.com/cswalthour/ai_ml_engineering) (`claude-sdk` branch).

## Overview

This project builds an "Intelligent Sales Assistant" that answers questions about a synthetic bikes/skis dataset by routing between two retrieval methods within a Snowflake Cortex Agent: natural-language-to-SQL analytics over structured sales data (`cortex_analyst_text_to_sql`), and semantic search over product documentation and images (`cortex_search`). It also includes a standalone REPL for talking to Claude directly via the Anthropic SDK (`src/run_claude_sdk.py`).

See [`CLAUDE.md`](CLAUDE.md) for setup commands, environment variables, and a full architecture breakdown.

## Attribution

This project originated from Snowflake's [Build Agentic AI Application in Snowflake](https://quickstarts.snowflake.com/guide/build-agentic-application-in-snowflake/index.html) quickstart guide and has since been substantially extended (Anthropic SDK integration, Claude-based personas, additional tooling). The original quickstart's Apache 2.0 license is preserved in [`LICENSE`](LICENSE).
