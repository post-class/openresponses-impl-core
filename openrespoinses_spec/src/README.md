# OpenResponses src Generation Procedure and Usage

This directory contains type definitions generated from `openapi.json` and a browser runtime client.

## Target Files

- `openresponses_models.py`: Python (Pydantic v2) models generated from OpenAPI
- `openresponses_models.ts`: TypeScript type definitions generated from OpenAPI
- `openresponses_models.js`: CommonJS file output by `openapi-typescript` (mostly empty for runtime use)
- `openresponses_types.d.ts`: Thin facade for type checking only (`.d.ts`)
- `openresponses_client.js`: ESM client for browser runtime (manually managed)

## Regeneration Commands

Regenerate `openresponses_models.py` / `openresponses_models.ts` from `schema/openapi.json`.  
Since `discriminator` causes generation inconsistencies with the current schema, it is removed in preprocessing.

```bash
set -euo pipefail

SPEC_TMP="/tmp/openresponses.openapi.no_discriminator.json"
PY_OUT="initial_build_spec/api/openresponses/src/openresponses_models.py"
TS_OUT="initial_build_spec/api/openresponses/src/openresponses_models.ts"

# 1) Create temporary spec with discriminator removed
./.venv/bin/python - <<'PY'
import json
from pathlib import Path

src = Path("initial_build_spec/api/openresponses/schema/openapi.json")
dst = Path("/tmp/openresponses.openapi.no_discriminator.json")
obj = json.loads(src.read_text())

def strip_discriminator(v):
    if isinstance(v, dict):
        return {k: strip_discriminator(val) for k, val in v.items() if k != "discriminator"}
    if isinstance(v, list):
        return [strip_discriminator(x) for x in v]
    return v

dst.write_text(json.dumps(strip_discriminator(obj), ensure_ascii=False, indent=2))
print(f"WROTE {dst}")
PY

# 2) Regenerate Python models
./.venv/bin/datamodel-codegen \
  --input "$SPEC_TMP" \
  --input-file-type openapi \
  --output "$PY_OUT" \
  --output-model-type pydantic_v2.BaseModel \
  --enum-field-as-literal one

# 3) Regenerate TypeScript types
npx --yes --cache /tmp/npm-cache openapi-typescript@7.13.0 \
  "$SPEC_TMP" \
  -o "$TS_OUT"
```

## Verification Commands After Regeneration

```bash
# Check if Python import is possible
./.venv/bin/python -c "import initial_build_spec.api.openresponses.src.openresponses_models"

# Check if TS type values are not broken (OK if nothing is output)
rg -n 'type: "InputTextContentParam"|type: "ResponseOutputTextDeltaStreamingEvent"' \
  initial_build_spec/api/openresponses/src/openresponses_models.ts
```

## File Usage

### `openresponses_models.py`

Used as OpenAPI-compliant input/output models on the server-side Python.

```python
from initial_build_spec.api.openresponses.src.openresponses_models import CreateResponseBody

body = CreateResponseBody(model="gpt-5.2", input="Hello")
```

Can also be used directly as `request_model` / `response_model` in FastAPI endpoint definitions.

```python
from fastapi import APIRouter
from initial_build_spec.api.openresponses.src.openresponses_models import (
    CreateResponseBody,
    ResponseResource,
)

router = APIRouter()


@router.post("/responses", response_model=ResponseResource)
async def create_response_api(body: CreateResponseBody) -> ResponseResource:
    # Implement actual processing here and return in ResponseResource format
    # This example returns a minimal dummy
    return ResponseResource.model_validate(
        {
            "id": "resp_dummy",
            "object": "response",
            "created_at": 0,
            "completed_at": None,
            "status": "completed",
            "incomplete_details": None,
            "model": body.model or "gpt-5.2",
            "previous_response_id": None,
            "instructions": None,
            "output": [],
            "error": None,
            "tools": [],
            "tool_choice": "auto",
            "truncation": "disabled",
            "parallel_tool_calls": False,
            "text": {"format": {"type": "text"}},
            "top_p": 1.0,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
            "top_logprobs": 0,
            "temperature": 1.0,
            "reasoning": None,
            "usage": None,
            "max_output_tokens": None,
            "max_tool_calls": None,
            "store": False,
            "background": False,
            "service_tier": "default",
            "metadata": {},
            "safety_identifier": None,
            "prompt_cache_key": None,
        }
    )
```

### `openresponses_models.ts`

Used as type definitions during TypeScript compilation.  
Since it has no runtime code, use `openresponses_client.js` separately for frontend execution logic.

```ts
import type { components } from "./openresponses_models";

type CreateResponseBody = components["schemas"]["CreateResponseBody"];
```

### `openresponses_types.d.ts`

A type-only file to shorten type names used in JS/TS. Not loaded at runtime.

```js
/** @typedef {import('./openresponses_types').CreateResponseBody} CreateResponseBody */
```

### `openresponses_client.js`

Runtime ESM client for use from browser `<script type="module">`.  
Can handle both normal responses and SSE streams.

```html
<script type="module">
  import { OpenResponsesClient } from "./openresponses_client.js";

  const client = new OpenResponsesClient({
    baseUrl: "https://api.openai.com/v1",
    apiKey: "YOUR_API_KEY",
  });

  const response = await client.createResponse({
    model: "gpt-5.2",
    input: "Hello",
  });
  console.log(response);
</script>
```

### `openresponses_models.js`

A by-product of `openapi-typescript`. In CommonJS format with mostly empty content.  
Not referenced during browser runtime (type information uses `.ts` / `.d.ts`).
