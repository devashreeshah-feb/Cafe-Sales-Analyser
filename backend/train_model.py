import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    
    # Handle missing dates by imputing with mode or median date, but PRD says "Date imputation using median month"
    # Actually, let's just drop or impute dates carefully
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    median_date = df['transaction_date'].median()
    df['transaction_date'] = df['transaction_date'].fillna(median_date)
    
    df['month'] = df['transaction_date'].dt.month
    df['day_of_week'] = df['transaction_date'].dt.dayofweek
    
    # Handle categorical missing values
    df['item'] = df['item'].fillna('UNKNOWN')
    df['location'] = df['location'].fillna('UNKNOWN')
    df['payment_method'] = df['payment_method'].fillna('UNKNOWN')
    
    # Encode categorical features
    le_item = LabelEncoder()
    le_location = LabelEncoder()
    le_payment = LabelEncoder()
    
    df['item_encoded'] = le_item.fit_transform(df['item'].astype(str))
    df['location_encoded'] = le_location.fit_transform(df['location'].astype(str))
    df['payment_encoded'] = le_payment.fit_transform(df['payment_method'].astype(str))
    
    # Save encoders
    joblib.dump(le_item, 'le_item.joblib')
    joblib.dump(le_location, 'le_location.joblib')
    joblib.dump(le_payment, 'le_payment.joblib')
    
    # Feature list
    features = ['quantity', 'price_per_unit', 'item_encoded', 'location_encoded', 'payment_encoded', 'month', 'day_of_week']
    X = df[features]
    y = df['total_spent']
    
    return X, y, df

def train_model():
    print("Loading data...")
    file_path = 'cleaned_cafe_sales.csv'
    X, y, df = load_and_preprocess_data(file_path)
    
    print("Splitting data...")
    # Stratified split by month (as per PRD)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=X['month']
    )
    
    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    print("Evaluating model...")
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    # Calculate MAE
    predictions = model.predict(X_test)
    mae = np.mean(np.abs(predictions - y_test))
    
    print(f"Train R2: {train_score:.4f}")
    print(f"Test R2: {test_score:.4f}")
    print(f"Test MAE: {mae:.4f}")
    
    # Calculate anomaly score (tertiary PRD output)
    all_predictions = model.predict(X)
    df['predicted_spent'] = all_predictions
    df['residual'] = np.abs(df['total_spent'] - df['predicted_spent'])
    sigma = df['residual'].std()
    df['is_anomaly'] = df['residual'] > (2 * sigma) if sigma > 0 else df['residual'] > 0.01
    
    df.to_csv('processed_sales_data.csv', index=False)
    
    print("Saving model...")
    joblib.dump(model, 'rf_model.joblib')
    print("Training complete.")

if __name__ == '__main__':
    train_model()
