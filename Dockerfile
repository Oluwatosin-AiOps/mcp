# Run: docker build -t meridian-mcp .
# Run: docker run --rm -p 7860:7860 -e OPENAI_API_KEY -e MCP_SERVER_URL -e MODEL_NAME meridian-mcp
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY app.py ./app.py

ENV PYTHONUNBUFFERED=1
EXPOSE 7860

CMD ["python", "app.py"]
