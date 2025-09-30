"""
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
