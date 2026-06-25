"""
Generate a comprehensive model evaluation report
Usage: python generate_report.py
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, classification_report
import mlflow

# Enable MLflow file store
os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

def load_model_and_data():
    """Load the trained model and test data"""
    model = joblib.load("artifacts/random_forest.joblib")
    
    # Load test data
    test_df = pd.read_csv("data/processed/test.csv")
    X_test = test_df.drop(columns=["state_of_health"])
    y_test = test_df["state_of_health"]
    
    return model, X_test, y_test

def calculate_metrics(y_true, y_pred):
    """Calculate regression metrics"""
    return {
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "MAE": mean_absolute_error(y_true, y_pred),
        "R²": r2_score(y_true, y_pred),
        "Min Error": float(np.min(np.abs(y_true - y_pred))),
        "Max Error": float(np.max(np.abs(y_true - y_pred))),
        "Mean Error": float(np.mean(y_true - y_pred))
    }

def get_bucket(soh):
    """Classify SOH into health buckets"""
    if soh >= 85:
        return "Healthy"
    elif soh >= 70:
        return "Moderate"
    else:
        return "End-of-Life"

def generate_report():
    """Generate comprehensive evaluation report"""
    
    print("\n" + "="*80)
    print("🔬 EV BATTERY HEALTH PREDICTION - MODEL EVALUATION REPORT")
    print("="*80)
    
    # Load model and data
    model, X_test, y_test = load_model_and_data()
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    metrics = calculate_metrics(y_test, y_pred)
    
    print("\n📊 REGRESSION METRICS (Predicting State of Health %)")
    print("-" * 80)
    for metric_name, metric_value in metrics.items():
        print(f"  {metric_name:.<30} {metric_value:.4f}")
    
    # Classification into buckets
    y_buckets_true = y_test.apply(get_bucket)
    y_buckets_pred = pd.Series(y_pred).apply(get_bucket)
    
    print("\n🎯 HEALTH BUCKET CLASSIFICATION")
    print("-" * 80)
    
    from sklearn.metrics import confusion_matrix, accuracy_score
    
    accuracy = accuracy_score(y_buckets_true, y_buckets_pred)
    print(f"  Overall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)\n")
    
    print("  Classification Report:")
    print(classification_report(y_buckets_true, y_buckets_pred))
    
    # Confusion matrix
    cm = confusion_matrix(y_buckets_true, y_buckets_pred)
    print("  Confusion Matrix:")
    print("  " + "\t".join(["True \\ Pred", "EOL", "Healthy", "Moderate"]))
    labels = ["EOL", "Healthy", "Moderate"]
    for i, label in enumerate(labels):
        print(f"  {label:.<12}" + "\t".join(str(x) for x in cm[i]))
    
    # Feature importance
    print("\n🎚️  FEATURE IMPORTANCE (Top 10)")
    print("-" * 80)
    
    feature_names = X_test.columns.tolist()
    feature_importance = model.feature_importances_
    
    importance_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": feature_importance
    }).sort_values("Importance", ascending=False)
    
    for idx, row in importance_df.head(10).iterrows():
        bar = "█" * int(row["Importance"] * 100)
        print(f"  {row['Feature']:.<30} {bar} {row['Importance']:.4f}")
    
    # Prediction distribution
    print("\n📈 PREDICTION DISTRIBUTION")
    print("-" * 80)
    print(f"  Predictions Range: {y_pred.min():.2f}% - {y_pred.max():.2f}%")
    print(f"  Mean Prediction: {y_pred.mean():.2f}%")
    print(f"  Std Dev: {y_pred.std():.2f}%")
    
    # Bucket distribution
    bucket_dist = y_buckets_pred.value_counts()
    print(f"\n  Bucket Distribution:")
    for bucket in ["End-of-Life", "Moderate", "Healthy"]:
        count = bucket_dist.get(bucket, 0)
        pct = count / len(y_pred) * 100
        bar = "█" * int(pct / 5)
        print(f"    {bucket:.<15} {count:>4} ({pct:>5.1f}%) {bar}")
    
    # Error analysis
    errors = np.abs(y_test - y_pred)
    print(f"\n📉 ERROR ANALYSIS")
    print("-" * 80)
    print(f"  Mean Absolute Error: {errors.mean():.4f}%")
    print(f"  Median Absolute Error: {np.median(errors):.4f}%")
    print(f"  95th Percentile Error: {np.percentile(errors, 95):.4f}%")
    print(f"  99th Percentile Error: {np.percentile(errors, 99):.4f}%")
    
    # Get latest MLflow run info
    print("\n🔗 MLFLOW TRACKING")
    print("-" * 80)
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    from mlflow.tracking import MlflowClient
    client = MlflowClient(tracking_uri="sqlite:///mlflow.db")
    
    experiments = client.search_experiments()
    for exp in experiments:
        if exp.name == "ev-battery-soh":
            runs = client.search_runs(experiment_ids=[exp.experiment_id])
            if runs:
                latest_run = runs[0]
                print(f"  Latest Run ID: {latest_run.info.run_id}")
                print(f"  Status: {latest_run.info.status}")
                print(f"  Tracked Metrics:")
                for metric_name, metric_value in latest_run.data.metrics.items():
                    print(f"    - {metric_name}: {metric_value:.4f}")
    
    # Summary
    print("\n" + "="*80)
    print("✅ MODEL PERFORMANCE SUMMARY")
    print("="*80)
    print(f"  Model Type: Random Forest Regressor")
    print(f"  Test Samples: {len(y_test)}")
    print(f"  R² Score: {metrics['R²']:.4f} (explains {metrics['R²']*100:.2f}% of variance)")
    print(f"  RMSE: {metrics['RMSE']:.4f}%")
    print(f"  Classification Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Save report as JSON
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "model_type": "Random Forest Regressor",
        "test_samples": len(y_test),
        "regression_metrics": metrics,
        "classification_accuracy": float(accuracy),
        "top_features": importance_df.head(10).to_dict('records'),
        "prediction_range": [float(y_pred.min()), float(y_pred.max())],
        "bucket_distribution": bucket_dist.to_dict()
    }
    
    with open("model_evaluation_report.json", "w") as f:
        json.dump(report_data, f, indent=2)
    
    print("📄 Report saved to: model_evaluation_report.json\n")

if __name__ == "__main__":
    generate_report()
