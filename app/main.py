import os

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.inference.vision import VisionEnsemble
from app.nlp.advisor import build_advisory_response

app = FastAPI(title="Plant Health Advisor API")

# Change these class names to match your training labels exactly.
# The order must be identical to model outputs.
CLASS_NAMES = [
    "Tomato___Late_blight",
    "Tomato___healthy",
]

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


def run_prediction(image_bytes: bytes, filename: str, model: str, top_k: int = 0) -> dict:
    prediction = vision.predict(image_bytes=image_bytes, model=model, top_k=top_k)
    advisory = build_advisory_response(prediction["predicted_label"])

    payload = {
        "filename": filename,
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
