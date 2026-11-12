from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from routers import index_router

app = FastAPI(title='INDEX API - Metadata Tagger & Search Optimization', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(index_router.router)


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'agent': 'INDEX',
        'eyebrow': 'METADATA TAGGER'
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8002, reload=True)

