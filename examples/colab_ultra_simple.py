"""
⚡ YT-WHISPER-SCRIBE - VERSION ULTRA-SIMPLE POUR COLAB
Configuration garantie sans erreur, compatible avec tous les environnements
"""

print("⚡ YT-WHISPER-SCRIBE - SETUP ULTRA-SIMPLE")
print("=" * 50)

# === CONFIGURATION DIRECTE ===
import subprocess
import os
from pathlib import Path

def setup_project():
    """Configuration directe sans dépendance externe."""
    
    print("🔧 Configuration en cours...")
    
    try:
        # 1. Clone du projet
        if not os.path.exists('/content/yt-whisper-scribe'):
            print("📥 Clonage du projet...")
            subprocess.run([
                'git', 'clone', 
                'https://github.com/Jojo4911/yt-whisper-scribe.git',
                '/content/yt-whisper-scribe'
            ], check=True)
            print("✅ Projet cloné")
        else:
            print("✅ Projet déjà présent")
        
        # 2. Changement de dossier
        os.chdir('/content/yt-whisper-scribe')
        
        # 3. Installation système
        print("📦 Installation ffmpeg...")
        subprocess.run(['apt-get', 'update', '-qq'], check=True)
        subprocess.run(['apt-get', 'install', '-y', 'ffmpeg'], check=True)
        
        # 4. Installation Python
        print("🐍 Installation des dépendances...")
        subprocess.run(['pip', 'install', '-r', 'requirements.txt', '--quiet'], check=True)
        
        # 5. PyTorch CUDA (optionnel)
        try:
            import torch
            if not torch.cuda.is_available():
                print("🔥 Installation PyTorch CUDA...")
                subprocess.run([
                    'pip', 'install', 'torch', 'torchvision', 'torchaudio',
                    '--index-url', 'https://download.pytorch.org/whl/cu121', '--quiet'
                ], check=True)
        except ImportError:
            print("🔥 Installation PyTorch CUDA...")
            subprocess.run([
                'pip', 'install', 'torch', 'torchvision', 'torchaudio',
                '--index-url', 'https://download.pytorch.org/whl/cu121', '--quiet'
            ], check=True)
        
        print("✅ Configuration terminée!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def transcribe_video(
    url, 
    model="turbo", 
    output_format="srt", 
    language="en",
    use_cookies=True
):
    """Fonction de transcription simple et robuste."""
    
    # Vérification du projet
    if not os.path.exists('/content/yt-whisper-scribe'):
        print("⚠️  Projet non configuré. Configuration automatique...")
        if not setup_project():
            return None
    
    os.chdir('/content/yt-whisper-scribe')
    
    print(f"🎬 Transcription: {url}")
    print(f"📊 Paramètres: {model} | {output_format} | {language}")
    
    # Construction de la commande
    cmd = [
        'python', 'scripts/transcribe.py', url,
        '--model', model,
        '--output_format', output_format,
        '--language', language,
        '--device', 'auto',
        '--output_dir', 'data',
        '--verbose'
    ]
    
    # Gestion des cookies
    if use_cookies:
        cookies_paths = [
            '/content/drive/MyDrive/yt-whisper-private/cookies_youtube.txt',
            '/content/cookies_youtube.txt',
            '/content/cookies.txt',
            'data/cookies.txt'
        ]
        
        for cookie_path in cookies_paths:
            if os.path.exists(cookie_path):
                cmd.extend(['--cookies-file', cookie_path])
                print(f"🍪 Cookies trouvés: {Path(cookie_path).name}")
                break
        else:
            print("⚠️  Pas de cookies - Vidéos publiques seulement")
    
    # Exécution
    print("\n🚀 Début de la transcription...")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Transcription réussie!")
        
        # Recherche du fichier généré
        data_dir = Path('data')
        if data_dir.exists():
            files = list(data_dir.glob(f"*.{output_format}"))
            if files:
                latest = max(files, key=lambda p: p.stat().st_mtime)
                print(f"📁 Fichier: {latest}")
                
                # Aperçu
                try:
                    with open(latest, 'r', encoding='utf-8') as f:
                        content = f.read()
                        preview = content[:300] + "..." if len(content) > 300 else content
                        print("\n📄 Aperçu:")
                        print("-" * 30)
                        print(preview)
                        print("-" * 30)
                except:
                    pass
                
                return str(latest)
        
        print("⚠️  Fichier non trouvé")
        return None
    else:
        print("❌ Échec de la transcription")
        return None

