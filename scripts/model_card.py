#!/usr/bin/env python3
"""
Script para generar el Model Card del modelo de detección de tráfico.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import yaml
from pathlib import Path

# Importar configuración
from config import REPORTS_DIR

def create_model_card():
    """Crea el model card en formato YAML."""
    
    model_card = {
        'model_details': {
            'name': 'Traffic Anomaly Detector',
            'version': '1.0',
            'date': '2025-09',
            'type': 'RandomForestClassifier',
            'parameters': {
                'max_depth': 10,
                'n_estimators': 100,
                'random_state': 42
            }
        },
        
        'intended_use': {
            'primary_purpose': 'Detectar tráfico de red sospechoso',
            'users': ['Analistas SOC', 'Investigadores seguridad'],
            'out_of_scope': ['Tráfico cifrado', 'Protocolos no TCP/UDP']
        },
        
        'training_data': {
            'dataset': 'traffic_processed.csv',
            'records': 33902,
            'features': 20,
            'target_distribution': {
                'normal': '75%',
                'suspicious': '25%'
            }
        },
        
        'metrics': {
            'accuracy': 0.9991,
            'precision': 0.9940,
            'recall': 0.9820,
            'f1_score': 0.9880
        },
        
        'ethical_considerations': [
            'Sesgo hacia malware conocido',
            'No detecta amenazas zero-day'
        ],
        
        'privacy_protection': [
            'IPs pseudonimizadas con SHA-256',
            'k-anonimidad aplicada con k=10'
        ]
    }
    
    # Guardar model card
    output_path = REPORTS_DIR / 'model_card.yaml'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(model_card, f, 
                 default_flow_style=False, 
                 allow_unicode=True,
                 sort_keys=False)
    
    print(f"Model Card generado en: {output_path}")
    
    # Mostrar contenido
    print("\nContenido del Model Card:")
    print("="*60)
    with open(output_path, 'r', encoding='utf-8') as f:
        print(f.read())
    print("="*60)

def main():
    """Función principal."""
    print("="*60)
    print("GENERACIÓN DE MODEL CARD")
    print("="*60)
    
    create_model_card()
    
    print("\nModel Card completado exitosamente.")
    print("Formato YAML estándar para documentación del modelo.")

if __name__ == "__main__":
    main()