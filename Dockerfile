# FlowDesk v2 — image backend (API + ingest: satu image, dua peran)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PIP_NO_CACHE_DIR=1

WORKDIR /app


COPY requirements.txt .
RUN pip install torch==2.14.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt
RUN python -c "from sentence_transformers import SentenceTransformer; \
               SentenceTransformer('intfloat/multilingual-e5-base')"

# 3) Kode aplikasi. data/ dan frontend/ SENGAJA tidak di-copy:
#    - data dimount ke service ingest (KB bisa berubah tanpa rebuild)
#    - frontend diserve oleh container nginx sendiri
COPY src /app/src
COPY scripts /app/scripts

EXPOSE 8000
CMD ["python", "scripts/serve.py"]
