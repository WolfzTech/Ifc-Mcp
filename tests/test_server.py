def test_server_imports():
    import server
    assert hasattr(server, "mcp")
    assert callable(getattr(server.mcp, "run", None))
    assert len(server.mcp._tool_manager._tools) == 20
