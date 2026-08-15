#!/usr/bin/env python3
"""
Analizador de cabeceras de seguridad HTTP - estilo securityheaders.com
"""
import sys
import requests

# Cabeceras evaluadas y su peso (simplificación del criterio de securityheaders.com)
CHECKS = [
    ("Content-Security-Policy", 20, "Previene XSS e inyección de contenido"),
    ("Strict-Transport-Security", 15, "Fuerza conexiones HTTPS (HSTS)"),
    ("X-Frame-Options", 15, "Previene Clickjacking"),
    ("X-Content-Type-Options", 15, "Previene MIME-sniffing"),
    ("Referrer-Policy", 15, "Controla la información de referencia enviada"),
    ("Permissions-Policy", 10, "Restringe APIs del navegador (cámara, micro, geo...)"),
    ("Cache-Control", 10, "Control de almacenamiento en caché de contenido sensible"),
]

def grade(score):
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B"
    if score >= 60: return "C"
    if score >= 50: return "D"
    if score >= 30: return "E"
    return "F"

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 check_headers.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"\nAnalizando: {url}\n" + "="*60)

    try:
        r = requests.get(url, timeout=10)
    except Exception as e:
        print(f"Error al conectar: {e}")
        sys.exit(1)

    headers = {k.lower(): v for k, v in r.headers.items()}
    total = 0
    max_total = sum(w for _, w, _ in CHECKS)

    print(f"{'Cabecera':<30}{'Estado':<12}{'Descripción'}")
    print("-"*60)

    for name, weight, desc in CHECKS:
        present = name.lower() in headers
        status = " Presente" if present else " Ausente"
        if present:
            total += weight
        print(f"{name:<30}{status:<12}{desc}")

    # Extra: filtración de versión de servidor
    server_header = headers.get("server", "")
    if any(char.isdigit() for char in server_header):
        print(f"\n  El header 'Server' filtra versión: {server_header}")
    else:
        print(f"\n Header 'Server' no filtra versión: {server_header or '(vacío/oculto)'}")

    pct = round((total / max_total) * 100)
    print("\n" + "="*60)
    print(f"PUNTUACIÓN TOTAL: {total}/{max_total} ({pct}%)  -->  NOTA: {grade(pct)}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
