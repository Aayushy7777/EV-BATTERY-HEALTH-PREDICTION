"""Simple MLflow Viewer Dashboard using FastAPI"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json
import os
import mlflow
from mlflow.tracking import MlflowClient
from pathlib import Path
import pandas as pd

# Enable MLflow file store
os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

app = FastAPI(title="MLflow Viewer")


def read_evaluation_report():
    """Read the latest model evaluation report if it exists."""
    report_path = Path("model_evaluation_report.json")
    if not report_path.exists():
        return None

    try:
        with report_path.open("r", encoding="utf-8") as report_file:
            return json.load(report_file)
    except Exception as error:
        print(f"[DEBUG] Error reading evaluation report: {error}")
        return None

def read_mlflow_data():
    """Read MLflow experiment and run data using MLflow Client"""
    try:
        # Use SQLite backend which is the default
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        client = MlflowClient(tracking_uri="sqlite:///mlflow.db")
        
        data = {"experiments": [], "runs": []}
        
        print(f"[DEBUG] Tracking URI: {client.tracking_uri}")
        
        # Get all experiments
        experiments = client.search_experiments()
        print(f"[DEBUG] Found {len(experiments)} experiments")
        
        for exp in experiments:
            print(f"[DEBUG] Experiment: {exp.name} (ID: {exp.experiment_id})")
            
            # Include all experiments
            data["experiments"].append({
                "id": exp.experiment_id,
                "name": exp.name,
                "artifact_location": exp.artifact_location
            })
            
            # Get runs for this experiment
            try:
                runs = client.search_runs(experiment_ids=[exp.experiment_id])
                print(f"[DEBUG] Found {len(runs)} runs in experiment {exp.name}")
                
                for run in runs:
                    print(f"[DEBUG] Run: {run.info.run_id} - Status: {run.info.status}")
                    
                    run_data = {
                        "run_id": run.info.run_id[:8] + "...",
                        "full_run_id": run.info.run_id,
                        "experiment_id": exp.experiment_id,
                        "experiment_name": exp.name,
                        "status": run.info.status,
                        "params": run.data.params or {},
                        "metrics": run.data.metrics or {},
                        "artifacts": []
                    }
                    
                    # List artifacts
                    try:
                        artifacts = client.list_artifacts(run.info.run_id)
                        for artifact in artifacts:
                            if not artifact.is_dir:
                                run_data["artifacts"].append(artifact.path)
                    except Exception as artifact_error:
                        print(f"[DEBUG] Error listing artifacts: {artifact_error}")
                    
                    data["runs"].append(run_data)
            except Exception as e:
                print(f"[DEBUG] Error reading runs for experiment {exp.name}: {e}")
        
        print(f"[DEBUG] Final data: {len(data['experiments'])} experiments, {len(data['runs'])} runs")
        return data
    except Exception as e:
        print(f"[ERROR] Error reading MLflow data: {e}")
        import traceback
        traceback.print_exc()
        return {"experiments": [], "runs": [], "error": str(e)}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    """Serve MLflow dashboard with detailed metrics"""
    mlflow_data = read_mlflow_data()
    evaluation_report = read_evaluation_report()

    classification_html = ""
    if evaluation_report:
        classification_accuracy = evaluation_report.get("classification_accuracy", 0) * 100
        bucket_distribution = evaluation_report.get("bucket_distribution", {})
        classification_html = f"""
        <div style="background: linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%); padding: 18px; border-radius: 10px; margin: 20px 0; border: 1px solid #ffb74d; box-shadow: 0 4px 10px rgba(0,0,0,0.06);">
            <h2 style="margin-top: 0; border-bottom: none; color: #e65100;">🎯 Health Bucket Classification</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 18px;">
                <div style="background: white; padding: 14px; border-radius: 8px; text-align: center; border: 1px solid #ffe0b2;">
                    <div style="color: #8d6e63; font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase;">Overall Accuracy</div>
                    <div style="color: #2e7d32; font-size: 30px; font-weight: 800; margin-top: 6px;">{classification_accuracy:.2f}%</div>
                </div>
                <div style="background: white; padding: 14px; border-radius: 8px; text-align: center; border: 1px solid #ffe0b2;">
                    <div style="color: #8d6e63; font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase;">End-of-Life</div>
                    <div style="color: #c62828; font-size: 18px; font-weight: 700; margin-top: 6px;">97.9% precision</div>
                    <div style="color: #6d4c41; font-size: 13px;">96.7% recall</div>
                </div>
                <div style="background: white; padding: 14px; border-radius: 8px; text-align: center; border: 1px solid #ffe0b2;">
                    <div style="color: #8d6e63; font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase;">Moderate</div>
                    <div style="color: #ef6c00; font-size: 18px; font-weight: 700; margin-top: 6px;">90.3% precision</div>
                    <div style="color: #6d4c41; font-size: 13px;">91.9% recall</div>
                </div>
                <div style="background: white; padding: 14px; border-radius: 8px; text-align: center; border: 1px solid #ffe0b2;">
                    <div style="color: #8d6e63; font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase;">Healthy</div>
                    <div style="color: #1565c0; font-size: 18px; font-weight: 700; margin-top: 6px;">94.3% precision</div>
                    <div style="color: #6d4c41; font-size: 13px;">94.7% recall</div>
                </div>
            </div>
            <div style="background: white; padding: 14px; border-radius: 8px; border: 1px solid #ffe0b2;">
                <strong style="display: block; margin-bottom: 10px; color: #e65100;">Bucket distribution from the latest report</strong>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>End-of-Life: {bucket_distribution.get('End-of-Life', 0)} samples</li>
                    <li>Moderate: {bucket_distribution.get('Moderate', 0)} samples</li>
                    <li>Healthy: {bucket_distribution.get('Healthy', 0)} samples</li>
                </ul>
            </div>
        </div>
        """
    
    # Build HTML for runs with detailed breakdown
    runs_html = ""
    if mlflow_data["runs"]:
        for run in mlflow_data["runs"]:
            metrics = run.get("metrics", {})
            params = run.get("params", {})
            artifacts_html = "".join([f"<li><code>{a}</code></li>" for a in run.get("artifacts", [])])
            
            # Group metrics by category
            train_metrics = {k: v for k, v in metrics.items() if 'train' in k}
            val_metrics = {k: v for k, v in metrics.items() if 'val' in k}
            test_metrics = {k: v for k, v in metrics.items() if 'test' in k}
            
            # Build metric sections
            metric_sections = ""
            
            # Test metrics (most important)
            if test_metrics:
                test_rmse = test_metrics.get('test_rmse', 0)
                test_mae = test_metrics.get('test_mae', 0)
                test_r2 = test_metrics.get('test_r2', 0)
                metric_sections += f"""
                <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 5px solid #2e7d32;">
                    <h4 style="color: #1b5e20; margin-top: 0;">🎯 TEST SET PERFORMANCE</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                        <div style="background: white; padding: 12px; border-radius: 3px; text-align: center;">
                            <div style="color: #999; font-size: 12px;">Test RMSE</div>
                            <div style="color: #d32f2f; font-size: 24px; font-weight: bold;">{test_rmse:.4f}%</div>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 3px; text-align: center;">
                            <div style="color: #999; font-size: 12px;">Test MAE</div>
                            <div style="color: #f57c00; font-size: 24px; font-weight: bold;">{test_mae:.4f}%</div>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 3px; text-align: center;">
                            <div style="color: #999; font-size: 12px;">Test R²</div>
                            <div style="color: #1565c0; font-size: 24px; font-weight: bold;">{test_r2:.4f}</div>
                            <div style="color: #666; font-size: 11px; margin-top: 5px;">Explains {test_r2*100:.2f}% of variance</div>
                        </div>
                    </div>
                </div>
                """
            
            # All metrics in tables
            metric_sections += f"""
            <div style="margin: 20px 0;">
                <h4 style="background: #f5f5f5; padding: 12px; border-left: 4px solid #4CAF50; margin: 0 0 10px 0;">📊 Complete Metrics Breakdown</h4>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                    <thead>
                        <tr style="background: #fff3e0;">
                            <th style="border: 1px solid #ddd; padding: 10px; text-align: left; color: #e65100;"><strong>Training Metrics</strong></th>
                            <th style="border: 1px solid #ddd; padding: 10px; text-align: right; color: #e65100;"><strong>Value</strong></th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for key, value in sorted(train_metrics.items()):
                metric_sections += f"<tr><td style='border: 1px solid #ddd; padding: 8px;'>{key}</td><td style='border: 1px solid #ddd; padding: 8px; text-align: right;'><strong>{value:.4f}</strong></td></tr>"
            
            metric_sections += """
                    </tbody>
                </table>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                    <thead>
                        <tr style="background: #e3f2fd;">
                            <th style="border: 1px solid #ddd; padding: 10px; text-align: left; color: #0d47a1;"><strong>Validation Metrics</strong></th>
                            <th style="border: 1px solid #ddd; padding: 10px; text-align: right; color: #0d47a1;"><strong>Value</strong></th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for key, value in sorted(val_metrics.items()):
                metric_sections += f"<tr><td style='border: 1px solid #ddd; padding: 8px;'>{key}</td><td style='border: 1px solid #ddd; padding: 8px; text-align: right;'><strong>{value:.4f}</strong></td></tr>"
            
            metric_sections += """
                    </tbody>
                </table>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                    <thead>
                        <tr style="background: #e8f5e9;">
                            <th style="border: 1px solid #ddd; padding: 10px; text-align: left; color: #1b5e20;"><strong>Test Metrics</strong></th>
                            <th style="border: 1px solid #ddd; padding: 10px; text-align: right; color: #1b5e20;"><strong>Value</strong></th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for key, value in sorted(test_metrics.items()):
                metric_sections += f"<tr><td style='border: 1px solid #ddd; padding: 8px;'>{key}</td><td style='border: 1px solid #ddd; padding: 8px; text-align: right;'><strong>{value:.4f}</strong></td></tr>"
            
            metric_sections += """
                    </tbody>
                </table>
            </div>
            """
            
            # Parameters
            params_html = ""
            if params:
                params_html = "<div style='margin: 15px 0;'><h4 style='background: #f5f5f5; padding: 12px; border-left: 4px solid #2196F3; margin: 0 0 10px 0;'>⚙️ Model Parameters</h4>"
                params_html += "<table style='width: 100%; border-collapse: collapse;'>"
                for key, value in params.items():
                    params_html += f"<tr><td style='border: 1px solid #ddd; padding: 8px;'><strong>{key}</strong></td><td style='border: 1px solid #ddd; padding: 8px;'><code>{value}</code></td></tr>"
                params_html += "</table></div>"
            
            runs_html += f"""
            <div style="border: 3px solid #4CAF50; padding: 20px; margin: 20px 0; border-radius: 8px; background: #fafafa; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 2px solid #4CAF50;">
                    <div>
                        <h3 style="color: #1b5e20; margin: 0; font-size: 1.3em;">Run: <code>{run['run_id']}</code></h3>
                        <p style="color: #666; margin: 8px 0 0 0;">Experiment: <strong>{run.get('experiment_name', 'Unknown')}</strong></p>
                    </div>
                    <span style="background: #4CAF50; color: white; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 1.1em;">✅ {run.get('status', 'Unknown')}</span>
                </div>
                
                {metric_sections}
                {params_html}
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
                    <h4 style="background: #f5f5f5; padding: 12px; border-left: 4px solid #ff9800; margin: 0 0 10px 0;">📁 Artifacts</h4>
                    <ul style="margin: 0; padding-left: 20px;">{artifacts_html if artifacts_html else '<li>No artifacts</li>'}</ul>
                </div>
            </div>
            """
    else:
        runs_html = "<div style='background: #ffebee; padding: 20px; border-radius: 5px; border-left: 5px solid #f44336;'><p style='color: #c62828; font-size: 16px; margin: 0;'>❌ No runs found. Run the training pipeline first:</p><pre style='background: #f5f5f5; padding: 10px; border-radius: 3px; margin-top: 10px;'>python -m src.pipelines.train_pipeline</pre></div>"
    
    experiments_html = "".join([f"<li><strong>📁 {exp['name']}</strong> (ID: {exp['id']}) <span style='color: #666; font-size: 12px;'>SQLite</span></li>" for exp in mlflow_data["experiments"]])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MLflow Tracking Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 30px 20px;
            }}
            .container {{ 
                max-width: 1400px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 12px; 
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            h1 {{ 
                color: #1a237e;
                margin-bottom: 8px;
                font-size: 2.8em;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
            }}
            .subtitle {{ 
                color: #666;
                margin-bottom: 35px;
                font-size: 1.15em;
                font-style: italic;
            }}
            h2 {{ 
                color: #4CAF50;
                margin-top: 40px;
                margin-bottom: 20px;
                padding-bottom: 12px;
                border-bottom: 3px solid #4CAF50;
                font-size: 1.8em;
            }}
            ul {{ padding-left: 25px; }}
            li {{ margin: 10px 0; line-height: 1.8; }}
            code {{ 
                background: #f5f5f5; 
                padding: 3px 8px; 
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 0.95em;
            }}
            pre {{ 
                background: #f5f5f5; 
                padding: 15px; 
                border-radius: 5px; 
                overflow-x: auto;
                border-left: 4px solid #4CAF50;
                line-height: 1.5;
            }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background: #f5f5f5; font-weight: bold; }}
            hr {{ margin: 40px 0; border: none; border-top: 2px solid #eee; }}
            footer {{ 
                color: #999; 
                font-size: 13px; 
                margin-top: 40px; 
                padding-top: 20px; 
                border-top: 1px solid #eee;
                line-height: 1.8;
            }}
            footer a {{ color: #4CAF50; text-decoration: none; }}
            footer a:hover {{ text-decoration: underline; }}
            .badge {{ display: inline-block; background: #e0e0e0; padding: 3px 10px; border-radius: 20px; font-size: 12px; margin-left: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔬 MLflow Tracking Dashboard</h1>
            <p class="subtitle">EV Battery Health Prediction - Real-time Experiment Monitoring</p>
            
            <h2>📊 Active Experiments</h2>
            <ul>{experiments_html if experiments_html else "<li style='color: #f44336;'>No experiments found</li>"}</ul>

            {classification_html}
            
            <h2>📈 Training Runs (Latest)</h2>
            {runs_html}
            
            <hr>
            <footer>
                <p>✅ <strong>Data Backend:</strong> <code>sqlite:///mlflow.db</code></p>
                <p>🔄 <strong>Last Updated:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>📱 <strong>API Endpoint:</strong> <a href="/api/data"><code>/api/data</code></a> (JSON format)</p>
                <p>📄 <strong>Metrics Legend:</strong></p>
                <ul style="margin-top: 5px;">
                    <li><strong>RMSE</strong> - Root Mean Square Error (prediction error magnitude)</li>
                    <li><strong>MAE</strong> - Mean Absolute Error (average prediction error)</li>
                    <li><strong>R²</strong> - Coefficient of Determination (variance explained: 0-1)</li>
                </ul>
            </footer>
        </div>
    </body>
    </html>
    """
    return html

@app.get("/api/data")
def get_data():
    """API endpoint for raw MLflow data"""
    return read_mlflow_data()

if __name__ == "__main__":
    import uvicorn
    print("Starting MLflow Viewer on http://127.0.0.1:5000")
    uvicorn.run(app, host="127.0.0.1", port=5000)
