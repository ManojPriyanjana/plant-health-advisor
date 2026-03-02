from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="Plant Health Advisor API")

@app.get("/")
def root():
    return {"message": "Plant Health Advisor API is running ✅"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # For now: simple demo output (we will connect real models next)
    return {
        "filename": file.filename,
        "status": "received",
        "next_step": "connect MobileNet + ViT model inference"
    }