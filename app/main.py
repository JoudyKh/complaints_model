"""
main.py — API تصنيف شكاوى محافظة دمشق (multi-label).

تشغيل محلي:
    uvicorn app.main:app --reload --port 8000

التوثيق التفاعلي (Swagger) بيصير جاهز تلقائياً على:
    http://localhost:8000/docs
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .model_service import router as model_router

app = FastAPI(
    title="Damascus Complaint Router API",
    description="تصنيف شكاوى محافظة دمشق إلى مديرية واحدة أو أكثر (multi-label)",
    version="1.0.0",
)

# CORS مفتوح مؤقتاً للتطوير — قيّديه لدومين الواجهة الفعلي قبل الإنتاج
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, description="نص الشكوى الخام")
    threshold: float | None = Field(None, ge=0.0, le=1.0, description="عتبة اختيارية تُلغي الافتراضية (0.5)")


class ClassifyResponse(BaseModel):
    departments: list[str]
    confidences: dict[str, float]
    action: str  # "auto_route" | "human_review"
    top_guess: str | None = None
    top_guess_confidence: float | None = None


class BatchClassifyRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=200)


@app.get("/health")
def health():
    return {"status": "ok", "n_departments": len(model_router.classes)}


@app.get("/departments")
def list_departments():
    """قائمة كل المديريات (فضاء التسميات الكامل، 34 مديرية) — لبناء واجهة الاختيار اليدوي."""
    return {"departments": model_router.classes}


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="نص الشكوى فاضي")

    threshold = req.threshold if req.threshold is not None else 0.5
    result = model_router.route(req.text, threshold=threshold)
    return result


@app.post("/classify_batch")
def classify_batch(req: BatchClassifyRequest):
    results = []
    for text in req.texts:
        if not text.strip():
            results.append({"error": "نص فاضي"})
            continue
        r = model_router.route(text)
        results.append(r)
    return {"results": results}
