from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.models.schemas import PromptRequest, ToolCallRequest
from app.services.audit_service import AuditService
from app.services.llm_router import LLMRouter
from app.services.llm_service import LLMService
from app.services.mcp_service import MCPService
from app.services.prompt_router import PromptRouter
from app.web.templates import HTML_TEMPLATE


router = APIRouter()

mcp_service = MCPService()
prompt_router = PromptRouter()
llm_service = LLMService()
llm_router = LLMRouter(llm_service)
audit_service = AuditService()


@router.get("/", response_class=HTMLResponse)
async def index():
    return HTML_TEMPLATE


@router.get("/api/health")
async def health():
    return {
        "app_name": settings.app_name,
        "app_env": settings.app_env,
        "mcp_server_url": settings.mcp_server_url,
        "llm_enabled": getattr(settings, "llm_enabled", True),
        "llm_ready": llm_service.is_ready(),
        "openai_model": llm_service.get_model_name(),
        "llm_base_url": llm_service.get_base_url(),
        "audit_enabled": audit_service.enabled,
        "audit_stream_key": audit_service.stream_key,
    }


@router.get("/api/tools")
async def list_tools():
    try:
        return {"tools": await mcp_service.list_tools()}
    except Exception as error:
        try:
            await audit_service.write_error(
                request_id=locals().get("request_id", audit_service.new_request_id()),
                tool=locals().get("tool_name"),
                error=str(error),
                result_type=prompt_router.get_result_type(locals().get("tool_name")) if locals().get("tool_name") else None,
            )
        except Exception:
            pass

        raise HTTPException(status_code=500, detail=str(error))


@router.get("/api/tools/schema")
async def list_tool_schemas():
    """
    Endpoint debug untuk melihat input_schema masing-masing MCP tool.
    """
    try:
        tools = await mcp_service.list_tools()
        return {
            "tools": [
                {
                    "name": tool.get("name"),
                    "description": tool.get("description"),
                    "input_schema": tool.get("input_schema"),
                }
                for tool in tools
            ]
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))



@router.get("/api/audit/recent")
async def recent_audit(limit: int = 25):
    try:
        return {
            "enabled": audit_service.enabled,
            "stream_key": audit_service.stream_key,
            "events": await audit_service.recent(limit=limit),
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/api/prompt")
async def run_prompt(req: PromptRequest):
    """
    Main prompt endpoint.

    Important:
    - Response ke UI tetap raw/full dari MCP.
    - Summary LLM memakai compact response di llm_router.py.
    """
    try:
        available_tools = await mcp_service.list_tools()
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil MCP tools: {error}")

    try:
        form_data = getattr(req, "form_data", None) or {}
        request_id = audit_service.new_request_id()
        confirmed = bool(getattr(req, "confirmed", False) or form_data.get("confirmed"))

        if req.mode == "llm":
            tool_name, arguments, reason = llm_router.select_tool(req.prompt, available_tools)
            selected_by = "llm"
        else:
            tool_name, reason = prompt_router.detect_tool(req.prompt, available_tools)
            arguments = prompt_router.build_arguments(tool_name, req.prompt, form_data) if tool_name else {}
            selected_by = "rule-based"

        if not tool_name:
            await audit_service.write_error(
                request_id=request_id,
                tool=None,
                error="Prompt belum dikenali atau tidak ada MCP tool yang cocok.",
                result_type=None,
            )
            return {
                "request_id": request_id,
                "error": "Prompt belum dikenali atau tidak ada MCP tool yang cocok.",
                "message": (
                    "Coba prompt seperti: cek koneksi, list module aktif, cari host, cari detection, "
                    "atau query NGSIEM. Untuk LLM Mode, gunakan prompt natural seperti: "
                    "'Cari aktivitas powershell 24 jam terakhir'."
                ),
                "prompt": req.prompt,
                "mode": req.mode,
                "selected_by": selected_by,
                "reason": reason,
            }

        validation_error = prompt_router.validate_arguments(tool_name, arguments)
        if validation_error:
            await audit_service.write_error(
                request_id=request_id,
                tool=tool_name,
                error=validation_error,
                result_type=prompt_router.get_result_type(tool_name),
            )
            return {
                "request_id": request_id,
                "error": validation_error,
                "requires_input": True,
                "required_input_type": "cql" if tool_name == "falcon_search_ngsiem" else "ids",
                "prompt": req.prompt,
                "mode": req.mode,
                "selected_by": selected_by,
                "reason": reason,
                "tool": tool_name,
                "arguments": arguments,
                "result_type": prompt_router.get_result_type(tool_name),
            }

        await audit_service.write_request(
            request_id=request_id,
            prompt=req.prompt,
            mode=req.mode,
            selected_by=selected_by,
            tool=tool_name,
            arguments=arguments,
            risk_level="read",
            confirmed=confirmed,
        )

        mcp_response = await mcp_service.call_tool(tool_name, arguments)

        if req.mode == "llm":
            summary = llm_router.summarize_result(
                prompt=req.prompt,
                mcp_response=mcp_response,
                tool_name=tool_name,
                arguments=arguments,
            )
        else:
            summary = prompt_router.build_summary(tool_name)

        result = mcp_response.get("result", [])

        await audit_service.write_success(
            request_id=request_id,
            tool=tool_name,
            result_type=prompt_router.get_result_type(tool_name),
            result_count=len(result) if isinstance(result, list) else None,
        )

        return {
            "request_id": request_id,
            "prompt": req.prompt,
            "mode": req.mode,
            "selected_by": selected_by,
            "reason": reason,
            "tool": tool_name,
            "arguments": arguments,
            "summary": summary,
            "result_type": prompt_router.get_result_type(tool_name),
            "result": result,
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/api/tool")
async def call_tool(req: ToolCallRequest):
    request_id = audit_service.new_request_id()

    try:
        await audit_service.write_request(
            request_id=request_id,
            prompt=f"Direct tool call: {req.tool_name}",
            mode="tool",
            selected_by="manual",
            tool=req.tool_name,
            arguments=req.arguments,
            risk_level="read",
            confirmed=bool(getattr(req, "confirmed", False)),
        )

        mcp_response = await mcp_service.call_tool(req.tool_name, req.arguments)
        result = mcp_response.get("result", [])

        await audit_service.write_success(
            request_id=request_id,
            tool=req.tool_name,
            result_type=prompt_router.get_result_type(req.tool_name),
            result_count=len(result) if isinstance(result, list) else None,
        )

        return {
            **mcp_response,
            "request_id": request_id,
            "result_type": prompt_router.get_result_type(req.tool_name),
        }
    except Exception as error:
        await audit_service.write_error(
            request_id=request_id,
            tool=req.tool_name,
            error=str(error),
            result_type=prompt_router.get_result_type(req.tool_name),
        )
        raise HTTPException(status_code=500, detail=str(error))
