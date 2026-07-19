from fastapi import FastAPI
from app.routers.documents import router
from app.models.database import init_db

app = FastAPI(title="Tri9T Assignment - CT200 API")

init_db()
app.include_router(router)

@app.get("/")
def root():
    return {"message": "CT-200 Document API running"}