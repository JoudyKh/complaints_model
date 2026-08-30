# Damascus Complaint Router API

API لتصنيف شكاوى محافظة دمشق إلى مديرية واحدة أو أكثر (multi-label)،
مبني فوق الموديل الكلاسيكي (TF-IDF char + OneVsRestClassifier LinearSVC).

## التشغيل المحلي
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
التوثيق التفاعلي: http://localhost:8000/docs

## Endpoints

### `GET /health`
فحص إنه الخدمة شغالة وعدد الأقسام المحمّلة.

### `GET /departments`
قائمة كل المديريات (34، فضاء التسميات الكامل).

### `POST /classify`
```json
{"text": "الحاوية مكسورة والقمامة مكدسة على الرصيف من اسبوع"}
```
الرد:
```json
{
  "departments": ["مديرية النظافة", "مديرية الصيانة و الإنارة"],
  "confidences": {"مديرية النظافة": 0.789, "مديرية الصيانة و الإنارة": 0.573},
  "action": "auto_route",
  "top_guess": null,
  "top_guess_confidence": null
}
```
لو ولا قسم عدّى العتبة، `action="human_review"` و`departments=[]`، مع `top_guess` كمؤشر للمراجعة اليدوية.

### `POST /classify_batch`
نفس الشي لعدة نصوص دفعة وحدة (`{"texts": [...]}`، حد أقصى 200). يمكن تمرير
`threshold` اختياريًا لتطبيق نفس العتبة على كل النصوص.

## ⚠️ ملاحظات مهمة قبل النشر الفعلي

1. **إصدار scikit-learn مثبَّت بدقة (1.6.1) بـ requirements.txt** ليطابق نسخة
   التدريب بالضبط — لا تغيّريه بدون إعادة اختبار كامل؛ تحذير عدم توافق النسخ
   قد يعني نتائج مختلفة بصمت.
2. **لا يوجد PII scrubbing بهالنسخة (قرار صريح من مالكة المشروع)** — النص
   الخام (بما فيه أي اسم أو رقم هوية مذكور بالشكوى) بيدخل ويترجع كما هو،
   بدون إخفاء. أي تخزين أو عرض لاحق لنتائج هالـ API رح يحمل نفس هالمعلومات.
3. **لُوحظ أثناء الاختبار:** نص عشوائي بلا معنى رجّع تصنيف بثقة متوسطة بدل
   `human_review` — العتبة 0.5 ما بتلتقط كل حالات الغموض. يستاهل مراجعة لاحقاً
   (رفع العتبة أو إضافة كشف out-of-distribution) قبل الاعتماد الكامل بالإنتاج.
4. **CORS مفتوح (`allow_origins=["*"]`)** — قيّديه لدومين الواجهة الفعلي قبل الإنتاج.

## هيكلية المشروع
```
app/
  main.py            FastAPI endpoints
  model_service.py   تحميل الموديل + منطق التنبؤ (route_complaint)
  text_normalize.py  نفس دالة normalize_arabic من النوتبوك بالضبط
  model/
    damgov_router_multilabel_svm.joblib
    damgov_label_binarizer.joblib
requirements.txt
```
