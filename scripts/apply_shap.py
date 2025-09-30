#!/usr/bin/env python3
"""
Script para aplicar SHAP y explicar las decisiones del modelo.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import sys
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split

# Importar configuración y utilidades
from config import DATASET_PROCESSED, MODEL_PATH, SHAP_DIR, RESULTS_DIR, RANDOM_STATE, TEST_SIZE
from utils import OutputLogger, print_separator, load_dataset

def load_model_and_data():
    """Carga el modelo entrenado y prepara los datos."""
    print_separator("CARGANDO MODELO Y DATOS")
    
    # Cargar modelo
    model = joblib.load(MODEL_PATH)
    print(f"Modelo cargado desde: {MODEL_PATH}")
    
    # Cargar datos
    df = load_dataset(DATASET_PROCESSED, "Dataset procesado")
    
    # Preparar X e y
    X = df.drop('suspicious', axis=1)
    y = df['suspicious']
    
    # Obtener conjunto de test (mismo split que en entrenamiento)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    
    print(f"Datos de test: {X_test.shape[0]:,} registros")
    
    return model, X_train, X_test, y_test

def create_shap_explainer(model, X_train):
    """Crea el explainer de SHAP."""
    print_separator("CREANDO EXPLAINER DE SHAP")
    
    print("Usando TreeExplainer (optimizado para Random Forest)...")
    explainer = shap.TreeExplainer(model)
    print("Explainer creado exitosamente.")
    
    return explainer

def find_examples(X_test, y_test, model):
    """Encuentra ejemplos específicos para explicar."""
    print_separator("BUSCANDO EJEMPLOS PARA EXPLICAR")
    
    # Obtener predicciones
    y_pred = model.predict(X_test.values)
    
    # Encontrar índices de ejemplos correctamente clasificados
    suspicious_mask = (y_test == 1) & (y_pred == 1)
    normal_mask = (y_test == 0) & (y_pred == 0)
    
    suspicious_indices = X_test.index[suspicious_mask].tolist()
    normal_indices = X_test.index[normal_mask].tolist()
    
    # Seleccionar ejemplos
    suspicious_idx = suspicious_indices[0] if suspicious_indices else None
    normal_idx = normal_indices[0] if normal_indices else None
    
    print(f"Ejemplo sospechoso seleccionado: índice {suspicious_idx}")
    print(f"Ejemplo normal seleccionado: índice {normal_idx}")
    
    return suspicious_idx, normal_idx

def explain_instance(explainer, X_test, idx, instance_type, model):
    """Explica una instancia específica."""
    print(f"\nExplicando instancia {instance_type} (índice {idx})...")
    
    # Obtener la instancia
    instance = X_test.loc[[idx]]
    
    # Calcular valores SHAP
    shap_values_all = explainer.shap_values(instance)
    
    # Debug: ver estructura
    print(f"  Tipo de shap_values_all: {type(shap_values_all)}")
    if isinstance(shap_values_all, list):
        print(f"  Longitud de la lista: {len(shap_values_all)}")
        print(f"  Forma del primer elemento: {shap_values_all[0].shape}")
        print(f"  Forma del segundo elemento: {shap_values_all[1].shape}")
        shap_values = shap_values_all[1]  # Clase positiva
        expected_value = explainer.expected_value[1]
    else:
        print(f"  Forma de shap_values_all: {shap_values_all.shape}")
        # Manejar diferentes formas posibles
        if len(shap_values_all.shape) == 3:
            # Forma (1, n_features, n_classes) - tomar primera instancia, clase 1
            shap_values = shap_values_all[0, :, 1]
        elif len(shap_values_all.shape) == 2 and shap_values_all.shape[1] == 2:
            # Forma (n_features, n_classes) - tomar clase 1
            shap_values = shap_values_all[:, 1]
        else:
            shap_values = shap_values_all
        
        expected_value = explainer.expected_value[1] if hasattr(explainer.expected_value, '__len__') else explainer.expected_value
    
    # Ya no necesitamos verificar si es 2D porque lo manejamos arriba
    print(f"  Forma final de shap_values: {shap_values.shape}")
    print(f"  Número de features: {len(instance.columns)}")
    
    # Predicción y probabilidad
    prediction = model.predict(instance)[0]
    proba = model.predict_proba(instance)[0]
    
    print(f"  Predicción: {'Sospechoso' if prediction == 1 else 'Normal'}")
    print(f"  Probabilidad sospechoso: {proba[1]:.4f}")
    
    # Crear bar plot como alternativa más simple
    plt.figure(figsize=(10, 8))
    
    # Preparar datos para el plot
    feature_names = instance.columns.tolist()
    
    # Verificar que las dimensiones coincidan
    if len(shap_values) != len(feature_names):
        print(f"  ADVERTENCIA: Dimensiones no coinciden - shap_values: {len(shap_values)}, features: {len(feature_names)}")
        # Ajustar si es necesario
        min_len = min(len(shap_values), len(feature_names))
        shap_values = shap_values[:min_len]
        feature_names = feature_names[:min_len]
    
    # Convertir a numpy array si no lo es
    shap_values = np.array(shap_values)
    
    # Ordenar por valor absoluto SHAP
    abs_shap = np.abs(shap_values)
    sorted_idx = np.argsort(abs_shap)[::-1]
    
    # Tomar top 15 o menos si no hay tantas features
    n_features = min(15, len(sorted_idx))
    sorted_idx = sorted_idx[:n_features]
    
    # Obtener los valores y nombres ordenados
    sorted_shap_values = shap_values[sorted_idx]
    sorted_feature_names = [feature_names[int(i)] for i in sorted_idx]
    
    # Crear índices para el plot
    y_pos = np.arange(len(sorted_shap_values))
    
    # Crear bar plot horizontal
    plt.barh(y_pos, sorted_shap_values, 
             color=['red' if x > 0 else 'blue' for x in sorted_shap_values])
    plt.yticks(y_pos, sorted_feature_names)
    plt.xlabel('Impacto SHAP (rojo=sospechoso, azul=normal)')
    plt.title(f'Top {n_features} Features - Instancia {instance_type.capitalize()}')
    plt.tight_layout()
    
    # Guardar plot
    plot_path = SHAP_DIR / f'force_plot_{instance_type}.png'
    plt.savefig(plot_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"  Force plot guardado en: {plot_path}")
    
    # Mostrar top features para esta instancia
    print(f"\n  Top 10 features que influyen en la predicción:")
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'shap_value': shap_values,
        'feature_value': instance.iloc[0].values[:len(feature_names)]
    })
    feature_importance['abs_shap'] = np.abs(feature_importance['shap_value'])
    feature_importance = feature_importance.sort_values('abs_shap', ascending=False)
    
    for idx_feat, row in feature_importance.head(10).iterrows():
        direction = "→ sospechoso" if row['shap_value'] > 0 else "→ normal"
        print(f"    {row['feature']}: {row['feature_value']:.4f} (SHAP: {row['shap_value']:.4f} {direction})")
    
    return shap_values

def create_summary_plot(explainer, X_test, model):
    """Crea el summary plot global."""
    print_separator("CREANDO SUMMARY PLOT GLOBAL")
    
    print("Calculando valores SHAP para todo el conjunto de test...")
    print("(Esto puede tardar unos momentos...)")
    
    # Limitar a una muestra si el dataset es muy grande
    sample_size = min(1000, len(X_test))
    X_sample = X_test.sample(n=sample_size, random_state=RANDOM_STATE)
    
    # Calcular SHAP values
    shap_values = explainer.shap_values(X_sample)
    
    # Para clasificación binaria
    if isinstance(shap_values, list):
        shap_values = shap_values[1]
    
    # Crear summary plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(
        shap_values, 
        X_sample,
        show=False
    )
    
    # Guardar plot
    plot_path = SHAP_DIR / 'summary_plot.png'
    plt.savefig(plot_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"Summary plot guardado en: {plot_path}")
    print(f"(Basado en {sample_size} muestras del test set)")
    
    return shap_values

def interpret_results():
    """Proporciona interpretación de los resultados."""
    print_separator("INTERPRETACIÓN DE RESULTADOS")
    
    print("""
