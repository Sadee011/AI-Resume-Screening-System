import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from preprocessing import clean_text   # me file eka thiyenna ona

def train_and_save_vectorizer(
        resume_path='../data/processed/resumes_clean.csv',
        jobs_path='../data/processed/jobs_clean.csv',
        save_path='../model/tfidf_vectorizer.pkl'):


    # Load datasets
    df_res = pd.read_csv(resume_path)
    df_job = pd.read_csv(jobs_path)

    print(f'Resumes: {len(df_res)}, Jobs: {len(df_job)}')

    # Clean text
    print('Cleaning text...')
    resume_texts = df_res['resume'].apply(clean_text).tolist()
    job_texts = df_job['description'].apply(clean_text).tolist()

    # Combine texts
    all_texts = resume_texts + job_texts
    print(f'Total documents: {len(all_texts)}')

    # Create TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        max_features=8000,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True
    )

    # Train (fit)
    vectorizer.fit(all_texts)

    print(f'Vocabulary size: {len(vectorizer.vocabulary_)} words')

    # Save model
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, 'wb') as f:
        pickle.dump(vectorizer, f)

    print(f'Vectorizer saved at: {save_path}')

    return vectorizer


def load_vectorizer(path='../model/tfidf_vectorizer.pkl'):
    with open(path, 'rb') as f:
        return pickle.load(f)


def text_to_vector(text, vectorizer):
    clean = clean_text(text)
    return vectorizer.transform([clean])


if __name__ == '__main__':
    vec = train_and_save_vectorizer()

    # Show sample vocabulary
    terms = list(vec.vocabulary_.keys())[:20]
    print('Sample vocab:', terms)