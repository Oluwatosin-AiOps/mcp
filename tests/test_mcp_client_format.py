import mcp.types as types

from app.mcp_client import format_tool_result, tool_to_openai_function


def test_format_tool_result_text_only():
    result = types.CallToolResult(
        content=[types.TextContent(type="text", text="SKU MON-1 available.")],
        isError=False,
    )
    assert format_tool_result(result) == "SKU MON-1 available."


def test_tool_to_openai_shape():
    tool = types.Tool(
        name="sample_tool",
        description="Does something.",
        inputSchema={"type": "object", "properties": {"q": {"type": "string"}}},
    )
    spec = tool_to_openai_function(tool)
    assert spec["type"] == "function"
    assert spec["function"]["name"] == "sample_tool"
    assert spec["function"]["parameters"]["type"] == "object"
