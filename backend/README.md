## Setup and running

Create `.env` file with `GROQ_API_KEY` and `ALLOWED_ORIGINS` (optionally `GROQ_MODEL` and `MODEL_TEMPERATURE`)

Local with hot-reloading:

```bash
pyenv install
pyenv exec pip install -r requirements.txt   
pyenv exec pytest
cd src
pyenv exec python -m uvicorn api:app --reload
```

(Probably better to setup in a virtual environment)
