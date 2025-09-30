#!/usr/bin/env python3
"""
Script para realizar feature engineering sobre el dataset etiquetado.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Importar configuración y utilidades
from config import DATASET_LABELED, DATASET_PROCESSED, RESULTS_DIR
from utils import OutputLogger, print_separator, load_dataset

def extract_temporal_features(df):
    """Extrae características temporales del timestamp."""
    print("Extrayendo características temporales...")
    
    df['datetime'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Eliminar columnas temporales no necesarias
    df = df.drop(['datetime', 'timestamp'], axis=1)
    
    print(f"  - Agregadas: hour, day_of_week, is_weekend")
    return df

def encode_protocol(df):
    """One-hot encoding para protocol."""
    print("Aplicando one-hot encoding a protocol...")
    
    # One-hot encoding
    protocol_dummies = pd.get_dummies(df['protocol'], prefix='protocol')
    df = pd.concat([df, protocol_dummies], axis=1)
    df = df.drop('protocol', axis=1)
    
    print(f"  - Protocol codificado en: {', '.join(protocol_dummies.columns)}")
    return df

def categorize_ports(df):
    """Categoriza puertos en bien_conocido/registrado/dinámico."""
    print("Categorizando puertos...")
    
    def categorize_port(port):
        if pd.isna(port):
            return 'unknown'
        elif port < 1024:
            return 'well_known'
        elif port < 49152:
            return 'registered'
        else:
            return 'dynamic'
    
    # Categorizar puertos fuente y destino
    df['src_port_category'] = df['src_port'].apply(categorize_port)
    df['dst_port_category'] = df['dst_port'].apply(categorize_port)
    
    # One-hot encoding para categorías
    src_cat_dummies = pd.get_dummies(df['src_port_category'], prefix='src_port_cat')
    dst_cat_dummies = pd.get_dummies(df['dst_port_category'], prefix='dst_port_cat')
    
    df = pd.concat([df, src_cat_dummies, dst_cat_dummies], axis=1)
    df = df.drop(['src_port_category', 'dst_port_category'], axis=1)
    
    print(f"  - Puertos categorizados y codificados")
    return df

def create_binary_flags(df):
    """Crea flags binarios para características importantes."""
    print("Creando flags binarios...")
    
    # Flags binarios
    df['has_dns'] = df['dns_query'].notna().astype(int)
    df['has_http'] = df['http_host'].notna().astype(int)
    df['has_user_agent'] = df['user_agent'].notna().astype(int)
    
    # Flag para puertos conocidos de malware
    malware_ports = [137, 4444, 6667, 31337, 12345, 1337, 5555]
    df['is_malware_port'] = (
        df['dst_port'].isin(malware_ports) | 
        df['src_port'].isin(malware_ports)
    ).astype(int)
    
    print(f"  - Agregados: has_dns, has_http, has_user_agent, is_malware_port")
    return df

def normalize_length(df):
    """Normaliza la columna length."""
    print("Normalizando length...")
    
    scaler = StandardScaler()
    df['length_normalized'] = scaler.fit_transform(df[['length']])
    
    # Mantener length original por si acaso
    print(f"  - length_normalized agregado (media=0, std=1)")
    return df

def encode_ip_ranges(df):
    """Codifica rangos de IPs (simplificado)."""
    print("Codificando rangos de IPs...")
    
    # Como las IPs están anonimizadas, crear features basadas en los primeros caracteres
    df['src_ip_prefix'] = df['src_ip_anon'].str[:2]
    df['dst_ip_prefix'] = df['dst_ip_anon'].str[:2]
    
    # Contar frecuencia de prefijos (IPs que aparecen mucho podrían ser servidores)
    src_freq = df['src_ip_anon'].value_counts()
    dst_freq = df['dst_ip_anon'].value_counts()
    
    df['src_ip_freq'] = df['src_ip_anon'].map(src_freq)
    df['dst_ip_freq'] = df['dst_ip_anon'].map(dst_freq)
    
    # Normalizar frecuencias
    scaler = StandardScaler()
    df['src_ip_freq_norm'] = scaler.fit_transform(df[['src_ip_freq']])
    df['dst_ip_freq_norm'] = scaler.fit_transform(df[['dst_ip_freq']])
    
    # Eliminar columnas de prefijos y frecuencias sin normalizar
    df = df.drop(['src_ip_prefix', 'dst_ip_prefix', 'src_ip_freq', 'dst_ip_freq'], axis=1)
    
    print(f"  - Agregadas frecuencias normalizadas de IPs")
    return df

def drop_non_numeric_columns(df):
    """Elimina columnas no numéricas."""
    print("Eliminando columnas no numéricas...")
    
    # Columnas a eliminar
    columns_to_drop = ['src_ip_anon', 'dst_ip_anon', 'dns_query', 
                      'http_host', 'http_path', 'user_agent']
    
    # Eliminar solo las que existen
    existing_cols = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(existing_cols, axis=1)
    
    print(f"  - Eliminadas: {', '.join(existing_cols)}")
    return df

def reorder_columns(df):
    """Reordena columnas con suspicious al final."""
    print("Reordenando columnas...")
    
    # Mover suspicious al final
    cols = [col for col in df.columns if col != 'suspicious']
    cols.append('suspicious')
    df = df[cols]
    
    return df

def main():
    """Función principal de feature engineering."""
    # Configurar output logger
    output_file = RESULTS_DIR / 'feature_engineering_output.txt'
    sys.stdout = OutputLogger(str(output_file))
    
    print_separator("FEATURE ENGINEERING")
    
    # Cargar dataset etiquetado
    df = load_dataset(DATASET_LABELED, "Dataset etiquetado")
    
    # Aplicar transformaciones
    print_separator("APLICANDO TRANSFORMACIONES")
    df = extract_temporal_features(df)
    df = encode_protocol(df)
    df = categorize_ports(df)
    df = create_binary_flags(df)
    df = normalize_length(df)
    df = encode_ip_ranges(df)
    df = drop_non_numeric_columns(df)
    df = reorder_columns(df)
    
    # Información final
    print_separator("DATASET PROCESADO")
    print(f"Forma final: {df.shape[0]:,} registros, {df.shape[1]} features")
    print(f"\nFeatures finales ({len(df.columns)-1} + 1 target):")
    for i, col in enumerate(df.columns):
        if col == 'suspicious':
            print(f"  TARGET: {col}")
        else:
            print(f"  {i+1}. {col}")
    
    # Guardar dataset procesado
    df.to_csv(DATASET_PROCESSED, index=False)
    print(f"\nDataset procesado guardado en: {DATASET_PROCESSED}")
    
    # Verificar que no hay NaN
    nan_count = df.isnull().sum().sum()
    print(f"\nValores NaN en el dataset final: {nan_count}")
    
    print("\nFeature engineering completado exitosamente.")
    
    # Cerrar logger
    sys.stdout.close()
    sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    main()