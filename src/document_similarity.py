import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_top_similar_docs(uploaded_text, csv_path='src/product_descriptions.csv', top_n=10):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    if 'Product' not in df.columns or 'Description' not in df.columns:
        raise ValueError("CSV must contain 'Product' and 'Description' columns.")

    df = df.dropna(subset=['Description'])
    descriptions = df['Description'].astype(str).tolist()

    if not descriptions:
        raise ValueError("No valid descriptions found in the CSV file.")

    docs = [uploaded_text] + descriptions
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(docs)
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    top_indices = similarity_scores.argsort()[::-1][:top_n]

    results = []
    for idx in top_indices:
        score = similarity_scores[idx]
        row = df.iloc[idx]
        product = str(row['Product']).strip()
        snippet = str(row['Description'])[:300].replace('\n', ' ')
        results.append({
            'filename': f"{product} (Row {idx + 1})",
            'score': float(score),
            'snippet': snippet
        })

    return results
