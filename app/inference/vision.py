import io
from typing import Literal

import keras
import numpy as np
from PIL import Image

from app.inference.vit_layers import VIT_CUSTOM_OBJECTS
from keras.applications.mobilenet_v2 import preprocess_input


class VisionEnsemble:
    def __init__(self, mobilenet_path: str, vit_path: str, class_names: list[str]):
        self.class_names = class_names

        self.mobilenet = keras.models.load_model(mobilenet_path, compile=False)
        self.vit = keras.models.load_model(
            vit_path,
            custom_objects=VIT_CUSTOM_OBJECTS,
            compile=False,
        )

        self.mobilenet_num_classes = self._infer_num_classes(self.mobilenet, "mobilenet")
        self.vit_num_classes = self._infer_num_classes(self.vit, "vit")

        if self.mobilenet_num_classes != self.vit_num_classes:
            raise ValueError(
                "Model output mismatch: "
                f"mobilenet has {self.mobilenet_num_classes} classes, "
                f"vit has {self.vit_num_classes} classes."
            )

        if len(self.class_names) != self.mobilenet_num_classes:
            raise ValueError(
                "CLASS_NAMES length does not match model output classes. "
                f"CLASS_NAMES={len(self.class_names)}, model_classes={self.mobilenet_num_classes}. "
                "Update CLASS_NAMES to exactly match your training label order."
            )

    def _infer_num_classes(self, model, model_name: str) -> int:
        output_shape = model.output_shape
        if isinstance(output_shape, list):
            raise ValueError(f"{model_name} has multiple outputs; expected a single classification head.")

        num_classes = output_shape[-1]
        if not isinstance(num_classes, int) or num_classes <= 1:
            raise ValueError(f"{model_name} output shape is invalid for classification: {output_shape}")

        return num_classes

    def _to_probabilities(self, scores: np.ndarray) -> np.ndarray:
        probs = np.asarray(scores, dtype=np.float32).reshape(-1)
        total = float(np.sum(probs))

        if np.any(probs < 0.0) or total <= 0.0 or not np.isclose(total, 1.0, atol=1e-3):
            shifted = probs - np.max(probs)
            exp_scores = np.exp(shifted)
            probs = exp_scores / np.sum(exp_scores)

        return probs

    def _load_image(self, image_bytes: bytes, size=(224, 224)) -> np.ndarray:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize(size)
        arr = np.array(img, dtype=np.float32)
        return np.expand_dims(arr, axis=0)

    def _predict_mobilenet(self, image_batch: np.ndarray) -> np.ndarray:
        mobilenet_input = preprocess_input(image_batch.copy())
        scores = self.mobilenet.predict(mobilenet_input, verbose=0)[0]
        return self._to_probabilities(scores)

    def _predict_vit(self, image_batch: np.ndarray) -> np.ndarray:
        vit_input = image_batch / 255.0
        scores = self.vit.predict(vit_input, verbose=0)[0]
        return self._to_probabilities(scores)

    def _label_for_index(self, index: int) -> str:
        if not 0 <= index < len(self.class_names):
            raise IndexError(
                f"Predicted class index {index} is out of range for CLASS_NAMES length {len(self.class_names)}."
            )
        return self.class_names[index]

    def predict(
        self,
        image_bytes: bytes,
        model: Literal["mobilenet", "vit", "ensemble"] = "ensemble",
        top_k: int = 0,
    ) -> dict:
        x = self._load_image(image_bytes)

        if model == "mobilenet":
            probs = self._predict_mobilenet(x)
        elif model == "vit":
            probs = self._predict_vit(x)
        elif model == "ensemble":
            pm = self._predict_mobilenet(x)
            pv = self._predict_vit(x)
            if pm.shape != pv.shape:
                raise ValueError(f"Model probability shape mismatch: mobilenet={pm.shape}, vit={pv.shape}")
            probs = (pm + pv) / 2.0
            probs = probs / np.sum(probs)
        else:
            raise ValueError("model must be one of: mobilenet, vit, ensemble")

        top_index = int(np.argmax(probs))
        result = {
            "model": model,
            "predicted_label": self._label_for_index(top_index),
            "confidence": float(probs[top_index]),
        }

        if top_k > 0:
            k = min(top_k, probs.size)
            top_indices = np.argsort(probs)[::-1][:k]
            result["top_k"] = [
                {"label": self._label_for_index(int(i)), "confidence": float(probs[int(i)])}
                for i in top_indices
            ]

        return result
