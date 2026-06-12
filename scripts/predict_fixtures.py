from fifa_predictor.models.predict import predict_fixtures


if __name__ == "__main__":
    predictions = predict_fixtures()
    print(predictions[["match_number", "home_team", "away_team", "predicted_winner", "predicted_score", "confidence"]].head(12).to_string(index=False))
