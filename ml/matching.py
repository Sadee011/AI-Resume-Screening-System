import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import clean_text
 
 
def load_vectorizer(path='../model/tfidf_vectorizer.pkl'):
    with open(path, 'rb') as f:
        return pickle.load(f)
 
 
def get_match_score(resume_text, job_description, vectorizer):
    """
    Resume + Job description → Match percentage (0–100)
 
    Steps:
    1. Both texts clean karannawa
    2. Both texts vectors ekak convert karannawa
    3. Cosine similarity calculate karannawa
    4. Percentage convert karannawa
    """
    # Step 1: Clean
    resume_clean = clean_text(resume_text)
    job_clean    = clean_text(job_description)
 
    # Step 2: Vector convert
    resume_vec = vectorizer.transform([resume_clean])
    job_vec    = vectorizer.transform([job_clean])
 
    # Step 3: Similarity (0.0 to 1.0)
    similarity = cosine_similarity(resume_vec, job_vec)[0][0]
 
    # Step 4: Percentage (0 to 100)
    score = round(float(similarity) * 100, 2)
    return score
 
 
def classify_match(score):
    """
    Score → Human readable label + color
    Used in frontend visualization
    """
    if score >= 70:
        return {'label': 'STRONG MATCH',  'color': '#22c55e', 'emoji': '🟢'}
    elif score >= 45:
        return {'label': 'AVERAGE MATCH', 'color': '#f59e0b', 'emoji': '🟡'}
    else:
        return {'label': 'WEAK MATCH',    'color': '#ef4444', 'emoji': '🔴'}
 
 
def batch_match(resume_text, df_jobs, vectorizer, top_n=5):
    """
    One resume → All jobs eke match karannawa
    Top N best matching jobs return karannawa
    """
    scores = []
    for _, row in df_jobs.iterrows():
        score = get_match_score(resume_text, row['description'], vectorizer)
        scores.append({
            'company':   row['company'],
            'job_title': row['job_title'],
            'score':     score,
            'label':     classify_match(score)['label']
        })
 
    # Sort by score descending
    scores.sort(key=lambda x: x['score'], reverse=True)
    return scores[:top_n]
 
 
# ── TEST ──
if __name__ == '__main__':
    import pandas as pd
    vec = load_vectorizer()
    df_jobs = pd.read_csv('../data/processed/jobs_clean.csv')
 
    sample_resume = '''
    Python developer with 3 years experience.
    Expert in machine learning, pandas, scikit-learn.
    Built classification models, NLP pipelines.
    Experience with data analysis and visualization.
    '''
 
    # Single job match
    sample_job = df_jobs['description'][0]
    score = get_match_score(sample_resume, sample_job, vec)
    result = classify_match(score)
    print(f'Match Score: {score}% → {result["label"]} {result["emoji"]}')
 
    # Top 5 jobs for this resume
    print('\nTop 5 matching jobs:')
    top_jobs = batch_match(sample_resume, df_jobs, vec, top_n=5)
    for i, job in enumerate(top_jobs, 1):
        print(f'{i}. {job["company"]} - {job["job_title"]}: {job["score"]}%')

