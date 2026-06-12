from fifa_predictor.models.train import train_models


if __name__ == "__main__":
    artifacts = train_models()
    print(f"Best classifier: {artifacts.metrics['best_classifier']}")
    print(f"Metrics written to models/metrics.json")
