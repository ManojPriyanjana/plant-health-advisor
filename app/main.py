import os
import io

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image

from app.inference.vision import VisionEnsemble
from app.nlp.advisor import build_advisory_response

app = FastAPI(title="Plant Health Advisor API")

# Change these class names to match your training labels exactly.
# The order must be identical to model outputs.
CLASS_NAMES = [
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

CONFIDENCE_THRESHOLD = 0.65
DISAGREEMENT_MIN_CONFIDENCE = 0.55
MIN_IMAGE_SIDE_PX = 224
MIN_BRIGHTNESS = 45.0
MIN_SHARPNESS = 20.0

APP_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
STATIC_DIR = os.path.join(APP_DIR, "static")

MOBILENET_PATH = os.path.join(MODEL_DIR, "mobilenet_model.keras")
VIT_PATH = os.path.join(MODEL_DIR, "vit_model.keras")

vision = VisionEnsemble(
    mobilenet_path=MOBILENET_PATH,
    vit_path=VIT_PATH,
    class_names=CLASS_NAMES,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def assess_image_quality(image_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size

    gray = np.asarray(image.convert("L"), dtype=np.float32)
    brightness = float(np.mean(gray))
    # Use local gradient variance as a lightweight blur proxy.
    sharpness = float(np.var(np.diff(gray, axis=1)) + np.var(np.diff(gray, axis=0)))

    issues: list[str] = []
    if min(width, height) < MIN_IMAGE_SIDE_PX:
        issues.append(
            f"Image is low resolution ({width}x{height}). Use at least {MIN_IMAGE_SIDE_PX}px on the shorter side."
        )
    if brightness < MIN_BRIGHTNESS:
        issues.append("Image appears too dark. Use better lighting for more reliable predictions.")
    if sharpness < MIN_SHARPNESS:
        issues.append("Image appears blurry. Capture a sharper close-up of the affected leaves.")

    return {
        "width": width,
        "height": height,
        "brightness": round(brightness, 2),
        "sharpness": round(sharpness, 2),
        "issues": issues,
    }


def detect_model_disagreement(mobilenet_prediction: dict, vit_prediction: dict) -> dict:
    mobilenet_label = mobilenet_prediction["predicted_label"]
    vit_label = vit_prediction["predicted_label"]
    mobilenet_conf = float(mobilenet_prediction["confidence"])
    vit_conf = float(vit_prediction["confidence"])

    labels_match = mobilenet_label == vit_label
    both_confident = (
        mobilenet_conf >= DISAGREEMENT_MIN_CONFIDENCE and vit_conf >= DISAGREEMENT_MIN_CONFIDENCE
    )
    is_disagreement = (not labels_match) and both_confident

    return {
        "labels_match": labels_match,
        "is_disagreement": is_disagreement,
        "mobilenet_label": mobilenet_label,
        "mobilenet_confidence": round(mobilenet_conf, 4),
        "vit_label": vit_label,
        "vit_confidence": round(vit_conf, 4),
    }


def run_prediction(image_bytes: bytes, filename: str, model: str, top_k: int = 0) -> dict:
    quality = assess_image_quality(image_bytes=image_bytes)

    prediction = vision.predict(image_bytes=image_bytes, model=model, top_k=top_k)
    mobilenet_prediction = (
        prediction
        if model == "mobilenet"
        else vision.predict(image_bytes=image_bytes, model="mobilenet", top_k=0)
    )
    vit_prediction = (
        prediction if model == "vit" else vision.predict(image_bytes=image_bytes, model="vit", top_k=0)
    )
    disagreement = detect_model_disagreement(
        mobilenet_prediction=mobilenet_prediction,
        vit_prediction=vit_prediction,
    )

    advisory = build_advisory_response(prediction["predicted_label"])
    is_uncertain = float(prediction["confidence"]) < CONFIDENCE_THRESHOLD
    warnings: list[str] = []
    if is_uncertain:
        warnings.append(
            f"Low confidence ({prediction['confidence'] * 100:.1f}%). The prediction may be uncertain."
        )
    if disagreement["is_disagreement"]:
        warnings.append(
            "Model disagreement detected: "
            f"mobilenet={disagreement['mobilenet_label']} ({disagreement['mobilenet_confidence'] * 100:.1f}%), "
            f"vit={disagreement['vit_label']} ({disagreement['vit_confidence'] * 100:.1f}%)."
        )
    warnings.extend(quality["issues"])

    payload = {
        "filename": filename,
        "model": prediction["model"],
        "predicted_label": prediction["predicted_label"],
        "confidence": round(prediction["confidence"], 4),
        "advisory": advisory,
        "warnings": warnings,
        "reliability": {
            "is_uncertain": is_uncertain,
            "has_model_disagreement": disagreement["is_disagreement"],
            "has_image_quality_issues": len(quality["issues"]) > 0,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
        },
        "model_comparison": disagreement,
        "image_quality": quality,
    }

    if "top_k" in prediction:
        payload["top_k"] = [
            {"label": item["label"], "confidence": round(item["confidence"], 4)}
            for item in prediction["top_k"]
        ]

    return payload


def render_ui(
    request: Request,
    result: dict | None = None,
    error: str | None = None,
    selected_model: str = "ensemble",
    status_code: int = 200,
):
    return templates.TemplateResponse(
        "ui_predict.html",
        {
            "request": request,
            "result": result,
            "error": error,
            "selected_model": selected_model,
        },
        status_code=status_code,
    )


@app.get("/")
def root():
    return {"message": "Plant Health Advisor API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    return render_ui(request=request)


@app.get("/ui/predict", response_class=HTMLResponse)
def ui_predict_form(request: Request):
    return render_ui(request=request)


@app.post("/ui/predict", response_class=HTMLResponse)
async def ui_predict(
    request: Request,
    file: UploadFile = File(...),
    model: str = Form(default="ensemble"),
):
    selected_model = model if model in {"ensemble", "mobilenet", "vit"} else "ensemble"

    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise ValueError("Please upload a valid image file.")
        result = run_prediction(
            image_bytes=image_bytes,
            filename=file.filename or "uploaded_image",
            model=selected_model,
            top_k=5,
        )
        return render_ui(
            request=request,
            result=result,
            error=None,
            selected_model=selected_model,
        )
    except Exception as exc:
        return render_ui(
            request=request,
            result=None,
            error=f"Prediction failed. Please check the image and try again. ({exc})",
            selected_model=selected_model,
            status_code=400,
        )


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    model: str = Query(default="ensemble", pattern="^(mobilenet|vit|ensemble)$"),
    top_k: int = Query(default=0, ge=0, le=10),
):
    try:
        image_bytes = await file.read()
        payload = run_prediction(
            image_bytes=image_bytes,
            filename=file.filename or "uploaded_image",
            model=model,
            top_k=top_k,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}") from exc

    return JSONResponse(payload)
