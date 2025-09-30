#!/usr/bin/env python3
"""
Script para crear la variable objetivo (suspicious) basada en reglas.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import sys
import pandas as pd

# Importar configuración y utilidades
from config import DATASET_ORIGINAL, DATASET_LABELED, RESULTS_DIR
from utils import OutputLogger, print_separator, load_dataset

def apply_labeling_rules(df):
    """Aplica las reglas para etiquetar tráfico como sospechoso."""
    print_separator("APLICANDO REGLAS DE ETIQUETADO")
    
    # Inicializar columna objetivo
    df['suspicious'] = 0
    suspicious_counts = {}
    
    # Regla 1: Puerto 137 (NetBIOS) - conocido por vulnerabilidades
    rule1 = (df['dst_port'] == 137) | (df['src_port'] == 137)
    df.loc[rule1, 'suspicious'] = 1
    suspicious_counts['Puerto 137 (NetBIOS)'] = rule1.sum()
    print(f"Regla 1 - Puerto 137 (NetBIOS): {rule1.sum()} registros")
    
    # Regla 2: Puertos de malware conocidos
    malware_ports = [4444, 6667, 31337, 12345, 1337, 5555]
    rule2 = df['dst_port'].isin(malware_ports) | df['src_port'].isin(malware_ports)
    df.loc[rule2, 'suspicious'] = 1
    suspicious_counts['Puertos de malware'] = rule2.sum()
    print(f"Regla 2 - Puertos de malware conocidos: {rule2.sum()} registros")
    
    # Regla 3: TLDs sospechosos en consultas DNS
    suspicious_tlds = ['.tk', '.ml', '.ga', '.biz', '.cn']
    rule3 = df['dns_query'].notna() & df['dns_query'].str.lower().str.endswith(tuple(suspicious_tlds))
    df.loc[rule3, 'suspicious'] = 1
    suspicious_counts['TLDs sospechosos'] = rule3.sum()
    print(f"Regla 3 - TLDs sospechosos: {rule3.sum()} registros")
    
    # Regla 4: HTTP sin User-Agent
    rule4 = df['http_host'].notna() & df['user_agent'].isna()
    df.loc[rule4, 'suspicious'] = 1
    suspicious_counts['HTTP sin User-Agent'] = rule4.sum()
    print(f"Regla 4 - HTTP sin User-Agent: {rule4.sum()} registros")
    
    # Regla 5: Dominios muy largos (>40 chars, posible DGA)
    rule5 = df['dns_query'].notna() & (df['dns_query'].str.len() > 40)
    df.loc[rule5, 'suspicious'] = 1
    suspicious_counts['Dominios largos (DGA)'] = rule5.sum()
    print(f"Regla 5 - Dominios largos (posible DGA): {rule5.sum()} registros")
    
    # Regla 6: Paquetes extremadamente grandes + puerto alto
    length_threshold = df['length'].quantile(0.99)
    rule6 = (df['length'] > length_threshold) & (df['dst_port'] > 10000)
    df.loc[rule6, 'suspicious'] = 1
    suspicious_counts['Paquetes grandes + puerto alto'] = rule6.sum()
    print(f"Regla 6 - Paquetes grandes + puerto alto: {rule6.sum()} registros")
    
    return df, suspicious_counts

def analyze_target_distribution(df):
    """Analiza la distribución de la variable objetivo."""
    print_separator("DISTRIBUCIÓN DE LA VARIABLE OBJETIVO")
    
    total = len(df)
    suspicious = df['suspicious'].sum()
    normal = total - suspicious
    
    print(f"\nDistribución final:")
    print(f"  Normal: {normal:,} ({normal/total*100:.1f}%)")
    print(f"  Sospechoso: {suspicious:,} ({suspicious/total*100:.1f}%)")
    
    # Verificar balance objetivo (10-30%)
    suspicious_pct = suspicious/total*100
    if 10 <= suspicious_pct <= 30:
        print(f"\nBalance: {suspicious_pct:.1f}% sospechoso - DENTRO del rango objetivo (10-30%)")
    else:
        print(f"\nADVERTENCIA: {suspicious_pct:.1f}% sospechoso - FUERA del rango objetivo (10-30%)")
    
    return suspicious_pct

def save_labeled_dataset(df):
    """Guarda el dataset etiquetado."""
    print_separator("GUARDANDO DATASET ETIQUETADO")
    
    # Reorganizar columnas para que suspicious sea la última
    columns = [col for col in df.columns if col != 'suspicious'] + ['suspicious']
    df = df[columns]
    
    # Guardar dataset
    df.to_csv(DATASET_LABELED, index=False)
    print(f"Dataset guardado en: {DATASET_LABELED}")
    print(f"Registros: {len(df):,}")
    print(f"Columnas: {len(df.columns)} (agregada 'suspicious')")
    
    return df

def main():
    """Función principal para crear variable objetivo."""
    # Configurar output logger
    output_file = RESULTS_DIR / 'create_target_output.txt'
    sys.stdout = OutputLogger(str(output_file))
    
    print_separator("CREACIÓN DE VARIABLE OBJETIVO")
    
    # Cargar dataset original
    df = load_dataset(DATASET_ORIGINAL, "Dataset original")
    
    # Aplicar reglas de etiquetado
    df, suspicious_counts = apply_labeling_rules(df)
    
    # Analizar distribución
    suspicious_pct = analyze_target_distribution(df)
    
    # Mostrar resumen de reglas
    print_separator("RESUMEN DE REGLAS APLICADAS")
    for rule, count in suspicious_counts.items():
        print(f"  {rule}: {count} registros")
    
    # Guardar dataset etiquetado
    save_labeled_dataset(df)
    
    print_separator("PROCESO COMPLETADO")
    print(f"\nVariable objetivo creada exitosamente.")
    print(f"Balance final: {suspicious_pct:.1f}% tráfico sospechoso")
    
    # Cerrar logger
    sys.stdout.close()
    sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    main()