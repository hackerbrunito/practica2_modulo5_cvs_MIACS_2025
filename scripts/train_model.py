#!/usr/bin/env python3
"""
Script para entrenar un modelo RandomForest interpretable.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
import joblib

# Importar configuración y utilidades
from config import DATASET_PROCESSED, MODEL_PATH, RESULTS_DIR, RANDOM_STATE, TEST_SIZE, MAX_DEPTH
from utils import OutputLogger, print_separator, load_dataset

def prepare_data(df):
    """Prepara los datos para entrenamiento."""
    print_separator("PREPARACIÓN DE DATOS")
    
    # Separar features y target
    X = df.drop('suspicious', axis=1)
    y = df['suspicious']
    
    print(f"Features (X): {X.shape}")
    print(f"Target (y): {y.shape}")
    print(f"Distribución del target:")
    print(f"  - Normal (0): {(y == 0).sum()} ({(y == 0).sum() / len(y) * 100:.1f}%)")
    print(f"  - Sospechoso (1): {(y == 1).sum()} ({(y == 1).sum() / len(y) * 100:.1f}%)")
    
    return X, y

def split_data(X, y):
    """Divide los datos en train/test."""
    print_separator("DIVISIÓN TRAIN/TEST")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=TEST_SIZE, 
        random_state=RANDOM_STATE, 
        stratify=y
    )
    
    print(f"Conjunto de entrenamiento: {X_train.shape[0]:,} registros")
    print(f"Conjunto de test: {X_test.shape[0]:,} registros")
    print(f"Proporción test: {TEST_SIZE} (30%)")
    print(f"Random state: {RANDOM_STATE}")
    print(f"Estratificación: Sí (mantiene proporción de clases)")
    
    return X_train, X_test, y_train, y_test

def train_model(X_train, y_train):
    """Entrena el modelo RandomForest."""
    print_separator("ENTRENAMIENTO DEL MODELO")
    
    # Configurar modelo para interpretabilidad
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=MAX_DEPTH,  # Limitado para interpretabilidad
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1
    )
    
    print(f"Modelo: RandomForestClassifier")
    print(f"Parámetros:")
    print(f"  - n_estimators: 100")
    print(f"  - max_depth: {MAX_DEPTH} (para interpretabilidad)")
    print(f"  - random_state: {RANDOM_STATE}")
    print(f"  - n_jobs: -1 (todos los cores)")
    
    print(f"\nEntrenando modelo...")
    model.fit(X_train, y_train)
    print("Modelo entrenado exitosamente.")
    
    return model

def evaluate_model(model, X_train, X_test, y_train, y_test):
    """Evalúa el modelo en train y test."""
    print_separator("EVALUACIÓN DEL MODELO")
    
    # Predicciones
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Métricas en conjunto de entrenamiento
    print("MÉTRICAS EN CONJUNTO DE ENTRENAMIENTO:")
    train_accuracy = accuracy_score(y_train, y_train_pred)
    train_precision = precision_score(y_train, y_train_pred)
    train_recall = recall_score(y_train, y_train_pred)
    train_f1 = f1_score(y_train, y_train_pred)
    
    print(f"  - Accuracy: {train_accuracy:.4f}")
    print(f"  - Precision: {train_precision:.4f}")
    print(f"  - Recall: {train_recall:.4f}")
    print(f"  - F1-Score: {train_f1:.4f}")
    
    # Métricas en conjunto de test
    print("\nMÉTRICAS EN CONJUNTO DE TEST:")
    test_accuracy = accuracy_score(y_test, y_test_pred)
    test_precision = precision_score(y_test, y_test_pred)
    test_recall = recall_score(y_test, y_test_pred)
    test_f1 = f1_score(y_test, y_test_pred)
    
    print(f"  - Accuracy: {test_accuracy:.4f}")
    print(f"  - Precision: {test_precision:.4f}")
    print(f"  - Recall: {test_recall:.4f}")
    print(f"  - F1-Score: {test_f1:.4f}")
    
    # Matriz de confusión
    print("\nMATRIZ DE CONFUSIÓN (Test):")
    cm = confusion_matrix(y_test, y_test_pred)
    print(f"  True Negatives:  {cm[0,0]:6,}")
    print(f"  False Positives: {cm[0,1]:6,}")
    print(f"  False Negatives: {cm[1,0]:6,}")
    print(f"  True Positives:  {cm[1,1]:6,}")
    
    # Reporte de clasificación completo
    print("\nREPORTE DE CLASIFICACIÓN (Test):")
    print(classification_report(y_test, y_test_pred, 
                              target_names=['Normal', 'Sospechoso']))
    
    return test_accuracy, test_precision, test_recall, test_f1

def analyze_feature_importance(model, X_train):
    """Analiza la importancia de las features."""
    print_separator("IMPORTANCIA DE FEATURES")
    
    # Obtener importancias
    feature_importances = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("Top 15 features más importantes:")
    for idx, row in feature_importances.head(15).iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    return feature_importances

def save_model(model):
    """Guarda el modelo entrenado."""
    print_separator("GUARDANDO MODELO")
    
    joblib.dump(model, MODEL_PATH)
    print(f"Modelo guardado en: {MODEL_PATH}")

def main():
    """Función principal para entrenar el modelo."""
    # Configurar output logger
    output_file = RESULTS_DIR / 'train_model_output.txt'
    sys.stdout = OutputLogger(str(output_file))
    
    print_separator("ENTRENAMIENTO DE MODELO DE MACHINE LEARNING")
    
    # Cargar dataset procesado
    df = load_dataset(DATASET_PROCESSED, "Dataset procesado")
    
    # Preparar datos
    X, y = prepare_data(df)
    
    # División train/test
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # Entrenar modelo
    model = train_model(X_train, y_train)
    
    # Evaluar modelo
    accuracy, precision, recall, f1 = evaluate_model(
        model, X_train, X_test, y_train, y_test
    )
    
    # Analizar importancia de features
    feature_importances = analyze_feature_importance(model, X_train)
    
    # Guardar modelo
    save_model(model)
    
    print_separator("RESUMEN FINAL")
    print(f"Modelo: RandomForestClassifier (max_depth={MAX_DEPTH})")
    print(f"Métricas en test:")
    print(f"  - Accuracy: {accuracy:.4f}")
    print(f"  - Precision: {precision:.4f}")
    print(f"  - Recall: {recall:.4f}")
    print(f"  - F1-Score: {f1:.4f}")
    print(f"\nNOTA: El objetivo NO es alta precisión, sino interpretabilidad.")
    print("El modelo está limitado en profundidad para facilitar explicación con SHAP.")
    
    print("\nEntrenamiento completado exitosamente.")
    
    # Cerrar logger
    sys.stdout.close()
    sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    main()