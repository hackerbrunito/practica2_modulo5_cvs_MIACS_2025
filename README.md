# Práctica 2 - Módulo 5: IA Aplicada a la Ciberseguridad

## Español --- (find the English version down below)

### Descripción del Proyecto
Este proyecto implementa un sistema completo de detección de tráfico anómalo en redes utilizando técnicas de Machine Learning, explicabilidad (XAI) y privacidad avanzada. Se aplica el ciclo completo desde el análisis exploratorio hasta la documentación del modelo siguiendo estándares éticos y legales.

### Requisitos del Sistema
- Ubuntu 25 o similar
- Python 3.13+
- UV (gestor de paquetes Python)
- 2GB de espacio en disco
- Dataset: traffic_anonymous.csv (33,902 registros)

### Estructura del Proyecto
```
M5T2_MIACS_2025/
├── data/                    # Datasets
├── scripts/                 # Scripts Python
├── results/                 # Outputs y gráficos
│   ├── exploratory/        # Análisis exploratorio
│   ├── shap_plots/         # Visualizaciones XAI
│   └── privacy_analysis/   # Métricas privacidad
├── models/                  # Modelo entrenado
├── reports/                 # Documentación
└── main.py                  # Orquestador principal
```

### Instalación

1. **Preparar entorno inicial**
   ```bash
   python setup_structure.py
   ```

2. **Configurar entorno virtual**
   ```bash
   cd scripts
   python setup_venv.py
   cd ..
   source .venv/bin/activate
   ```

3. **Crear archivos de configuración**
   ```bash
   cd scripts
   python create_base_files.py
   cd ..
   ```

4. **Copiar dataset**
   - Colocar `traffic_anonymous.csv` en la carpeta `data/`

### Ejecución

**Opción 1: Pipeline completo automático**
```bash
python main.py
```

**Opción 2: Ejecutar scripts individuales**
```bash
cd scripts
python verify_dataset.py
python exploratory_analysis.py
# ... etc
```

### Descripción de Scripts

1. **verify_dataset.py** - Verifica integridad del dataset
2. **exploratory_analysis.py** - Análisis estadístico y visualizaciones
3. **create_target.py** - Genera variable objetivo (suspicious)
4. **feature_engineering.py** - Prepara características para ML
5. **train_model.py** - Entrena RandomForestClassifier
6. **apply_shap.py** - Aplica explicabilidad con SHAP
7. **k_anonymity.py** - Implementa privacidad con k=10
8. **rgpd_analysis.py** - Análisis de cumplimiento legal
9. **model_card.py** - Genera documentación del modelo

### Outputs Generados

- **Datasets procesados**: 
  - `traffic_labeled.csv` - Con etiquetas
  - `traffic_processed.csv` - Con features
  - `traffic_k_anonymous.csv` - Anonimizado

- **Modelo**: 
  - `random_forest_model.pkl` - RF con max_depth=10

- **Visualizaciones**:
  - Gráficos de análisis exploratorio
  - Force plots y summary plot de SHAP
  - Comparativa utilidad vs privacidad

- **Documentación**:
  - Model Card en YAML
  - Análisis RGPD completo
  - Logs detallados de cada proceso

### Métricas del Modelo
- Accuracy: 99.91%
- Precision: 99.40%
- Recall: 98.20%
- F1-Score: 98.80%

---

## English

### Project Description
This project implements a complete network traffic anomaly detection system using Machine Learning techniques, explainability (XAI), and advanced privacy. It applies the complete cycle from exploratory analysis to model documentation following ethical and legal standards.

### System Requirements
- Ubuntu 25 or similar
- Python 3.13+
- UV (Python package manager)
- 2GB disk space
- Dataset: traffic_anonymous.csv (33,902 records)

### Project Structure
```
M5T2_MIACS_2025/
├── data/                    # Datasets
├── scripts/                 # Python scripts
├── results/                 # Outputs and plots
│   ├── exploratory/        # Exploratory analysis
│   ├── shap_plots/         # XAI visualizations
│   └── privacy_analysis/   # Privacy metrics
├── models/                  # Trained model
├── reports/                 # Documentation
└── main.py                  # Main orchestrator
```

### Installation

1. **Setup initial environment**
   ```bash
   python setup_structure.py
   ```

2. **Configure virtual environment**
   ```bash
   cd scripts
   python setup_venv.py
   cd ..
   source .venv/bin/activate
   ```

3. **Create configuration files**
   ```bash
   cd scripts
   python create_base_files.py
   cd ..
   ```

4. **Copy dataset**
   - Place `traffic_anonymous.csv` in `data/` folder

### Execution

**Option 1: Automatic complete pipeline**
```bash
python main.py
```

**Option 2: Run individual scripts**
```bash
cd scripts
python verify_dataset.py
python exploratory_analysis.py
# ... etc
```

### Script Descriptions

1. **verify_dataset.py** - Verifies dataset integrity
2. **exploratory_analysis.py** - Statistical analysis and visualizations
3. **create_target.py** - Creates target variable (suspicious)
4. **feature_engineering.py** - Prepares features for ML
5. **train_model.py** - Trains RandomForestClassifier
6. **apply_shap.py** - Applies explainability with SHAP
7. **k_anonymity.py** - Implements privacy with k=10
8. **rgpd_analysis.py** - Legal compliance analysis
9. **model_card.py** - Generates model documentation

### Generated Outputs

- **Processed datasets**: 
  - `traffic_labeled.csv` - With labels
  - `traffic_processed.csv` - With features
  - `traffic_k_anonymous.csv` - Anonymized

- **Model**: 
  - `random_forest_model.pkl` - RF with max_depth=10

- **Visualizations**:
  - Exploratory analysis plots
  - SHAP force plots and summary plot
  - Utility vs privacy comparison

- **Documentation**:
  - Model Card in YAML
  - Complete GDPR analysis
  - Detailed logs for each process

### Model Metrics
- Accuracy: 99.91%
- Precision: 99.40%
- Recall: 98.20%
- F1-Score: 98.80%

---

**Autor / Author**: Carlos Val Souto  
**Fecha / Date**: Septiembre 2025  
**Máster**: IA Aplicada a la Ciberseguridad