FROM python:3.11-slim AS base

# Keep Python output predictable in containers.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*


FROM base AS api

RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch

COPY requirements.api.txt .
RUN pip install --no-cache-dir -r requirements.api.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS ui

COPY requirements.ui.txt .
RUN pip install --no-cache-dir -r requirements.ui.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
