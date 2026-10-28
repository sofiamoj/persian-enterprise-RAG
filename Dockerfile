FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 HF_HOME=/hf_cache
WORKDIR /app
COPY requirements.txt requirements-model.txt ./
# Install CPU-only torch first, from the CPU index only, so the CUDA build is never pulled in.
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install -r requirements.txt -r requirements-model.txt
COPY . .
EXPOSE 8000
# One worker: the embedding model (~500 MB RAM) is loaded once per worker.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py load_samples && gunicorn config.wsgi -b 0.0.0.0:8000 --workers 1 --threads 4 --timeout 300"]
