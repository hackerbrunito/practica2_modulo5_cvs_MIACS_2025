#!/usr/bin/env python3
"""
Script para análisis RGPD específico del dataset de tráfico.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import sys
from pathlib import Path

# Importar configuración y utilidades
from config import RESULTS_DIR
from utils import OutputLogger, print_separator

def analyze_personal_data():
    """Identifica y analiza datos personales en el dataset."""
    print_separator("1. IDENTIFICACIÓN DE DATOS PERSONALES")
    
    print("\nDATOS PERSONALES IDENTIFICADOS:")
    
    print("\na) DIRECCIONES IP (Pseudonimizadas)")
    print("   - src_ip_anon y dst_ip_anon")
    print("   - Técnica: Hash SHA-256 truncado a 12 caracteres")
    print("   - Naturaleza: Dato personal según RGPD Art. 4(1)")
    print("   - Razón: Permite identificación indirecta con información adicional")
    print("   - Riesgo: Re-identificación mediante análisis de patrones de tráfico")
    
    print("\nb) CONSULTAS DNS")
    print("   - dns_query: dominios visitados por usuarios")
    print("   - Naturaleza: Perfil de navegación = dato personal")
    print("   - Ejemplo: 'facebook.com', 'gmail.com' revelan hábitos")
    print("   - Riesgo: Creación de perfiles de comportamiento detallados")
    
    print("\nc) USER-AGENT")
    print("   - user_agent: información del navegador y sistema")
    print("   - Naturaleza: Contribuye al fingerprinting del dispositivo")
    print("   - Ejemplo: 'Mozilla/5.0 (Windows NT 10.0; Win64)...'")
    print("   - Riesgo: Combinado con otros datos permite identificación única")
    
    print("\nd) METADATOS DE RED")
    print("   - Puertos, protocolos, timestamps")
    print("   - Naturaleza: Datos de tráfico = datos personales en contexto")
    print("   - Riesgo: Patrones reveladores (ej: puerto 22 = uso de SSH)")

def analyze_pseudonymization_vs_anonymization():
    """Analiza la diferencia entre pseudonimización y anonimización."""
    print_separator("2. PSEUDONIMIZACIÓN VS ANONIMIZACIÓN")
    
    print("\nPSEUDONIMIZACIÓN APLICADA:")
    print("- IPs hasheadas con SHA-256 (12 caracteres)")
    print("- Características:")
    print("  • Proceso determinístico (misma IP → mismo hash)")
    print("  • Sin clave/salt almacenada")
    print("  • Técnicamente irreversible")
    
    print("\nLIMITACIONES:")
    print("- No es verdadera anonimización según RGPD porque:")
    print("  • Ataques de diccionario sobre espacio IPv4 (4.3B direcciones)")
    print("  • Análisis de patrones temporales y de comportamiento")
    print("  • Correlación con logs externos")
    
    print("\nK-ANONIMIDAD APLICADA (k=10):")
    print("- Intento de anonimización mediante generalización")
    print("- Cada registro indistinguible de al menos otros 9")
    print("- PERO: sigue siendo pseudonimización porque:")
    print("  • IPs hasheadas siguen siendo identificadores únicos")
    print("  • DNS queries no generalizadas")
    print("  • User-agents intactos")
    
    print("\nCONCLUSIÓN:")
    print("Dataset pseudonimizado, NO anonimizado")
    print("→ RGPD sigue aplicando completamente")

def analyze_legal_basis():
    """Analiza la base legal para el tratamiento."""
    print_separator("3. BASE LEGAL DEL TRATAMIENTO")
    
    print("\nBASE LEGAL: INTERÉS LEGÍTIMO (Art. 6.1.f RGPD)")
    
    print("\nJUSTIFICACIÓN:")
    print("- Finalidad: Seguridad de la red y detección de amenazas")
    print("- Interés legítimo del responsable en:")
    print("  • Proteger infraestructura IT")
    print("  • Prevenir ciberataques")
    print("  • Cumplir obligaciones de ciberseguridad")
    
    print("\nEVALUACIÓN DE PROPORCIONALIDAD:")
    print("✓ Necesidad: Imprescindible para detectar tráfico malicioso")
    print("✓ Proporcionalidad: Solo datos mínimos de red")
    print("✓ Salvaguardias: Pseudonimización + k-anonimidad")
    print("✗ Riesgo: Perfilado de usuarios legítimos")
    
    print("\nMEDIDAS COMPENSATORIAS NECESARIAS:")
    print("- Minimización: Eliminar DNS/HTTP cuando sea posible")
    print("- Plazo retención: Máximo 6 meses")
    print("- Transparencia: Informar a usuarios")
    print("- Opt-out: Permitir exclusión del análisis")

def analyze_residual_risks():
    """Analiza riesgos residuales post-anonimización."""
    print_separator("4. RIESGOS RESIDUALES POST-ANONIMIZACIÓN")
    
    print("\nRIESGOS IDENTIFICADOS:")
    
    print("\n1. RE-IDENTIFICACIÓN POR ANÁLISIS DE PATRONES")
    print("   - Comportamiento único de navegación")
    print("   - Horarios de conexión regulares")
    print("   - Combinación puerto/protocolo/longitud distintiva")
    print("   - Mitigación: Aumentar k a 20-50")
    
    print("\n2. ATAQUES DE LINKAGE")
    print("   - Cruce con logs públicos (ej: servidores web)")
    print("   - Correlación temporal con eventos conocidos")
    print("   - Mitigación: Generalizar timestamps a ventanas de 15 min")
    
    print("\n3. INFERENCIAS SENSIBLES")
    print("   - DNS a sitios médicos → condición de salud")
    print("   - Puertos específicos → actividades profesionales")
    print("   - Patrones nocturnos → hábitos personales")
    print("   - Mitigación: Eliminar DNS de categorías sensibles")
    
    print("\n4. IDENTIFICACIÓN DE OUTLIERS")
    print("   - is_length_outlier facilita re-identificación")
    print("   - Comportamiento anómalo = más identificable")
    print("   - Mitigación: Eliminar o generalizar outliers")
    
    print("\nRECOMENDACIONES FINALES:")
    print("1. Implementar anonimización verdadera (eliminar IPs)")
    print("2. Agregación temporal (ventanas de 1 hora)")
    print("3. Supresión selectiva de datos sensibles")
    print("4. Evaluación de Impacto (DPIA) obligatoria")

def generate_summary():
    """Genera resumen ejecutivo del análisis."""
    print_separator("RESUMEN EJECUTIVO")
    
    print("\nDATASET: traffic_anonymous.csv")
    print("NATURALEZA: Datos de tráfico de red pseudonimizados")
    print("CLASIFICACIÓN RGPD: Datos personales (NO anonimizados)")
    
    print("\nPRINCIPALES RIESGOS:")
    print("- Re-identificación mediante análisis de patrones")
    print("- Creación de perfiles de comportamiento")
    print("- Revelación de información sensible")
    
    print("\nBASE LEGAL: Interés legítimo en seguridad")
    print("REQUERIMIENTOS: DPIA + medidas técnicas adicionales")
    
    print("\nCONCLUSIÓN:")
    print("El dataset requiere tratamiento como datos personales")
    print("con todas las obligaciones RGPD aplicables.")

def main():
    """Función principal del análisis RGPD."""
    # Configurar output logger
    output_file = RESULTS_DIR / 'rgpd_analysis_output.txt'
    sys.stdout = OutputLogger(str(output_file))
    
    print_separator("ANÁLISIS RGPD - DATASET TRÁFICO DE RED")
    print("Máximo 1 página - Análisis específico del dataset")
    
    # Ejecutar análisis
    analyze_personal_data()
    analyze_pseudonymization_vs_anonymization()
    analyze_legal_basis()
    analyze_residual_risks()
    generate_summary()
    
    print("\n" + "="*60)
    print("Análisis RGPD completado")
    print("Guardado en: rgpd_analysis_output.txt")
    
    # Cerrar logger
    sys.stdout.close()
    sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    main()