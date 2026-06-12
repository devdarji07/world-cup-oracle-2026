import sys
import time
sys.path.insert(0, r'C:\Users\devda\OneDrive\Desktop\World_cup_oracle\worldcup_predictor')
from src.train_model import train_models

log_path = 'training_run.log'
with open(log_path, 'w') as f:
    f.write('Starting training...\n')
    f.flush()
    try:
        train_models()
        f.write('Training completed successfully.\n')
    except Exception as e:
        f.write('Training failed:\n')
        import traceback
        traceback.print_exc(file=f)
    f.flush()
print('Runner finished; see training_run.log for details')
