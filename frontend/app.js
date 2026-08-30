const API_BASE = window.API_BASE_URL || window.location.origin;
const form = document.querySelector('#classifyForm');
const textInput = document.querySelector('#complaintText');
const threshold = document.querySelector('#threshold');
const thresholdValue = document.querySelector('#thresholdValue');
const characterCount = document.querySelector('#characterCount');
const button = document.querySelector('#classifyButton');
const resultPanel = document.querySelector('#resultPanel');
const serviceStatus = document.querySelector('#serviceStatus');
const departmentsList = document.querySelector('#departmentsList');
const departmentCount = document.querySelector('#departmentCount');

threshold.addEventListener('input', () => { thresholdValue.value = Number(threshold.value).toFixed(2); thresholdValue.textContent = thresholdValue.value; });
textInput.addEventListener('input', () => { characterCount.textContent = `${textInput.value.length} / 2000`; });

function setStatus(online, message) {
  serviceStatus.className = `service-status ${online ? 'online' : 'offline'}`;
  serviceStatus.querySelector('span:last-child').textContent = message;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (char) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char]));
}

function renderResult(data) {
  const isReview = data.action === 'human_review';
  const departments = (data.departments || []).map((name) => {
    const score = Number(data.confidences?.[name] || 0);
    return `<div class="department-result"><div class="department-name">${escapeHtml(name)}</div><div class="confidence-row"><div class="bar"><span style="width:${Math.round(score * 100)}%"></span></div><span class="confidence">${Math.round(score * 100)}%</span></div></div>`;
  }).join('');
  resultPanel.className = 'result-panel';
  resultPanel.innerHTML = `<div class="result-header"><div><p class="result-label">نتيجة التحليل</p><h2>${isReview ? 'تحتاج إلى مراجعة' : 'الجهة المقترحة'}</h2></div><span class="action-badge ${isReview ? 'review' : ''}">${isReview ? 'مراجعة بشرية' : 'توجيه تلقائي'}</span></div>${departments || `<div class="review-note">لم تتجاوز أي مديرية عتبة الثقة المحددة. يفضل مراجعة الشكوى يدويًا.</div>`}${data.top_guess ? `<p class="top-guess">الترشيح الأقرب: <strong>${escapeHtml(data.top_guess)}</strong> (${Math.round(Number(data.top_guess_confidence || 0) * 100)}%)</p>` : ''}`;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = textInput.value.trim();
  if (!text) return;
  button.disabled = true;
  button.querySelector('span:first-child').textContent = 'جارٍ التحليل...';
  try {
    const response = await fetch(`${API_BASE}/classify`, { method:'POST', headers:{ 'Content-Type':'application/json' }, body:JSON.stringify({ text, threshold:Number(threshold.value) }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'تعذر تحليل الشكوى');
    renderResult(data); setStatus(true, 'الخدمة متصلة');
  } catch (error) {
    resultPanel.className = 'result-panel';
    resultPanel.innerHTML = `<div class="result-empty"><span class="empty-icon">!</span><h2>تعذر الاتصال</h2><p>${escapeHtml(error.message)}<br>تأكد من تشغيل FastAPI على المنفذ 8000.</p></div>`;
    setStatus(false, 'الخدمة غير متاحة');
  } finally { button.disabled = false; button.querySelector('span:first-child').textContent = 'تصنيف الشكوى'; }
});

async function loadDepartments() {
  try {
    const response = await fetch(`${API_BASE}/departments`);
    if (!response.ok) throw new Error('تعذر تحميل المديريات');
    const data = await response.json();
    departmentCount.textContent = `${data.departments.length} مديرية`;
    departmentsList.innerHTML = data.departments.map((name) => `<span class="department-chip">${escapeHtml(name)}</span>`).join('');
    setStatus(true, 'الخدمة متصلة');
  } catch { departmentsList.innerHTML = '<span class="loading-line">تعذر تحميل الدليل من الخدمة.</span>'; setStatus(false, 'الخدمة غير متاحة'); }
}

loadDepartments();
