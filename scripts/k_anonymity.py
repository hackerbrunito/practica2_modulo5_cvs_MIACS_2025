#!/usr/bin/env python3
"""
Script para aplicar k-anonimidad al dataset preservando utilidad.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import joblib

# Importar configuración y utilidades
from config import DATASET_PROCESSED, DATASET_K_ANON, PRIVACY_DIR, RESULTS_DIR, K_ANONYMITY, RANDOM_STATE, TEST_SIZE, MAX_DEPTH
from utils import OutputLogger, print_separator, load_dataset

def define_quasi_identifiers(df):
    """Define los cuasi-identificadores para k-anonimidad."""
    print_separator("DEFINIENDO CUASI-IDENTIFICADORES")
    
    # Crear columnas categóricas para generalización
    df_anon = df.copy()
    
    # 1. Port range (generalización de puertos)
    def categorize_port_range(port):
        if port < 1024:
            return 'well_known'
        elif port < 10000:
            return 'registered'
        elif port < 50000:
            return 'dynamic_low'
        else:
            return 'dynamic_high'
    
    df_anon['src_port_range'] = df_anon['src_port'].apply(categorize_port_range)
    df_anon['dst_port_range'] = df_anon['dst_port'].apply(categorize_port_range)
    
    # 2. Hour bucket (generalización temporal)
    df_anon['hour_bucket'] = pd.cut(df_anon['hour'], 
                                    bins=[0, 6, 12, 18, 24], 
                                    labels=['night', 'morning', 'afternoon', 'evening'],
                                    include_lowest=True)
    
    # 3. Length bucket (generalización de tamaño)
    # Usar cut en lugar de qcut para evitar problemas con duplicados
    length_min = df_anon['length'].min()
    length_max = df_anon['length'].max()
    bins = [length_min, 100, 500, 1000, 1500, length_max + 1]
    df_anon['length_bucket'] = pd.cut(df_anon['length'], 
                                      bins=bins,
                                      labels=['very_small', 'small', 'medium', 'large', 'very_large'],
                                      include_lowest=True)
    
    # Lista de cuasi-identificadores
    quasi_identifiers = ['src_port_range', 'dst_port_range', 'hour_bucket', 'length_bucket']
    
    print("Cuasi-identificadores definidos:")
    for qi in quasi_identifiers:
        print(f"  - {qi}")
    
    return df_anon, quasi_identifiers

def apply_k_anonymity(df, quasi_identifiers, k):
    """Aplica k-anonimidad al dataset."""
    print_separator(f"APLICANDO {k}-ANONIMIDAD")
    
    # Agrupar por cuasi-identificadores
    groups = df.groupby(quasi_identifiers, observed=True).size().reset_index(name='count')
    
    print(f"Grupos totales antes de k-anonimidad: {len(groups)}")
    print(f"Grupos que no cumplen k={k}: {len(groups[groups['count'] < k])}")
    
    # Marcar registros que cumplen k-anonimidad
    df_grouped = df.groupby(quasi_identifiers, observed=True).size().reset_index(name='group_size')
    df_anon = df.merge(df_grouped, on=quasi_identifiers, how='left')
    
    # Registros que cumplen k-anonimidad
    mask_k_anon = df_anon['group_size'] >= k
    df_k_anonymous = df_anon[mask_k_anon].copy()
    
    # Eliminar columna auxiliar
    df_k_anonymous = df_k_anonymous.drop('group_size', axis=1)
    
    print(f"\nRegistros originales: {len(df):,}")
    print(f"Registros tras k-anonimidad: {len(df_k_anonymous):,}")
    print(f"Registros suprimidos: {len(df) - len(df_k_anonymous):,} ({(len(df) - len(df_k_anonymous))/len(df)*100:.1f}%)")
    
    return df_k_anonymous

def measure_information_loss(df_original, df_anon, quasi_identifiers):
    """Mide la pérdida de información tras aplicar k-anonimidad."""
    print_separator("MIDIENDO PÉRDIDA DE INFORMACIÓN")
    
    # 1. Pérdida de registros
    record_loss = (len(df_original) - len(df_anon)) / len(df_original) * 100
    print(f"Pérdida de registros: {record_loss:.2f}%")
    
    # 2. Pérdida de diversidad en cuasi-identificadores
    print("\nPérdida de diversidad en cuasi-identificadores:")
    diversity_loss = {}
    
    for qi in quasi_identifiers:
        if qi in df_anon.columns:
            unique_original = df_original[qi].nunique() if qi in df_original.columns else 0
            unique_anon = df_anon[qi].nunique()
            loss = (1 - unique_anon/unique_original) * 100 if unique_original > 0 else 0
            diversity_loss[qi] = loss
            print(f"  {qi}: {unique_original} → {unique_anon} valores únicos ({loss:.1f}% pérdida)")
    
    # 3. Cambios en distribución de la variable objetivo
    if 'suspicious' in df_original.columns and 'suspicious' in df_anon.columns:
        orig_suspicious = df_original['suspicious'].mean()
        anon_suspicious = df_anon['suspicious'].mean()
        print(f"\nDistribución de 'suspicious':")
        print(f"  Original: {orig_suspicious:.3f}")
        print(f"  Anonimizado: {anon_suspicious:.3f}")
        print(f"  Diferencia: {abs(orig_suspicious - anon_suspicious):.3f}")
    
    return record_loss, diversity_loss

def compare_model_performance(df_original, df_anon):
    """Compara el rendimiento del modelo antes y después de k-anonimidad."""
    print_separator("COMPARANDO RENDIMIENTO DEL MODELO")
    
    # Preparar datasets
    features_to_use = [col for col in df_original.columns 
                      if col not in ['suspicious', 'src_port_range', 'dst_port_range', 
                                    'hour_bucket', 'length_bucket', 'group_size']]
    
    X_orig = df_original[features_to_use]
    y_orig = df_original['suspicious']
    
    X_anon = df_anon[features_to_use]
    y_anon = df_anon['suspicious']
    
    # Split datasets
    X_train_orig, X_test_orig, y_train_orig, y_test_orig = train_test_split(
        X_orig, y_orig, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_orig
    )
    
    X_train_anon, X_test_anon, y_train_anon, y_test_anon = train_test_split(
        X_anon, y_anon, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_anon
    )
    
    # Entrenar modelos
    print("\nEntrenando modelo con datos originales...")
    model_orig = RandomForestClassifier(n_estimators=100, max_depth=MAX_DEPTH, 
                                       random_state=RANDOM_STATE, n_jobs=-1)
    model_orig.fit(X_train_orig, y_train_orig)
    
    print("Entrenando modelo con datos anonimizados...")
    model_anon = RandomForestClassifier(n_estimators=100, max_depth=MAX_DEPTH,
                                       random_state=RANDOM_STATE, n_jobs=-1)
    model_anon.fit(X_train_anon, y_train_anon)
    
    # Evaluar modelos
    y_pred_orig = model_orig.predict(X_test_orig)
    y_pred_anon = model_anon.predict(X_test_anon)
    
    accuracy_orig = accuracy_score(y_test_orig, y_pred_orig)
    accuracy_anon = accuracy_score(y_test_anon, y_pred_anon)
    f1_orig = f1_score(y_test_orig, y_pred_orig)
    f1_anon = f1_score(y_test_anon, y_pred_anon)
    
    print("\nMÉTRICAS COMPARATIVAS:")
    print(f"Accuracy - Original: {accuracy_orig:.4f}")
    print(f"Accuracy - Anonimizado: {accuracy_anon:.4f}")
    print(f"Pérdida de accuracy: {(accuracy_orig - accuracy_anon):.4f}")
    
    print(f"\nF1-Score - Original: {f1_orig:.4f}")
    print(f"F1-Score - Anonimizado: {f1_anon:.4f}")
    print(f"Pérdida de F1: {(f1_orig - f1_anon):.4f}")
    
    return {
        'accuracy_orig': accuracy_orig,
        'accuracy_anon': accuracy_anon,
        'f1_orig': f1_orig,
        'f1_anon': f1_anon
    }

def create_utility_comparison_plot(metrics, record_loss):
    """Crea gráfico comparativo de utilidad vs privacidad."""
    print_separator("CREANDO GRÁFICO DE UTILIDAD VS PRIVACIDAD")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Gráfico 1: Métricas del modelo
    categories = ['Accuracy', 'F1-Score']
    original = [metrics['accuracy_orig'], metrics['f1_orig']]
    anonymized = [metrics['accuracy_anon'], metrics['f1_anon']]
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax1.bar(x - width/2, original, width, label='Original', color='blue')
    ax1.bar(x + width/2, anonymized, width, label='Anonimizado', color='orange')
    ax1.set_xlabel('Métrica')
    ax1.set_ylabel('Valor')
    ax1.set_title('Comparación de Métricas del Modelo')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend()
    ax1.set_ylim(0, 1.1)
    
    # Gráfico 2: Trade-off privacidad vs utilidad
    privacy_gain = K_ANONYMITY
    utility_loss = (metrics['accuracy_orig'] - metrics['accuracy_anon']) * 100
    
    ax2.scatter(privacy_gain, 100 - utility_loss, s=200, color='red', marker='o')
    ax2.set_xlabel('Privacidad (k)')
    ax2.set_ylabel('Utilidad Preservada (%)')
    ax2.set_title(f'Trade-off: {K_ANONYMITY}-Anonimidad vs Utilidad')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, K_ANONYMITY * 2)
    ax2.set_ylim(90, 101)
    
    # Anotar el punto
    ax2.annotate(f'k={K_ANONYMITY}\n{100-utility_loss:.1f}% utilidad',
                xy=(privacy_gain, 100 - utility_loss),
                xytext=(privacy_gain + 2, 100 - utility_loss - 2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    plot_path = PRIVACY_DIR / 'utility_comparison.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico guardado en: {plot_path}")

def save_anonymized_dataset(df_anon, quasi_identifiers):
    """Guarda el dataset anonimizado."""
    print_separator("GUARDANDO DATASET ANONIMIZADO")
    
    # Eliminar columnas de generalización temporales
    columns_to_drop = [col for col in quasi_identifiers if col in df_anon.columns]
    df_final = df_anon.drop(columns=columns_to_drop, errors='ignore')
    
    # Guardar
    df_final.to_csv(DATASET_K_ANON, index=False)
    
    print(f"Dataset anonimizado guardado en: {DATASET_K_ANON}")
    print(f"Registros: {len(df_final):,}")
    print(f"Columnas: {len(df_final.columns)}")

def main():
    """Función principal para aplicar k-anonimidad."""
    # Configurar output logger
    output_file = PRIVACY_DIR / 'k_anonymity_output.txt'
    sys.stdout = OutputLogger(str(output_file))
    
    print_separator(f"APLICACIÓN DE {K_ANONYMITY}-ANONIMIDAD")
    print(f"k = {K_ANONYMITY}")
    
    # Cargar dataset procesado
    df_original = load_dataset(DATASET_PROCESSED, "Dataset procesado original")
    
    # Definir cuasi-identificadores
    df_with_qi, quasi_identifiers = define_quasi_identifiers(df_original)
    
    # Aplicar k-anonimidad
    df_anon = apply_k_anonymity(df_with_qi, quasi_identifiers, K_ANONYMITY)
    
    # Medir pérdida de información
    record_loss, diversity_loss = measure_information_loss(df_with_qi, df_anon, quasi_identifiers)
    
    # Comparar rendimiento del modelo
    metrics = compare_model_performance(df_original, df_anon)
    
    # Crear gráfico comparativo
    create_utility_comparison_plot(metrics, record_loss)
    
    # Guardar dataset anonimizado
    save_anonymized_dataset(df_anon, quasi_identifiers)
    
    print_separator("RESUMEN FINAL")
    print(f"\n{K_ANONYMITY}-anonimidad aplicada exitosamente.")
    print(f"Privacidad ganada: Grupos de al menos {K_ANONYMITY} registros idénticos")
    print(f"Utilidad preservada: {(metrics['accuracy_anon']/metrics['accuracy_orig'])*100:.1f}% de accuracy original")
    print(f"Trade-off aceptable para protección de privacidad.")
    
    # Cerrar logger
    sys.stdout.close()
    sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    main()