INTERPRETACIÓN DE LOS GRÁFICOS SHAP:

1. FORCE PLOTS (Instancias individuales):
   - Muestran cómo cada feature contribuye a la predicción
   - Rojo = empuja hacia clase sospechosa (1)
   - Azul = empuja hacia clase normal (0)
   - El ancho representa la magnitud de la contribución

2. SUMMARY PLOT (Global):
   - Muestra las features más importantes en general
   - Cada punto es una instancia
   - Color rojo = valor alto de la feature
   - Color azul = valor bajo de la feature
   - Posición horizontal = impacto SHAP (izq=normal, der=sospechoso)

3. HALLAZGOS CLAVE:
   - Las features relacionadas con puertos tienen gran impacto
   - Los flags binarios (has_dns, has_http) son importantes
   - Las frecuencias de IP normalizadas influyen en la decisión
   - La hora del día puede ser un factor relevante
""")

def main():
    """Función principal para aplicar SHAP."""
    # Configurar output logger
    output_file = SHAP_DIR / 'apply_shap_output.txt'
    sys.stdout = OutputLogger(str(output_file))
    
    print_separator("ANÁLISIS DE EXPLICABILIDAD CON SHAP")
    
    # Cargar modelo y datos
    model, X_train, X_test, y_test = load_model_and_data()
    
    # Crear explainer
    explainer = create_shap_explainer(model, X_train)
    
    # Encontrar ejemplos
    suspicious_idx, normal_idx = find_examples(X_test, y_test, model)
    
    # Explicar instancia sospechosa
    if suspicious_idx is not None:
        print_separator("EXPLICACIÓN: INSTANCIA SOSPECHOSA")
        explain_instance(explainer, X_test, suspicious_idx, "suspicious", model)
    
    # Explicar instancia normal
    if normal_idx is not None:
        print_separator("EXPLICACIÓN: INSTANCIA NORMAL")
        explain_instance(explainer, X_test, normal_idx, "normal", model)
    
    # Crear summary plot
    create_summary_plot(explainer, X_test, model)
    
    # Interpretar resultados
    interpret_results()
    
    print_separator("PROCESO COMPLETADO")
    print("\nAnálisis SHAP completado exitosamente.")
    print("Gráficos guardados en results/shap_plots/")
    
    # Cerrar logger
    sys.stdout.close()
    sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    main()