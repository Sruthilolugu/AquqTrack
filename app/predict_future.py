import pandas as pd
import joblib
import os

# Load the trained model
model_path = "/Users/sruthiuma/Documents/PrototypeSIH/models/best_model.pkl"
model = joblib.load(model_path)

# Load dataset
dataset_path = "/Users/sruthiuma/Documents/PrototypeSIH/dataset/monsoon_cleaned.csv"
df = pd.read_csv(dataset_path)
df["Date"] = pd.to_datetime(df["Date"])

def get_predictions(village, start_date, end_date):
    """
    Predict DTWL for the given village between start_date and end_date
    """
    print(f"Village selected: {village}")
    print(f"Start date: {start_date}, End date: {end_date}")
    print(f"Available villages in dataset: {df['VILLAGE'].unique()}")

    data = df[df["VILLAGE"].str.strip().str.lower() == village.strip().lower()].sort_values("Date")
    if len(data) < 2:
        print(f"No data found for village: {village}")
        return pd.DataFrame()  # Not enough data

    lag1 = data["DTWL"].iloc[-1]
    lag2 = data["DTWL"].iloc[-2]

    future_dates = pd.date_range(start=pd.to_datetime(start_date), end=pd.to_datetime(end_date), freq='M')
    predictions = []

    all_villages = [col.replace("VILLAGE_", "") for col in model.feature_names_in_ if col.startswith("VILLAGE_")]

    for date in future_dates:
        X_new = pd.DataFrame({
            "Year": [date.year],
            "Month": [date.month],
            "Lag1": [lag1],
            "Lag2": [lag2]
        })

        for v in all_villages:
            X_new[f"VILLAGE_{v}"] = 1 if v.lower() == village.strip().lower() else 0

        X_new = X_new[model.feature_names_in_]

        pred = model.predict(X_new)[0]
        predictions.append({"Date": date, "Predicted_DTWl": pred})

        lag2 = lag1
        lag1 = pred

    return pd.DataFrame(predictions)
