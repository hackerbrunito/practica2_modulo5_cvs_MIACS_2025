#!/usr/bin/env python3
"""
Script para configurar el entorno virtual con UV.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import subprocess
import sys
from pathlib import Path

def find_python_versions():
    """Busca versiones de Python instaladas en el sistema."""
    print("Buscando versiones de Python instaladas...")
    
    versions = []
    # Buscar Python 3.8 a 3.12
    for minor in range(8, 13):
        version = f"3.{minor}"
        try:
            result = subprocess.run(
                [f"python{version}", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                versions.append(version)
        except FileNotFoundError:
            continue
    
    # También intentar con python3
    try:
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output_version = result.stdout.strip().split()[-1]
            base_version = ".".join(output_version.split(".")[:2])
            if base_version not in versions:
                versions.append(base_version)
    except FileNotFoundError:
        pass
    
    return versions

def select_python_version(versions):
    """Permite al usuario seleccionar una versión de Python."""
    print(f"Versiones disponibles: {versions}")
    
    while True:
        selected = input("Selecciona una versión: ")
        if selected in versions:
            return selected
        print("Versión no válida. Intenta de nuevo.")

def create_requirements():
    """Crea el archivo requirements.txt."""
    print("Creando requirements.txt...")
    
    requirements_content = """pandas==2.2.3
numpy==2.1.3
scikit-learn==1.5.2
shap==0.46.0
matplotlib==3.9.2
seaborn==0.13.2
pyyaml==6.0.2"""
    
    base_dir = Path(__file__).parent.parent
    req_path = base_dir / 'requirements.txt'
    
    with open(req_path, 'w') as f:
        f.write(requirements_content)

def create_virtual_env(version):
    """Crea el entorno virtual con UV."""
    print(f"Creando .venv con Python {version}...")
    
    base_dir = Path(__file__).parent.parent
    
    # Crear entorno virtual con uv
    subprocess.run(
        ["uv", "venv", "--python", version],
        cwd=base_dir,
        check=True
    )

def install_dependencies():
    """Instala las dependencias usando UV."""
    print("Activando entorno con source...")
    print("Instalando dependencias...")
    
    base_dir = Path(__file__).parent.parent
    
    # Instalar con uv pip
    subprocess.run(
        ["uv", "pip", "install", "-r", "requirements.txt"],
        cwd=base_dir,
        check=True
    )

def main():
    """Función principal."""
    versions = find_python_versions()
    
    if not versions:
        print("No se encontraron versiones de Python instaladas.")
        sys.exit(1)
    
    selected_version = select_python_version(versions)
    create_requirements()
    create_virtual_env(selected_version)
    install_dependencies()
    
    print("\nEntorno virtual creado exitosamente.")
    print("Para activarlo usa: source .venv/bin/activate")

if __name__ == "__main__":
    main()