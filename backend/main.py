import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import(
    ALLOWED_ORIGINS, 
    APP_DESCRIPTION, 
    APP_TITLE, 
    APP_VERSION, 
    SPACY_MODEL_PRIMARY, 
    SPACY_MODEL_SECONDARY, SENTENCE_TRANSFORMER_MODEL
)
from backend.api.routes import router

logger=logging.getLogger('ats_resume_scorer')  # You know how when something goes wrong in your app, you want to know what happened and when? That's what a logger does.

@asynccontextmanager  # async lets the server multitask — while waiting for slow things (file reading, database calls, AI model responses), it handles other requests instead of sitting idle.
async def lifespan(app:FastAPI):  # Think of yield like a pause button. Everything before yield runs at startup, everything after yield runs at shutdown.
    # Why load models here and not inside each request? Because AI models are heavy — loading spaCy or SentenceTransformer takes a few seconds. If you loaded them inside every request:
    logger.info('Starting ATS Resume Analyzer API...')

    logger.info(f'Loading spaCy NLP model: {SPACY_MODEL_PRIMARY}')
    import spacy
    try:
        app.state.nlp = spacy.load(SPACY_MODEL_PRIMARY)
        logger.info(f'Loaded {SPACY_MODEL_PRIMARY}')
    except OSError:
        logger.warning(f'{SPACY_MODEL_PRIMARY} not found — downloading...')
        import subprocess
        subprocess.run(["python", "-m", "spacy", "download", SPACY_MODEL_PRIMARY])
        try:
            app.state.nlp = spacy.load(SPACY_MODEL_PRIMARY)
        except OSError:
            subprocess.run(["python", "-m", "spacy", "download", SPACY_MODEL_SECONDARY])
            app.state.nlp = spacy.load(SPACY_MODEL_SECONDARY)
    logger.info(f'Loading SentenceTransformer: {SENTENCE_TRANSFORMER_MODEL}')
    from sentence_transformers import SentenceTransformer
    app.state.embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    logger.info(f'Loaded {SENTENCE_TRANSFORMER_MODEL}')

    logger.info('All models loaded. API is ready to serve requests.')
    assert hasattr(app.state, "nlp")
    assert hasattr(app.state, "embedder")
    yield

    logger.info('shutting down the api!!')

app=FastAPI(
    title=APP_TITLE, 
    description=APP_DESCRIPTION, 
    version=APP_VERSION, 
    lifespan=lifespan,
    docs_url='/docs',
    redoc_url='/redoc'
)

app.add_middleware(  # CORS middleware tells your backend "yes, requests from this specific frontend are allowed."
    CORSMiddleware, 
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True, 
    allow_methods     = ['*'],
    allow_headers     = ['*'],

)

app.include_router(router)  # This plugs in all your API routes (like /analyze-resume, /history etc.) which are defined in a separate routes.py file. Keeps the code organized — main.py doesn't need to know the details of every route.

@app.get('/')     # The decorator takes your function and registers it with FastAPI as "when someone sends a GET request to /, call this function.
async def root():
    return {
        'name':      'ATS Resume Analyzer API',
        'version':   '2.0.0',
        'endpoints': {
            'POST   /api/v1/analyze-resume': 'Analyze a resume',
            'GET    /api/v1/history':        'Get user history',
            'DELETE /api/v1/history/:id':    'Delete a history entry',
            'GET    /api/v1/health':         'Health check',
            'POST   /api/v1/generate-pdf':   'Generate PDF report from data',
        },
    }

if __name__=='__main__':  # if __name__ == '__main__' means — only run this block if you directly execute this file (python main.py), not when it's imported by something else.
    import uvicorn        # Uvicorn is the actual server that listens for incoming HTTP requests and passes them to FastAPI.
    uvicorn.run(
        'backend.main:app',
        host    = '0.0.0.0',
        port    = 8000,
        reload  = True,    # Auto-restart on code changes (dev only)
    )