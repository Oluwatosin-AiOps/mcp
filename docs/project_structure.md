# Project structure

```text
app/           package: config, mcp_client, agent, guardrails, auth_session, ui
app.py         entry: Gradio (no args), --print-config, or CLI agent turn
tests/
scripts/       discovery + smoke scripts
docs/
docker-compose.yml
pyproject.toml / uv.lock / requirements.txt / .python-version
README.md      Spaces YAML + body
.env.example
```

`app.py` stays thin. `app.agent` owns the tool loop and uses `mcp_client` + `guardrails`.
