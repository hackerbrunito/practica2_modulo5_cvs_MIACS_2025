"""
Configuración centralizada del proyecto.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""
from pathlib import Path

# Paths base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
RESULTS_DIR = BASE_DIR / 'results'
MODELS_DIR = BASE_DIR / 'models'
REPORTS_DIR = BASE_DIR / 'reports'

# Subdirectorios de results
EXPLORATORY_DIR = RESULTS_DIR / 'exploratory'
SHAP_DIR = RESULTS_DIR / 'shap_plots'
PRIVACY_DIR = RESULTS_DIR / 'privacy_analysis'

# Archivos de datos
DATASET_ORIGINAL = DATA_DIR / 'traffic_anonymous.csv'
DATASET_LABELED = DATA_DIR / 'traffic_labeled.csv'
DATASET_PROCESSED = DATA_DIR / 'traffic_processed.csv'
DATASET_K_ANON = DATA_DIR / 'traffic_k_anonymous.csv'

# Modelo
MODEL_PATH = MODELS_DIR / 'random_forest_model.pkl'

# Parámetros globales
RANDOM_STATE = 42
TEST_SIZE = 0.3
K_ANONYMITY = 10
MAX_DEPTH = 10  # Para interpretabilidad