def upload_and_clean_cookies():
    """Guide pour nettoyer les cookies."""
    print("🧹 NETTOYAGE DES COOKIES")
    print("\n1. Uploadez votre cookies.txt complet via l'interface Colab")
    print("2. Exécutez cette fonction pour nettoyer automatiquement")
    
    # Recherche du fichier uploadé
    potential_files = ['/content/cookies.txt', '/content/cookies_complets.txt']
    
    input_file = None
    for file_path in potential_files:
        if os.path.exists(file_path):
            input_file = file_path
            break
    
    if not input_file:
        print("❌ Aucun fichier cookies.txt trouvé dans /content/")
        return False
    
    print(f"📁 Fichier détecté: {input_file}")
    
    # Nettoyage
    os.chdir('/content/yt-whisper-scribe')
    output_file = '/content/cookies_youtube_clean.txt'
    
    try:
        result = subprocess.run([
            'python', 'scripts/clean_cookies.py', input_file, output_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Cookies nettoyés!")
            print(result.stdout)
            
            # Sauvegarde dans Drive si disponible
            drive_path = '/content/drive/MyDrive/yt-whisper-private/cookies_youtube.txt'
            if os.path.exists('/content/drive'):
                try:
                    os.makedirs(os.path.dirname(drive_path), exist_ok=True)
                    subprocess.run(['cp', output_file, drive_path], check=True)
                    print(f"💾 Sauvegardé dans Drive: {drive_path}")
                except:
                    print("⚠️  Sauvegarde Drive échouée")
            
            return True
        else:
            print(f"❌ Erreur: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def check_system():
    """Vérification rapide du système."""
    print("🔍 VÉRIFICATION DU SYSTÈME")
    print("-" * 30)
    
    # GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu = torch.cuda.get_device_name(0)
            print(f"✅ GPU: {gpu}")
        else:
            print("⚠️  GPU: Non disponible")
    except:
        print("❌ PyTorch: Non installé")
    
    # FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        if result.returncode == 0:
            print("✅ ffmpeg: Disponible")
        else:
            print("❌ ffmpeg: Erreur")
    except:
        print("❌ ffmpeg: Non trouvé")
    
    # Projet
    if os.path.exists('/content/yt-whisper-scribe'):
        print("✅ Projet: Configuré")
        
        # Scripts essentiels
        script_path = '/content/yt-whisper-scribe/scripts/transcribe.py'
        if os.path.exists(script_path):
            print("  ✅ scripts/transcribe.py")
        else:
            print("  ❌ scripts/transcribe.py")
            
        glossary_path = '/content/yt-whisper-scribe/SWOOD_Glossary.json'
        if os.path.exists(glossary_path):
            print("  ✅ SWOOD_Glossary.json")
        else:
            print("  ❌ SWOOD_Glossary.json")
    else:
        print("❌ Projet: Non configuré")

def demo():
    """Démonstration interactive."""
    print("🎯 DÉMONSTRATION")
    
    check_system()
    
    print("\nExemples d'utilisation:")
    print("transcribe_video('https://youtube.com/watch?v=VIDEO_ID')")
    print("transcribe_video('URL', model='medium', output_format='txt')")
    
    try:
        url = input("\n🎬 URL YouTube (Enter pour ignorer): ").strip()
        if url and ('youtube.com' in url or 'youtu.be' in url):
            return transcribe_video(url)
        else:
            print("ℹ️  Aucune URL - Test avec une URL publique")
            return transcribe_video("https://youtube.com/watch?v=dQw4w9WgXcQ", model="tiny")
    except KeyboardInterrupt:
        print("\n⏹️  Démonstration annulée")
        return None

# === AUTO-CONFIGURATION ===
if __name__ == "__main__":
    try:
        # Détection de Colab
        import google.colab
        print("🔍 Google Colab détecté")
        
        # Configuration automatique si nécessaire
        if not os.path.exists('/content/yt-whisper-scribe'):
            print("🚀 Première utilisation - Configuration...")
            setup_project()
        
        print("\n✨ YT-Whisper-Scribe configuré!")
        print("\n📖 FONCTIONS DISPONIBLES:")
        print("  • transcribe_video(url) - Transcription")
        print("  • upload_and_clean_cookies() - Cookies")  
        print("  • check_system() - Diagnostic")
        print("  • demo() - Test interactif")
        
    except ImportError:
        print("⚠️  Optimisé pour Google Colab")
        setup_project()

# Configuration immédiate
setup_project()