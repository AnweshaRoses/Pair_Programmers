from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import router
from app.core.config import settings
from app.api import websocket as websocket_router
from app.api import rooms as rooms_router
from app.api import autocomplete as autocomplete_router

app = FastAPI(title="Realtime Code Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(autocomplete_router.router)
app.include_router(rooms_router.router)
app.include_router(websocket_router.router)


@app.get("/")
async def root():
    return {"message": "Backend is running", "env": settings.ENV}
