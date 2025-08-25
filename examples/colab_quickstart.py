"""
🚀 QUICKSTART COLAB - YT-Whisper-Scribe
Configuration rapide avec cookies YouTube sécurisés
"""

import os
import subprocess
from pathlib import Path

def setup_yt_whisper_colab():
    """Setup complet pour Google Colab avec cookies sécurisés"""
    
    print("=" * 60)
    print("🚀 YT-WHISPER-SCRIBE - SETUP COLAB")
    print("=" * 60)
    
    # 1. Clone du projet
    print("\n📥 1. Clonage du projet...")
    if not os.path.exists('/content/yt-whisper-scribe'):
        os.system('git clone https://github.com/Jojo4911/yt-whisper-scribe.git')
    
    os.chdir('/content/yt-whisper-scribe')
    print("✅ Projet cloné et actif")
    
    # 2. Installation des dépendances
    print("\n📦 2. Installation des dépendances...")
    os.system('pip install -r requirements.txt --quiet')
    os.system('pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --quiet')
    print("✅ Dépendances installées")
    
    # 3. Vérification GPU
    print("\n🎮 3. Vérification GPU...")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU détecté: {gpu_name}")
        else:
            print("⚠️  CPU seulement (plus lent)")
    except:
        print("⚠️  PyTorch non installé correctement")
    
    # 4. Configuration cookies
    print("\n🍪 4. Configuration des cookies...")
    print("""
MÉTHODES POUR UTILISER LES COOKIES:

A) Upload direct (temporaire):
   - Upload ton fichier cookies_youtube.txt via l'interface Colab
   - Il sera automatiquement détecté dans data/cookies.txt
   
B) Google Drive (persistant):
   from google.colab import drive
   drive.mount('/content/drive')
   # Copie ton fichier dans: /content/drive/My Drive/cookies_youtube.txt
   
C) Variable d'environnement:
   import os
   os.environ['YT_COOKIES_FILE'] = '/chemin/vers/ton/fichier'
    """)
    
    return True

def transcribe_video(url, model="turbo", use_swood_glossary=True, output_format="srt"):
    """Transcrit une vidéo YouTube avec configuration optimisée Colab"""
    
    print(f"\n🎬 Transcription: {url}")
    print(f"📊 Modèle: {model}")
    print(f"📝 Format: {output_format}")
    
    # Construction de la commande
    cmd = [
        "python", "scripts/transcribe.py", url,
        "--model", model,
        "--output_format", output_format,
        "--device", "auto",  # Détection auto GPU/CPU
        "--verbose"
    ]
    
    # Ajout du glossaire SWOOD si demandé
    if use_swood_glossary and os.path.exists("SWOOD_Glossary.json"):
        cmd.extend(["--replace-map", "SWOOD_Glossary.json"])
        print("🔧 Glossaire SWOOD activé")
    
    # Vérification des cookies
    cookies_paths = [
        "/content/yt-whisper-scribe/data/cookies.txt",
        "/content/drive/My Drive/cookies_youtube.txt",
        "/content/cookies.txt"
    ]
    
    for cookie_path in cookies_paths:
        if os.path.exists(cookie_path):
            cmd.extend(["--cookies-file", cookie_path])
            print(f"🍪 Cookies trouvés: {cookie_path}")
            break
    else:
        print("⚠️  Pas de cookies détectés (peut échouer sur certaines vidéos)")
    
    # Exécution
    print("\n" + "="*50)
    print("🚀 DÉBUT TRANSCRIPTION")
    print("="*50)
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    print("\n" + "="*50)
    if result.returncode == 0:
        print("✅ TRANSCRIPTION RÉUSSIE!")
        
        # Affichage des fichiers générés
        data_dir = Path("/content/yt-whisper-scribe/data")
        if data_dir.exists():
            files = list(data_dir.glob(f"*.{output_format}"))
            if files:
                latest_file = max(files, key=os.path.getmtime)
                print(f"📁 Fichier généré: {latest_file}")
                return str(latest_file)
    else:
        print("❌ ÉCHEC DE LA TRANSCRIPTION")
        print("Vérifiez l'URL et la configuration des cookies")
    
    print("="*50)
    return None

def quick_demo():
    """Démonstration rapide"""
    print("\n🎯 DÉMONSTRATION RAPIDE")
    print("Pour utiliser le système:")
    print("""
# 1. Setup initial
setup_yt_whisper_colab()

# 2. Transcription simple
file_path = transcribe_video("https://youtube.com/watch?v=VIDEO_ID")

# 3. Transcription avancée avec SWOOD
file_path = transcribe_video(
    url="https://youtube.com/watch?v=VIDEO_ID",
    model="medium",  # ou "large" pour plus de précision
    use_swood_glossary=True,
    output_format="srt"
)

# 4. Lire le résultat
if file_path:
    with open(file_path, 'r', encoding='utf-8') as f:
        print(f.read()[:500])  # Premiers 500 caractères
    """)

# Exécution automatique si appelé directement
if __name__ == "__main__":
    if 'google.colab' in str(get_ipython()):
        setup_yt_whisper_colab()
        quick_demo()
    else:
        print("⚠️  Ce script est conçu pour Google Colab")