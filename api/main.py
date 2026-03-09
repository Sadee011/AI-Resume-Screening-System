# api/main.py
import sys, os, csv, datetime

# ── Path setup ──
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'ml'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import PredictRequest, PredictResponse, SkillAnalysis

from ml.preprocessing import clean_text
from ml.feature_engineering import load_vectorizer
from ml.matching import get_match_score, classify_match
from ml.skill_extractor import analyze_skills

# ── FastAPI app ──
app = FastAPI(
    title='AI Resume Screener',
    description='Match resumes to job descriptions using NLP',
    version='1.0.0'
)

# ── CORS — allow all (dev mode) ──
app.add_middleware(CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

# ── Global vectorizer ──
vectorizer = None

@app.on_event('startup')
async def startup_event():
    global vectorizer
    model_path = os.path.join(PROJECT_ROOT, 'model', 'tfidf_vectorizer.pkl')
    vectorizer = load_vectorizer(model_path)
    print(f'✅ Model loaded! Vocab: {len(vectorizer.vocabulary_)} words')


@app.get('/')
def root():
    return {'status': '✅ AI Resume Screener is running!', 'docs': '/docs'}


@app.post('/predict', response_model=PredictResponse)
def predict(req: PredictRequest):
    if len(req.resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail='Resume too short (min 50 chars)')
    if len(req.job_description.strip()) < 50:
        raise HTTPException(status_code=400, detail='Job description too short (min 50 chars)')

    score  = get_match_score(req.resume_text, req.job_description, vectorizer)
    result = classify_match(score)
    skills = analyze_skills(req.resume_text, req.job_description)

    missing = skills['missing_skills']
    if score >= 70:
        advice = 'Strong match! Your profile aligns well. Apply with confidence.'
    elif score >= 45:
        advice = ('Average match. Consider improving: ' + ', '.join(missing[:3])) if missing else 'Average match. Strengthen your skillset.'
    else:
        advice = ('Low match. Key skills to develop: ' + ', '.join(missing[:5])) if missing else 'Low match. Review the job requirements carefully.'

    _log(score, result['label'])

    return PredictResponse(
        score=score,
        label=result['label'],
        color=result['color'],
        emoji=result['emoji'],
        skills=SkillAnalysis(
            matching_skills=skills['matching_skills'],
            missing_skills=skills['missing_skills'],
            coverage_pct=skills['coverage_pct']
        ),
        advice=advice
    )


def _log(score, label):
    log_path = os.path.join(PROJECT_ROOT, 'logs', 'predictions.csv')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a', newline='') as f:
        csv.writer(f).writerow([datetime.datetime.now(), score, label])
