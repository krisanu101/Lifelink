# LifeLink container image. Made by Krisanu.
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 NO_BROWSER=1 HOST=0.0.0.0 PORT=8000
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home lifelink && mkdir -p /app/database && chown -R lifelink /app/database
USER lifelink
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)" || exit 1
CMD ["python", "backend/server.py"]
