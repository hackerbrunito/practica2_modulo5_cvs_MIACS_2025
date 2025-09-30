#!/usr/bin/env python3
"""
Script para verificar que el dataset está correctamente cargado.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import sys
import pandas as pd
from pathlib import Path

# Importar configuración y utilidades
from config import DATASET_ORIGINAL, RESULTS_DIR
from utils import OutputLogger, print_separator

def verify_dataset():
    """Verifica la estructura y contenido del dataset."""
    # Configurar output logger
    output_file = RESULTS_DIR / 'verify_dataset_output.txt'
    sys.stdout = OutputLogger(str(output_file))
    
    print("Verificando dataset...")
    print_separator("VERIFICACIÓN DEL DATASET")
    
    # Verificar existencia del archivo
    if not DATASET_ORIGINAL.exists():
        print(f"ERROR: No se encuentra el archivo {DATASET_ORIGINAL}")
        sys.exit(1)
    
    print(f"Archivo encontrado: {DATASET_ORIGINAL}")
    
    # Cargar dataset
    df = pd.read_csv(DATASET_ORIGINAL)
    
    # Verificar estructura básica
    print(f"\nEstructura del dataset:")
    print(f"- Número de registros: {len(df):,}")
    print(f"- Número de columnas: {len(df.columns)}")
    
    # Verificar que son exactamente 33,902 registros y 12 columnas
    if len(df) != 33902:
        print(f"ADVERTENCIA: Se esperaban 33,902 registros, se encontraron {len(df):,}")
    
    if len(df.columns) != 12:
        print(f"ADVERTENCIA: Se esperaban 12 columnas, se encontraron {len(df.columns)}")
    
    # Mostrar columnas
    print("\nColumnas del dataset:")
    for col in df.columns:
        print(f"- {col}")
    
    # Tipos de datos
    print("\nTipos de datos:")
    print(df.dtypes)
    
    # Valores faltantes
    print("\nValores faltantes por columna:")
    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            print(f"- {col}: {count} ({count/len(df)*100:.2f}%)")
    
    # Estadísticas básicas
    print("\nEstadísticas básicas:")
    print(df.describe())
    
    # Información específica del dataset
    print("\nInformación adicional:")
    print(f"- Protocolos únicos: {df['protocol'].unique()}")
    print(f"- Distribución de protocolos:")
    protocol_dist = df['protocol'].value_counts()
    for protocol, count in protocol_dist.items():
        print(f"  - {protocol}: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\n- Registros con DNS queries: {df['dns_query'].notna().sum()} ({df['dns_query'].notna().sum()/len(df)*100:.1f}%)")
    print(f"- Registros con HTTP host: {df['http_host'].notna().sum()} ({df['http_host'].notna().sum()/len(df)*100:.1f}%)")
    print(f"- Registros marcados como outliers: {df['is_length_outlier'].sum()} ({df['is_length_outlier'].sum()/len(df)*100:.1f}%)")
    
    print("\nCreando verify_dataset_output.txt...")
    print("\nDataset verificado correctamente.")
    
    # Cerrar logger
    sys.stdout.close()
    sys.stdout = sys.stdout.terminal

def main():
    """Función principal."""
    verify_dataset()

if __name__ == "__main__":
    main()