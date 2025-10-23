from fastapi import FastAPI

app = FastAPI(title="Voiture Search API")

@app.get("/")
async def root(): 
    return {"message": "API ok"}
