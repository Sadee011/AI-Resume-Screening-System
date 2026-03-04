# ==========================================================
# preprocessing.py
# All data cleaning + NLP preprocessing functions
# ==========================================================

import os
import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# nltk.download('stopwords')
# nltk.download('wordnet')


# ----------------------------------------------------------
# Global NLP objects
# ----------------------------------------------------------
lemmatizer = WordNetLemmatizer()
STOP_WORDS = set(stopwords.words('english'))


# ==========================================================
# JOB DATASET CLEANING
# ==========================================================
def clean_jobs(input_path, output_path):

    # Load CSV
    df = pd.read_csv(input_path)
    print(f'Jobs loaded: {df.shape}')

    # Keep useful columns only
    cols = [
        'company',
        'rating',
        'location',
        'positionName',
        'description',
        'salary',
        'jobType/0'
    ]
    df = df[cols]

    # Rename columns
    df = df.rename(columns={
        'positionName': 'job_title',
        'jobType/0': 'job_type'
    })

    # Fill missing values (don't delete data)
    df['salary'] = df['salary'].fillna('Not Specified')
    df['job_type'] = df['job_type'].fillna('Full-time')

    # Create output folder if not exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save cleaned CSV
    df.to_csv(output_path, index=False)
    print(f'Jobs clean saved: {len(df)} rows → {output_path}')

    return df


# ==========================================================
# RESUME DATASET CLEANING
# ==========================================================
def clean_resumes(input_path, output_path):

    df = pd.read_csv(input_path)
    print(f'Resumes loaded: {df.shape}')

    # Lowercase column names
    df.columns = [c.lower() for c in df.columns]

    # Remove empty resumes
    df = df.dropna(subset=['resume'])

    # Remove very short resumes
    df = df[df['resume'].str.len() > 50]

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f'Resumes clean saved: {len(df)} rows → {output_path}')

    return df


# ==========================================================
# NLP TEXT CLEANING FUNCTION
# ==========================================================
def clean_text(text):

    # Safety check
    if not isinstance(text, str):
        return ''

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)

    # Step 3: Keep letters + spaces only
    text = re.sub(r'[^a-z\s]', ' ', text)

    # Step 4: Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Step 5: Remove stopwords
    words = text.split()
    words = [
        w for w in words
        if w not in STOP_WORDS and len(w) > 2
    ]

    # Step 6: Lemmatization
    words = [lemmatizer.lemmatize(w) for w in words]

    return ' '.join(words)


# ==========================================================
# RUN FILE DIRECTLY (Testing)
# ==========================================================
if __name__ == '__main__':

    print("Testing NLP clean_text()...\n")

    test = 'Python Developer!! 5+ years experience. Required skills: ML, AI'
    print('Before:', test)
    print('After :', clean_text(test))

    print("\nTesting dataset cleaning (if files exist)...")

    try:
        clean_jobs(
            '../data/jobs_dataset.csv',
            '../data/processed/jobs_clean.csv'
        )

        clean_resumes(
            '../data/resumes.csv',
            '../data/processed/resumes_clean.csv'
        )

        print("\nBoth datasets cleaned successfully!")

    except Exception as e:
        print("Dataset files not found. Skipping dataset cleaning test.")
        print("Error:", e)