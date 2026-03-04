import pandas as pd

# IT categories list
IT_CATEGORIES = [
    'Data Science',
    'Web Designing',
    'Java Developer',
    'Python Developer',
    'SAP Developer',
    'Automation Testing',
    'DevOps Engineer',
    'Network Security Engineer',
    'Database',
    'Hadoop',
    'ETL Developer',
    'DotNet Developer',
    'Blockchain',
    'Testing',
    'Business Analyst'
]

def filter_it_resumes(
        input_path='../data/resumes.csv',
        output_path='../data/processed/resumes_it_only.csv'):

    # Load dataset
    df = pd.read_csv(input_path)
    print(f"Original resumes: {len(df)}")

    # Filter by Category
    df_it = df[df['Category'].isin(IT_CATEGORIES)].copy()

    print(f"IT resumes only: {len(df_it)}")

    # Save filtered file
    df_it.to_csv(output_path, index=False)

    print(f"Filtered file saved at: {output_path}")


if __name__ == '__main__':
    filter_it_resumes()