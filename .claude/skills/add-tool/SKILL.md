---
name: add-tool
description: Scaffold a new LangChain tool for the voice assistant following the project's Atomic Tool pattern. Use when the user wants to add a new capability (e.g. a new API integration).
argument-hint: [tool-name] [description]
disable-model-invocation: true
allowed-tools: Read, Grep, Write, Edit, Bash
---

# Add New LangChain Tool

Scaffold a new tool for this project following the established Atomic Tool pattern.

## Arguments

- `$ARGUMENTS[0]` — snake_case tool name (e.g. `spotify`, `calendar`, `maps`)
- `$ARGUMENTS[1]` — one-sentence description of what the tool does

If arguments are missing, ask the user for: tool name, what API it calls, what parameters it needs, and what it returns.

## Steps

### 1. Read existing tools for reference

Read `src/tools/events.py` as the most complete example — it shows:
- `Union[str, dict, None]` location param pattern
- `display_limit = max(N, int(limit))` safety floor
- `ws_sender` injection for action pushback
- Nominatim rate-limit awareness

Also read `src/tools/base.py` for the `BaseTool` interface.

### 2. Create `src/tools/<tool_name>.py`

Follow this exact structure:

```python
"""
<ToolName> Tool
<Brief description of what it does and which API it calls>
"""

import os
import requests
from typing import Optional, Union
from tools.base import BaseTool
from loguru import logger


class <ToolName>Tool(BaseTool):
    name = "<tool_name>"
    description = "<LLM-facing description — this is what the agent reads to decide when to call it>"

    def __init__(self, location_adapter=None, ws_sender=None):
        self.location_adapter = location_adapter
        self.ws_sender = ws_sender
        self.api_key = os.getenv("<TOOL_API_KEY_ENV_VAR>")

    def execute(self, param: str, location: Union[str, dict, None] = None, **kwargs) -> dict:
        try:
            # 1. Resolve location if needed
            # 2. Call external API
            # 3. Parse and return results
            return {"success": True, "results": []}
        except Exception as e:
            return self.handle_error(e)
```

**Key rules to follow:**
- `location` param must be `Union[str, dict, None]` — never `dict` alone (LLM may pass a string)
- Normalize location internally — never let Pydantic reject a string
- No `image_url` fields in returned dicts — LLM renders them as `![Image](url)` in chat
- Log at `INFO` for successful calls, `WARNING` for rate limits / fallbacks, `ERROR` for failures
- Return `{"success": False, "error": "..."}` on failure, never raise

### 3. Register in `src/agent/core.py`

Add to `_initialize_tools()`:

```python
from tools.<tool_name> import <ToolName>Tool
<tool_name>_tool = <ToolName>Tool(self.location_adapter, ws_sender=self._ws_sender)
tools.append(StructuredTool.from_function(
    func=<tool_name>_tool.execute,
    name=<tool_name>_tool.name,
    description=<tool_name>_tool.description,
))
```

### 4. Add environment variable (if the tool needs an API key)

Add to `config/.env.example`:
```
<TOOL_API_KEY_ENV_VAR>=your_key_here
```

Document it in the `Environment Variables` table in `CLAUDE.md` and `docs/PROJECT_SUMMARY.md`.

### 5. Optionally add a quick-action chip in `ui/src/App.tsx`

In the `handleQuickAction` messages map:
```typescript
<tool_name>: "Trigger phrase for the new tool",
```

In the quick actions bar (keep to 4 chips max; use `--compact` modifier):
```tsx
<button className="chat-window__qa-btn" onClick={() => handleQuickAction('<tool_name>')} disabled={!isConnected}>
  <Icon /> <span>Label</span>
</button>
```

### 6. Verify

Ask the user to test with a natural language query in the chat and confirm the tool appears in LangSmith traces (if enabled).
