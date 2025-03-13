from fastapi import FastAPI
from app.configuration.server import Server

def create_app(_=None) -> FastAPI:
    
    app = FastAPI(title="TestServices",
                  debug=True)
    return Server(app).get_app()