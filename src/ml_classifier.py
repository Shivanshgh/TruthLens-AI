from pathlib import Path
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from src.preprocessing import clean_text

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "misinfo_classifier.pkl"
DATA_PATH = BASE_DIR / "data" / "dataset.csv"

def train_and_save_model(data_path: Path = DATA_PATH):
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}. Please supply a CSV with text,label.")
    
    df = pd.read_csv(data_path)
    df = df.dropna(subset=["text", "label"])
    
    label_map = {"fake": "misinformation", "true": "reliable", "misinformation": "misinformation", "reliable": "reliable"}
    df["label"] = df["label"].str.lower().map(label_map).fillna("reliable")
    
    cleaned_texts = [clean_text(t) for t in df["text"]]
    labels = df["label"].astype(str).to_numpy()
    
    X_train, X_test, y_train, y_test = train_test_split(
        cleaned_texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "report": classification_report(y_test, y_pred, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
    }
    
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    return metrics

def load_model():
    if not MODEL_PATH.exists():
        train_and_save_model()
    return joblib.load(MODEL_PATH)

def predict_ml(text: str) -> dict:
    model = load_model()
    cleaned = clean_text(text)
    
    print("MODEL TYPE:", type(model))
    print("CLEANED TYPE:", type(cleaned))
    print("CLEANED TEXT:", cleaned)

    probs = model.predict_proba([cleaned])[0]

    print("PROBS TYPE:", type(probs))
    print("PROBS:", probs)
    classes = model.classes_
    
    prob_dict = {cls: float(prob) for cls, prob in zip(classes, probs)}
    reliable_prob = prob_dict.get("reliable", 0.5)
    misinfo_prob = prob_dict.get("misinformation", 0.5)
    
    prediction = "reliable" if reliable_prob >= misinfo_prob else "misinformation"
    confidence = max(reliable_prob, misinfo_prob)
    
    return {
        "prediction": prediction,
        "reliable_probability": round(reliable_prob, 4),
        "misinformation_probability": round(misinfo_prob, 4),
        "confidence": round(confidence, 4)
    }
