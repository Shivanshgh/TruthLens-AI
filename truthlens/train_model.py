from src.ml_classifier import train_and_save_model

if __name__ == "__main__":
    print("Training ML Classifier on dataset...")
    metrics = train_and_save_model()
    print("Training complete!")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print("Model saved to models/misinfo_classifier.pkl")