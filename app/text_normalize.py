"""
نفس دالة normalize_arabic بالضبط من النوتبوك (خلية §4) — لازم تطابق تماماً
النص يلي تدرّب عليه الموديل، وإلا صار في train/serve skew.
"""
import re
import unicodedata

ARABIC_DIACRITICS = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u0640]')
TATWEEL = '\u0640'
REPEATED_CHAR = re.compile(r'(.)\1{2,}')
ALEF_VARIANTS = re.compile(r'[إأآا]')
YEH_VARIANTS = re.compile(r'ى')
HAMZA_ON_WAW_YEH = re.compile(r'[ؤئ]')
ARABIC_INDIC_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
PUNCT_RE = re.compile(r'[\.\,\!\?\;\:\-\_\(\)\[\]\{\}\"\'\/\\\|\+\=\*\&\^\%\$\#\@\~\`٪،؛؟…“”‘’«»]')
MULTISPACE = re.compile(r'\s+')


def normalize_arabic(text, remove_diacritics=True, normalize_alef=True, normalize_yeh=True,
                      normalize_hamza=True, collapse_repeats=True,
                      remove_punctuation=True, normalize_digits=True):
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    text = unicodedata.normalize('NFKC', text)
    text = ARABIC_DIACRITICS.sub('', text) if remove_diacritics else text.replace(TATWEEL, '')
    if normalize_alef: text = ALEF_VARIANTS.sub('ا', text)
    if normalize_yeh: text = YEH_VARIANTS.sub('ي', text)
    if normalize_hamza: text = HAMZA_ON_WAW_YEH.sub('ء', text)
    if collapse_repeats: text = REPEATED_CHAR.sub(r'\1\1', text)
    if normalize_digits: text = text.translate(ARABIC_INDIC_DIGITS)
    if remove_punctuation: text = PUNCT_RE.sub(' ', text)
    text = MULTISPACE.sub(' ', text).strip()
    return text