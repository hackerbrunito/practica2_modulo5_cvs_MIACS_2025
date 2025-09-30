#!/usr/bin/env python3
"""
Script para análisis exploratorio del dataset de tráfico.
Autor: Carlos Val Souto
Fecha: Septiembre 2025
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Importar configuración y utilidades
from config import DATASET_ORIGINAL, EXPLORATORY_DIR
from utils import OutputLogger, print_separator, load_dataset

def analyze_ports(df):
    """Analiza la distribución de puertos para identificar maliciosos."""
    print_separator("ANÁLISIS DE PUERTOS")
    
    # Top 20 puertos más frecuentes como destino
    dst_ports = df['dst_port'].value_counts().head(20)
    print("\nTop 20 puertos destino más frecuentes:")
    for port, count in dst_ports.items():
        print(f"  Puerto {int(port)}: {count} conexiones")
    
    # Puertos conocidos de malware
    malware_ports = [137, 4444, 6667, 31337, 12345, 1337, 5555]
    print("\nTráfico en puertos conocidos de malware:")
    for port in malware_ports:
        count = len(df[df['dst_port'] == port])
        if count > 0:
            print(f"  Puerto {port}: {count} conexiones")
    
    # Crear gráfico de distribución de puertos
    plt.figure(figsize=(12, 6))
    dst_ports.plot(kind='bar')
    plt.title('Top 20 Puertos Destino Más Frecuentes')
    plt.xlabel('Puerto')
    plt.ylabel('Número de Conexiones')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(EXPLORATORY_DIR / 'port_distribution.png')
    plt.close()

def analyze_dns_queries(df):
    """Analiza las consultas DNS para identificar TLDs sospechosos."""
    print_separator("ANÁLISIS DE CONSULTAS DNS")
    
    # Filtrar registros con consultas DNS
    dns_df = df[df['dns_query'].notna()]
    print(f"\nTotal de consultas DNS: {len(dns_df)}")
    
    # Extraer TLDs
    tlds = []
    for query in dns_df['dns_query'].dropna():
        parts = str(query).split('.')
        if len(parts) > 1:
            tld = parts[-1].lower()
            tlds.append(tld)
    
    tld_counts = Counter(tlds)
    print("\nTop 15 TLDs en consultas DNS:")
    for tld, count in tld_counts.most_common(15):
        print(f"  .{tld}: {count} consultas")
    
    # TLDs sospechosos
    suspicious_tlds = ['tk', 'ml', 'ga', 'biz', 'cn', 'ru', 'cc']
    print("\nConsultas DNS con TLDs sospechosos:")
    for tld in suspicious_tlds:
        count = tld_counts.get(tld, 0)
        if count > 0:
            print(f"  .{tld}: {count} consultas")
    
    # Longitud de dominios (posible DGA)
    domain_lengths = [len(str(query)) for query in dns_df['dns_query'].dropna()]
    
    plt.figure(figsize=(10, 6))
    plt.hist(domain_lengths, bins=30, edgecolor='black')
    plt.axvline(x=40, color='red', linestyle='--', label='Umbral sospechoso (>40 chars)')
    plt.title('Distribución de Longitud de Dominios DNS')
    plt.xlabel('Longitud del Dominio')
    plt.ylabel('Frecuencia')
    plt.legend()
    plt.tight_layout()
    plt.savefig(EXPLORATORY_DIR / 'dns_domain_lengths.png')
    plt.close()
    
    print(f"\nDominios con más de 40 caracteres: {sum(1 for l in domain_lengths if l > 40)}")

def analyze_http_traffic(df):
    """Analiza el tráfico HTTP para identificar anomalías."""
    print_separator("ANÁLISIS DE TRÁFICO HTTP")
    
    # Filtrar registros con datos HTTP
    http_df = df[df['http_host'].notna() | df['http_path'].notna()]
    print(f"\nTotal de registros HTTP: {len(http_df)}")
    
    # Registros HTTP sin User-Agent
    http_no_ua = http_df[http_df['user_agent'].isna()]
    print(f"Registros HTTP sin User-Agent: {len(http_no_ua)} ({len(http_no_ua)/len(http_df)*100:.1f}%)")
    
    # Paths más comunes
    print("\nTop 10 paths HTTP más comunes:")
    path_counts = http_df['http_path'].value_counts().head(10)
    for path, count in path_counts.items():
        print(f"  {path}: {count}")

def analyze_packet_lengths(df):
    """Analiza la distribución de longitudes de paquetes."""
    print_separator("ANÁLISIS DE LONGITUDES DE PAQUETES")
    
    print("\nEstadísticas de longitud de paquetes:")
    print(f"  Media: {df['length'].mean():.2f}")
    print(f"  Mediana: {df['length'].median():.2f}")
    print(f"  Desviación estándar: {df['length'].std():.2f}")
    print(f"  Mínimo: {df['length'].min()}")
    print(f"  Máximo: {df['length'].max()}")
    
    # Paquetes extremadamente grandes con puerto alto
    large_packets = df[df['length'] > df['length'].quantile(0.99)]
    high_port_large = large_packets[large_packets['dst_port'] > 10000]
    print(f"\nPaquetes muy grandes (>P99) con puerto alto (>10000): {len(high_port_large)}")
    
    # Gráfico de distribución
    plt.figure(figsize=(10, 6))
    plt.hist(df['length'], bins=50, edgecolor='black', alpha=0.7)
    plt.axvline(x=df['length'].quantile(0.99), color='red', linestyle='--', 
                label=f'P99: {df["length"].quantile(0.99):.0f}')
    plt.title('Distribución de Longitudes de Paquetes')
    plt.xlabel('Longitud del Paquete')
    plt.ylabel('Frecuencia')
    plt.xlim(0, df['length'].quantile(0.999))
    plt.legend()
    plt.tight_layout()
    plt.savefig(EXPLORATORY_DIR / 'packet_length_distribution.png')
    plt.close()

def analyze_temporal_patterns(df):
    """Analiza patrones temporales en el tráfico."""
    print_separator("ANÁLISIS TEMPORAL")
    
    # Convertir timestamp a datetime
    df['datetime'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['datetime'].dt.hour
    
    # Distribución por hora
    hourly_traffic = df['hour'].value_counts().sort_index()
    
    plt.figure(figsize=(10, 6))
    hourly_traffic.plot(kind='bar')
    plt.title('Distribución de Tráfico por Hora del Día')
    plt.xlabel('Hora')
    plt.ylabel('Número de Conexiones')
    plt.tight_layout()
    plt.savefig(EXPLORATORY_DIR / 'hourly_traffic_distribution.png')
    plt.close()
    
    print("\nDistribución de tráfico por hora:")
    for hour, count in hourly_traffic.items():
        print(f"  Hora {hour}: {count} conexiones")

def main():
    """Función principal del análisis exploratorio."""
    # Configurar output logger
    output_file = EXPLORATORY_DIR / 'exploratory_analysis_output.txt'
    sys.stdout = OutputLogger(str(output_file))
    
    print_separator("ANÁLISIS EXPLORATORIO DE DATOS")
    
    # Cargar dataset
    df = load_dataset(DATASET_ORIGINAL, "Dataset original de tráfico")
    
    # Ejecutar análisis
    analyze_ports(df)
    analyze_dns_queries(df)
    analyze_http_traffic(df)
    analyze_packet_lengths(df)
    analyze_temporal_patterns(df)
    
    print_separator("RESUMEN DE HALLAZGOS PARA ETIQUETADO")
    print("\nPatrones identificados para crear reglas de etiquetado:")
    print("1. Puerto 137 (NetBIOS) con tráfico significativo")
    print("2. Puertos de malware conocidos detectados (4444, 6667, 31337)")
    print("3. TLDs sospechosos en DNS (.tk, .ml, .ga, .biz, .cn)")
    print("4. Tráfico HTTP sin User-Agent (posible bot/malware)")
    print("5. Dominios DNS muy largos (>40 chars, posible DGA)")
    print("6. Paquetes extremadamente grandes con puerto alto")
    
    print("\nAnálisis exploratorio completado.")
    print("Gráficos guardados en results/exploratory/")
    
    # Cerrar logger
    sys.stdout.close()
    sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    main()