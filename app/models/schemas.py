from typing import Any, Dict, Literal

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    mode: Literal["rule", "llm"] = "rule"
    customer_name: str | None = None

    # Safety confirmation untuk tools yang bersifat modify/destructive.
    # Bisa dikirim langsung di body atau lewat form_data["confirmed"].
    confirmed: bool = False

    # Untuk field tambahan dari UI:
    # - cql_query
    # - query_string
    # - start
    # - limit
    # - filter
    # - ids
    # - confirmed
    form_data: Dict[str, Any] = Field(default_factory=dict)


class ToolCallRequest(BaseModel):
    tool_name: str = Field(..., min_length=1)
    arguments: Dict[str, Any] = Field(default_factory=dict)

    # Wajib true untuk tools yang mengubah atau menghapus data.
    confirmed: bool = False
