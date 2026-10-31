"""Serverless deployment FlowDesk v2 di Modal.com (Scale-to-Zero).

Menyajikan FastAPI (/ask, /feedback, /health) sekaligus UI statis (/)
dalam satu container serverless tanpa perlu NGINX terpisah.

Cara deploy:
    modal deploy deploy_modal.py
"""
import os
import sys
import modal

app = modal.App("flowdesk-v2")

# 1. Bangun image container (identik dengan Dockerfile: Python 3.12 + CPU torch + cache e5-base)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .run_commands(
        "pip install torch==2.14.0 --index-url https://download.pytorch.org/whl/cpu"
    )
    .pip_install_from_requirements("requirements.txt")
    .run_commands(
        'python -c "from sentence_transformers import SentenceTransformer; '
        "SentenceTransformer('intfloat/multilingual-e5-base')\""
    )
    .env({
        "PYTHONPATH": "/app/src",
        "FLOWDESK_FRONTEND_DIR": "/app/frontend",
    })
    .add_local_dir("src", remote_path="/app/src")
    .add_local_dir("frontend", remote_path="/app/frontend")
)


# 2. Bungkus FastAPI create_app() sebagai endpoint ASGI serverless
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv()],  
    memory=2048,                           # 2 GB RAM (untuk model multilingual-e5-base)
    scaledown_window=120,                  
    max_containers=1,                      
    timeout=300,                           
)
@modal.asgi_app()
def web():
    sys.path.insert(0, "/app/src")
    cloud_dsn = os.environ.get("CLOUD_PG_DSN", "").strip()
    if cloud_dsn:
        os.environ["FLOWDESK_PG_DSN"] = cloud_dsn
        os.environ["FEEDBACK_PG_DSN"] = cloud_dsn

    from flowdesk.api.app import create_app
    return create_app()