# Gmail Invoice Extractor

Week 1 deliverable from a [6-month AI Agent Engineer roadmap](../ai-engineer-roadmap/ROADMAP.md). Ports a personal n8n invoice-extraction workflow to pure Python + the Anthropic SDK — no LangChain, no agent framework — to see what the "LLM node" abstraction was hiding.

## What it does (v0)

- Takes an invoice image (JPG/PNG)
- Sends it to Claude Haiku with a Pydantic schema
- Returns a validated `Invoice` object: vendor, invoice number, date, total, currency

## Stack

- `uv` — package/venv/Python management
- `anthropic` — Claude SDK (vision + prefill for reliable JSON)
- `pydantic` — runtime-checked schemas
- `ruff` + `pytest` — lint, format, unit tests

## Run

```bash
uv sync
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
uv run python main.py path/to/invoice.jpg
uv run pytest -v
```

## Design notes

- **Prefilling**: the assistant turn is prefilled with `{` so Claude cannot emit markdown fences. More reliable than "please return JSON" instructions.
- **Unit tests vs evals**: tests cover pure logic (schema, media type mapping) deterministically. Extraction *quality* belongs in an eval suite (coming in Month 3 of the roadmap), not unit tests.

## Roadmap

- **Week 1** ✅ one-shot image → structured invoice
- **Week 2** hand-rolled tool loop, retries, better structured output
- **Week 3** versioned prompt library, XML tags, prompt caching
- **Week 4** full Gmail → webhook → Sheets pipeline
