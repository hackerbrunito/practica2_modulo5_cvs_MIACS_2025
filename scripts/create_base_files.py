#!/usr/bin/env python3
"""
Script para crear los archivos base de configuración del proyecto.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

from pathlib import Path

def create_config_py():
    """Crea el archivo config.py con la configuración centralizada."""
    print("Creando script config.py...")
    
    config_content = '''"""
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
'''
    
    scripts_dir = Path(__file__).parent
    config_path = scripts_dir / 'config.py'
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)

def create_utils_py():
    """Crea el archivo utils.py con funciones auxiliares compartidas."""
    print("Creando script utils.py...")
    
    utils_content = '''"""
Funciones auxiliares compartidas.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""
import sys
import pandas as pd

class OutputLogger:
    """Duplica output de consola a archivo."""
    
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()


def print_separator(title=""):
    """Imprime separador visual."""
    print("="*60)
    if title:
        print(title)
        print("="*60)


def load_dataset(filepath, description=""):
    """Carga dataset y muestra información."""
    df = pd.read_csv(filepath)
    if description:
        print(f"Cargando: {description}")
    print(f"Dataset: {len(df):,} registros, {len(df.columns)} columnas")
    return df
'''
    
    scripts_dir = Path(__file__).parent
    utils_path = scripts_dir / 'utils.py'
    
    with open(utils_path, 'w', encoding='utf-8') as f:
        f.write(utils_content)

def create_init_py():
    """Crea el archivo __init__.py para que scripts/ sea un paquete Python."""
    print("Creando __init__.py...")
    
    scripts_dir = Path(__file__).parent
    init_path = scripts_dir / '__init__.py'
    
    # Crear archivo vacío
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write("")

def main():
    """Función principal."""
    create_config_py()
    create_utils_py()
    create_init_py()

if __name__ == "__main__":
    main()