# Headless/CLI use of the agent (the Tkinter GUI needs a desktop; use the .exe on Windows).
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest
COPY . .
ENV DEEPSEEK_API_KEY=""
# docker run -e DEEPSEEK_API_KEY=sk-... -v "$PWD/in:/in" -v "$PWD/out:/out" simple-code-agent
ENTRYPOINT ["python", "main.py", "--cli", "--doc", "/in/Architecture_Documentation.md", "--views", "/in/Architecture_View.md", "--out", "/out"]
