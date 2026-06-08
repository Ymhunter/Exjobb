from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from app.database import SessionLocal, Menu

# Generic training data for Intent Classification
training_texts = [
    "I want to order food", "Can I get a meal?", "One order please", # Intent: order
    "Does this have onions?", "Is it gluten free?", "Allergies?", # Intent: question
    "How much does it cost?", "What is the price?", # Intent: price
    "What do you recommend?", "What should I eat?", "Any suggestions?" # Intent: recommendation
]
training_labels = ["order", "order", "order", "question", "question", "question", "price", "price", "recommendation", "recommendation", "recommendation"]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(training_texts)
clf = LogisticRegression()
clf.fit(X, training_labels)

def classify_intent(text: str) -> str:
    vec = vectorizer.transform([text])
    return clf.predict(vec)[0]

def recommend_dishes(preference: str, top_n: int = 3):
    db = SessionLocal()
    menu_items = db.query(Menu).all()
    db.close()
    
    if not menu_items:
        return []
    
    # Content-based recommendation
    descriptions = [item.description + " " + item.name for item in menu_items]
    rec_vectorizer = TfidfVectorizer()
    menu_matrix = rec_vectorizer.fit_transform(descriptions)
    
    pref_vec = rec_vectorizer.transform([preference])
    similarities = cosine_similarity(pref_vec, menu_matrix).flatten()
    
    # Get top_n indices sorted by highest similarity
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    results = []
    for i in top_indices:
        if similarities[i] > 0: # Only if there is some match
            results.append(menu_items[i])
            
    # Fallback to general items if no match
    if not results:
        results = menu_items[:top_n]
        
    return [{"name": item.name, "description": item.description, "price": item.price} for item in results]
