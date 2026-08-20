"""
model_service.py — تحميل الموديل التقليدي (TF-IDF + OneVsRestClassifier SVM)
وتوفير دالة تنبؤ multi-label، بنفس منطق route_complaint من النوتبوك بالضبط.
"""
import os
import joblib
import numpy as np
from scipy.special import expit

from .text_normalize import normalize_arabic

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
DECISION_THRESHOLD = 0.5  # نفس القيمة المعتمدة بـ contract.json (معايرة على val فقط)


class ComplaintRouter:
    def __init__(self):
        self.pipe = joblib.load(os.path.join(MODEL_DIR, "damgov_router_multilabel_svm.joblib"))
        self.mlb = joblib.load(os.path.join(MODEL_DIR, "damgov_label_binarizer.joblib"))
        self.classes = list(self.mlb.classes_)

    def sigmoid_scores(self, texts):
        """نفس sigmoid_scores من النوتبوك: expit(decision_function) —
        مسافة موقّعة محوّلة لـ[0,1]، مش احتمال معايَر إحصائياً."""
        return expit(self.pipe.decision_function(texts))

    def route(self, text: str, threshold: float = DECISION_THRESHOLD) -> dict:
        cleaned = normalize_arabic(text)
        scores = self.sigmoid_scores([cleaned])[0]
        order = np.argsort(-scores)
        hits = [(self.classes[i], float(scores[i])) for i in order if scores[i] >= threshold]

        if not hits:
            top_i = int(order[0])
            return {
                "departments": [],
                "confidences": {},
                "action": "human_review",
                "top_guess": self.classes[top_i],
                "top_guess_confidence": round(float(scores[top_i]), 3),
            }
        return {
            "departments": [d for d, _ in hits],
            "confidences": {d: round(s, 3) for d, s in hits},
            "action": "auto_route",
        }

    def route_batch(self, texts: list[str], threshold: float = DECISION_THRESHOLD) -> list[dict]:
        return [self.route(t, threshold) for t in texts]


# نسخة وحدة تُحمَّل مرة واحدة عند إقلاع الخدمة (joblib.load بطيء نسبياً)
router = ComplaintRouter()