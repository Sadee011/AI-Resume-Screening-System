import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.preprocessing import clean_text           
from ml.feature_engineering import load_vectorizer
from ml.matching import get_match_score, classify_match, batch_match 
from ml.skill_extractor import analyze_skills      
import pandas as pd

print('=' * 50)
print('WEEK 1 INTEGRATION TEST')
print('=' * 50)


BASE = os.path.dirname(os.path.abspath(__file__))

# 1. Load vectorizer
print('Loading vectorizer...')
vec = load_vectorizer(os.path.join(BASE, 'model', 'tfidf_vectorizer.pkl'))
print('OK')

# 2. Load jobs
df_jobs = pd.read_csv(os.path.join(BASE, 'data', 'processed', 'jobs_clean.csv'))
print(f'Jobs loaded: {len(df_jobs)}')

# 3. Sample resume
test_resume = '''
Experienced Data Scientist with 4 years of professional experience.
Proficient in Python, machine learning, and data analysis.
Skills: pandas, numpy, scikit-learn, TensorFlow, SQL.
Built recommendation systems and NLP models.
'''

# 4. Match test
first_job = df_jobs['description'][0]
score = get_match_score(test_resume, first_job, vec)
match = classify_match(score)

print(f'\nMatch Score: {score}% {match["emoji"]} {match["label"]}')

# 5. Skill analysis
skills = analyze_skills(test_resume, first_job)

print(f'Matching skills: {skills["matching_skills"]}')
print(f'Missing skills:  {skills["missing_skills"]}')

# 6. Top 3 jobs
top = batch_match(test_resume, df_jobs, vec, top_n=3)

print('\nTop 3 Matching Jobs:')
for i, j in enumerate(top, 1):
    print(f'  {i}. {j["company"]} | {j["job_title"]} | {j["score"]}%')

print('\nWeek 1 DONE!')