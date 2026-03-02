import os

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse

from app.inference.vision import VisionEnsemble
from app.nlp.advisor import build_advisory_response

app = FastAPI(title="Plant Health Advisor API")

# Change these class names to match your training labels exactly.
# The order must be identical to model outputs.
CLASS_NAMES = [
    "Tomato___Late_blight",
    "Tomato___healthy",
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

MOBILENET_PATH = os.path.join(MODEL_DIR, "mobilenet_model.keras")
VIT_PATH = os.path.join(MODEL_DIR, "vit_model.keras")

vision = VisionEnsemble(
    mobilenet_path=MOBILENET_PATH,
    vit_path=VIT_PATH,
    class_names=CLASS_NAMES,
)


@app.get("/")
def root():
    return {"message": "Plant Health Advisor API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    model: str = Query(default="ensemble", pattern="^(mobilenet|vit|ensemble)$"),
    top_k: int = Query(default=0, ge=0, le=10),
):
    image_bytes = await file.read()

    try:
        prediction = vision.predict(image_bytes=image_bytes, model=model, top_k=top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}") from exc

    advisory = build_advisory_response(prediction["predicted_label"])

    payload = {
        "filename": file.filename,
        "model": prediction["model"],
        "predicted_label": prediction["predicted_label"],
        "confidence": round(prediction["confidence"], 4),
        "advisory": advisory,
    }

    if "top_k" in prediction:
        payload["top_k"] = [
            {"label": item["label"], "confidence": round(item["confidence"], 4)}
            for item in prediction["top_k"]
        ]

    return JSONResponse(payload)
