import os, time, mlflow
from datetime import datetime
uri = os.getenv('MLFLOW_TRACKING_URI','<none>')
print('Tracking URI:', uri)
mlflow.set_tracking_uri(uri)
mlflow.set_experiment('defi-risk')
with mlflow.start_run(run_name=f"smoke-{datetime.now().strftime('%H%M%S')}"):
    mlflow.log_param('mode','smoke')
    mlflow.log_metric('timestamp', time.time())
    mlflow.log_metric('random_metric', 42)
print('Done.')
