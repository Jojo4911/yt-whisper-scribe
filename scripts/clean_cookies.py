#!/usr/bin/env python3
"""
Utilitaire pour nettoyer un fichier cookies.txt et ne garder que les domaines YouTube.
Usage: python scripts/clean_cookies.py input_cookies.txt output_cookies.txt
"""

import argparse
import sys
from pathlib import Path


def clean_cookies_for_youtube(input_file: Path, output_file: Path) -> None:
    """Filtre les cookies pour ne garder que ceux de YouTube."""
    youtube_domains = {
        'youtube.com',
        '.youtube.com',
        'www.youtube.com',
        'm.youtube.com',
        'googlevideo.com',
        '.googlevideo.com'
    }
    
    if not input_file.exists():
        print(f"Erreur: Le fichier {input_file} n'existe pas.")
        sys.exit(1)
    
    kept_lines = []
    total_lines = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                total_lines += 1
                line = line.strip()
                
                # Garder les commentaires et lignes vides
                if line.startswith('#') or not line:
                    kept_lines.append(line)
                    continue
                
                # Parser la ligne de cookie (format Netscape)
                parts = line.split('\t')
                if len(parts) >= 1:
                    domain = parts[0]
                    # Garder seulement les domaines YouTube
                    if any(yt_domain in domain for yt_domain in youtube_domains):
                        kept_lines.append(line)
        
        # Écrire le fichier nettoyé
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in kept_lines:
                f.write(line + '\n')
        
        print(f"✅ Cookies nettoyés: {len(kept_lines)}/{total_lines} lignes conservées")
        print(f"📁 Fichier sauvegardé: {output_file}")
        print("🔒 Seuls les cookies YouTube ont été conservés")
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Nettoie un fichier cookies.txt pour ne garder que les cookies YouTube"
    )
    parser.add_argument("input", help="Fichier cookies.txt d'entrée")
    parser.add_argument("output", help="Fichier cookies.txt de sortie nettoyé")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    clean_cookies_for_youtube(input_path, output_path)


if __name__ == "__main__":
    main()