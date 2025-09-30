#!/usr/bin/env python3
"""
Orquestador principal para ejecutar todo el pipeline de la práctica.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import sys
from pathlib import Path

# Agregar scripts al path
sys.path.append(str(Path(__file__).parent / 'scripts'))

# Importar todos los módulos
from scripts import verify_dataset
from scripts import exploratory_analysis
from scripts import create_target
from scripts import feature_engineering
from scripts import train_model
from scripts import apply_shap
from scripts import k_anonymity
from scripts import rgpd_analysis
from scripts import model_card

def print_header(step_name):
    """Imprime encabezado para cada paso."""
    print("\n" + "="*60)
    print(f"EJECUTANDO: {step_name}")
    print("="*60 + "\n")

def run_pipeline():
    """Ejecuta todo el pipeline en orden."""
    print("="*60)
    print("PIPELINE COMPLETO - PRÁCTICA 2 M5T2")
    print("="*60)
    
    try:
        # Paso 0.5: Verificar dataset
        print_header("Paso 0.5 - Verificar Dataset")
        verify_dataset.main()
        print("✓ Completado")
        
        # Paso 1: Análisis exploratorio
        print_header("Paso 1 - Análisis Exploratorio")
        exploratory_analysis.main()
        print("✓ Completado")
        
        # Paso 2: Crear variable objetivo
        print_header("Paso 2 - Crear Variable Objetivo")
        create_target.main()
        print("✓ Completado")
        
        # Paso 3: Feature engineering
        print_header("Paso 3 - Feature Engineering")
        feature_engineering.main()
        print("✓ Completado")
        
        # Paso 4: Entrenar modelo
        print_header("Paso 4 - Entrenar Modelo")
        train_model.main()
        print("✓ Completado")
        
        # Paso 5: Aplicar SHAP
        print_header("Paso 5 - Aplicar SHAP (XAI)")
        apply_shap.main()
        print("✓ Completado")
        
        # Paso 6: K-anonimidad
        print_header("Paso 6 - Aplicar K-Anonimidad")
        k_anonymity.main()
        print("✓ Completado")
        
        # Paso 7: Análisis RGPD
        print_header("Paso 7 - Análisis RGPD")
        rgpd_analysis.main()
        print("✓ Completado")
        
        # Paso 8: Model Card
        print_header("Paso 8 - Generar Model Card")
        model_card.main()
        print("✓ Completado")
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETADO EXITOSAMENTE")
        print("="*60)
        
        print("\nResumen de outputs generados:")
        print("- Datasets: data/traffic_labeled.csv, traffic_processed.csv, traffic_k_anonymous.csv")
        print("- Modelo: models/random_forest_model.pkl")
        print("- Gráficos: results/exploratory/, results/shap_plots/, results/privacy_analysis/")
        print("- Reportes: reports/model_card.yaml")
        print("- Outputs completos: results/*_output.txt")
        
    except Exception as e:
        print(f"\nERROR en el pipeline: {str(e)}")
        print("Revisa los logs para más detalles.")
        return 1
    
    return 0

def main():
    """Función principal."""
    print("\nEste script ejecutará TODO el pipeline de la práctica.")
    print("Asegúrate de que:")
    print("1. El dataset traffic_anonymous.csv está en data/")
    print("2. El entorno virtual está activado")
    print("3. Todas las dependencias están instaladas")
    
    response = input("\n¿Deseas continuar? (s/n): ")
    
    if response.lower() == 's':
        return run_pipeline()
    else:
        print("Pipeline cancelado.")
        return 0

if __name__ == "__main__":
    sys.exit(main())