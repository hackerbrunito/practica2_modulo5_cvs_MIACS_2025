#!/usr/bin/env python3
"""
Script para crear la estructura completa del proyecto M5T2_MIACS_2025.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

from pathlib import Path

def create_project_structure():
    """Crea toda la estructura de directorios del proyecto."""
    
    # Directorio base (el script se ejecuta desde la raíz del proyecto)
    base_dir = Path('.')
    
    # Estructura de directorios
    directories = [
        'data',
        'scripts',
        'results',
        'results/exploratory',
        'results/shap_plots',
        'results/privacy_analysis',
        'models',
        'reports'
    ]
    
    # Crear directorios
    print("Creando estructura de directorios...")
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Crear .gitignore
    print("Creando .gitignore...")
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
.ipynb_checkpoints/
"""
    
    gitignore_path = base_dir / '.gitignore'
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)

def main():
    """Función principal."""
    create_project_structure()

if __name__ == "__main__":
    main()