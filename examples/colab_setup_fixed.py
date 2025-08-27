"""
🚀 YT-WHISPER-SCRIBE - Configuration Colab CORRIGÉE
Version sans erreur de syntaxe, testée pour Google Colab
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# === CONFIGURATION ===
GITHUB_REPO = "https://github.com/Jojo4911/yt-whisper-scribe.git"
PROJECT_DIR = "/content/yt-whisper-scribe"
COOKIES_SEARCH_PATHS = [
    "/content/drive/MyDrive/yt-whisper-private/cookies_youtube.txt",
    "/content/drive/MyDrive/cookies_youtube.txt", 
    "/content/cookies_youtube.txt",
    "/content/cookies.txt",
    f"{PROJECT_DIR}/data/cookies.txt"
]

def setup_colab_environment(force_reinstall: bool = False):
    """Configure l'environnement Colab avec intégration GitHub directe."""
    
    print("🚀 YT-WHISPER-SCRIBE - SETUP COLAB CORRIGÉ")
    print("=" * 60)
    
    try:
        # 1. Vérification GPU
        print("\n🎮 1. Vérification GPU...")
        _check_gpu_availability()
        
        # 2. Clone/Update du projet depuis GitHub
        print("\n📥 2. Récupération du projet depuis GitHub...")
        success = _setup_project_from_github(force_reinstall)
        if not success:
            return False
        
        # 3. Installation des dépendances
        print("\n📦 3. Installation des dépendances...")
        _install_dependencies()
        
        # 4. Configuration des cookies
        print("\n🍪 4. Configuration des cookies...")
        _setup_cookies_management()
        
        # 5. Configuration Google Drive (optionnel)
        print("\n☁️ 5. Configuration Google Drive...")
        _setup_drive_integration()
        
        print("\n✅ Setup terminé! Utilisez transcribe_video(url)")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur durante la configuration: {e}")
        print("🔧 Essayez la configuration manuelle...")
        return _manual_setup()

def _check_gpu_availability():
    """Vérifie la disponibilité du GPU."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"✅ GPU détecté: {gpu_name} ({gpu_memory:.1f} GB)")
        else:
            print("⚠️  CPU seulement - Activez le GPU: Runtime > Change runtime type > GPU")
    except ImportError:
        print("⚠️  PyTorch non encore installé")

def _setup_project_from_github(force_reinstall: bool = False):
    """Clone ou met à jour le projet depuis GitHub."""
    try:
        if os.path.exists(PROJECT_DIR) and force_reinstall:
            print("🔄 Suppression de l'ancienne version...")
            subprocess.run(["rm", "-rf", PROJECT_DIR], check=True)
        
        if not os.path.exists(PROJECT_DIR):
            print(f"📥 Clonage depuis {GITHUB_REPO}...")
            result = subprocess.run([
                "git", "clone", GITHUB_REPO, PROJECT_DIR
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Erreur de clonage: {result.stderr}")
                return False
            print("✅ Projet cloné avec succès")
        else:
            print("📂 Projet existant détecté")
            os.chdir(PROJECT_DIR)
            print("🔄 Mise à jour depuis GitHub...")
            subprocess.run(["git", "pull", "origin", "main"], capture_output=True)
            print("✅ Projet mis à jour")
        
        os.chdir(PROJECT_DIR)
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du clonage: {e}")
        return False

def _install_dependencies():
    """Installe les dépendances du projet."""
    try:
        # Mise à jour des paquets système
        subprocess.run(["apt-get", "update", "-qq"], check=True)
        subprocess.run(["apt-get", "install", "-y", "ffmpeg"], check=True)
        
        # Installation des dépendances Python
        subprocess.run([
            "pip", "install", "-r", "requirements.txt", "--quiet"
        ], check=True)
        
        # Installation PyTorch avec CUDA (si nécessaire)
        try:
            import torch
            if not torch.cuda.is_available():
                print("🔧 Installation de PyTorch avec CUDA...")
                subprocess.run([
                    "pip", "install", "torch", "torchvision", "torchaudio", 
                    "--index-url", "https://download.pytorch.org/whl/cu121", "--quiet"
                ], check=True)
        except ImportError:
            print("🔧 Installation de PyTorch avec CUDA...")
            subprocess.run([
                "pip", "install", "torch", "torchvision", "torchaudio", 
                "--index-url", "https://download.pytorch.org/whl/cu121", "--quiet"
            ], check=True)
        
        print("✅ Dépendances installées")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        raise

def _setup_drive_integration():
    """Configure l'intégration avec Google Drive."""
    try:
        # Import dynamique pour éviter les erreurs hors Colab
        try:
            from google.colab import drive
        except ImportError:
            print("⚠️  Module google.colab non disponible")
            return
            
        if not os.path.exists("/content/drive"):
            print("🔗 Montage de Google Drive...")
            drive.mount('/content/drive')
            print("✅ Google Drive monté")
        else:
            print("✅ Google Drive déjà monté")
            
        # Création du dossier privé pour les cookies
        private_dir = Path("/content/drive/MyDrive/yt-whisper-private")
        private_dir.mkdir(exist_ok=True)
        print(f"📁 Dossier privé créé: {private_dir}")
        
    except Exception as e:
        print(f"⚠️  Erreur Drive: {e}")

def _setup_cookies_management():
    """Configure la gestion avancée des cookies."""
    cookies_path = _find_cookies_file()
    
    if cookies_path:
        print(f"✅ Cookies détectés: {cookies_path}")
        os.environ['YT_COOKIES_FILE'] = str(cookies_path)
        print("🔧 Variable YT_COOKIES_FILE configurée")
    else:
        print("ℹ️  Aucun cookie détecté - Fonctionnement sans cookies")
        _show_cookies_instructions()

def _find_cookies_file() -> Optional[Path]:
    """Recherche les cookies dans les emplacements prédéfinis."""
    for path_str in COOKIES_SEARCH_PATHS:
        path = Path(path_str)
        if path.exists() and path.is_file():
            return path
    return None

def _show_cookies_instructions():
    """Affiche les instructions pour configurer les cookies."""
    print("""
📋 POUR AJOUTER VOS COOKIES:

1. Méthode recommandée (Google Drive):
   - Exportez vos cookies depuis votre navigateur
   - Utilisez clean_cookies_interactive() pour les nettoyer
   - Sauvegardez dans /content/drive/MyDrive/yt-whisper-private/

2. Upload direct:
   - Uploadez cookies_youtube.txt via l'interface Colab
   - Le système les détectera automatiquement

⚠️  SÉCURITÉ: Utilisez uniquement des cookies YouTube nettoyés!
    """)

def _manual_setup():
    """Configuration manuelle de secours."""
    try:
        print("🔧 Configuration manuelle...")
        
        # Clone du projet
        if not os.path.exists(PROJECT_DIR):
            subprocess.run([
                'git', 'clone', GITHUB_REPO, PROJECT_DIR
            ], check=True)
        
        os.chdir(PROJECT_DIR)
        
        # Installation basique
        subprocess.run([
            'pip', 'install', '-r', 'requirements.txt', '--quiet'
        ], check=True)
        
        print("✅ Configuration manuelle terminée!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration manuelle échouée: {e}")
        return False

def clean_cookies_interactive():
    """Nettoie interactivement un fichier cookies."""
    print("🧹 NETTOYAGE INTERACTIF DES COOKIES")
    
    # Recherche du fichier cookies uploadé
    potential_files = [
        "/content/cookies.txt",
        "/content/cookies_complets.txt", 
        "/content/cookies_full.txt"
    ]
    
    input_file = None
    for file_path in potential_files:
        if os.path.exists(file_path):
            input_file = file_path
            break
    
    if not input_file:
        print("❌ Aucun fichier cookies détecté dans /content/")
        print("   Uploadez d'abord votre fichier cookies.txt via l'interface Colab")
        return False
    
    print(f"📁 Fichier détecté: {input_file}")
    
    # Nettoyage
    output_file = "/content/cookies_youtube_clean.txt"
    
    try:
        # Vérification que nous sommes dans le bon dossier
        if not os.path.exists("scripts/clean_cookies.py"):
            os.chdir(PROJECT_DIR)
        
        # Utilisation du script de nettoyage
        result = subprocess.run([
            "python", "scripts/clean_cookies.py", 
            input_file, output_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Cookies nettoyés avec succès!")
            print(result.stdout)
            
            # Configuration automatique
            os.environ['YT_COOKIES_FILE'] = output_file
            print(f"🔧 Variable YT_COOKIES_FILE configurée: {output_file}")
            
            # Option de copie vers Drive
            drive_path = "/content/drive/MyDrive/yt-whisper-private/cookies_youtube.txt"
            if os.path.exists("/content/drive"):
                try:
                    os.makedirs(os.path.dirname(drive_path), exist_ok=True)
                    subprocess.run(["cp", output_file, drive_path], check=True)
                    print(f"💾 Cookies sauvegardés dans Drive: {drive_path}")
                except Exception as e:
                    print(f"⚠️  Sauvegarde Drive échouée: {e}")
            
            return True
        else:
            print("❌ Erreur lors du nettoyage:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def transcribe_video(
    url: str, 
    model: str = "turbo", 
    output_format: str = "srt",
    use_swood_glossary: bool = True,
    language: str = "en",
    device: str = "auto",
    verbose: bool = True
) -> Optional[str]:
    """Fonction principale de transcription optimisée pour Colab."""
    
    print(f"\n🎬 TRANSCRIPTION: {url}")
    print(f"📊 Modèle: {model} | Format: {output_format} | Langue: {language}")
    
    # Vérification de l'environnement
    if not os.path.exists(PROJECT_DIR):
        print("❌ Projet non configuré. Exécutez setup_colab_environment() d'abord.")
        return None
    
    os.chdir(PROJECT_DIR)
    
    # Construction de la commande
    cmd = [
        "python", "scripts/transcribe.py", url,
        "--model", model,
        "--output_format", output_format,
        "--language", language,
        "--device", device,
        "--output_dir", "data"
    ]
    
    if verbose:
        cmd.append("--verbose")
    
    # Ajout du glossaire SWOOD
    if use_swood_glossary and os.path.exists("SWOOD_Glossary.json"):
        cmd.extend(["--replace-map", "SWOOD_Glossary.json"])
        print("🔧 Glossaire SWOOD activé")
    
    # Gestion des cookies
    cookies_path = _find_cookies_file()
    if cookies_path:
        cmd.extend(["--cookies-file", str(cookies_path)])
        print(f"🍪 Cookies configurés: {cookies_path.name}")
    else:
        print("⚠️  Pas de cookies - Certaines vidéos pourraient être inaccessibles")
    
    # Exécution
    print("\n" + "="*60)
    print("🚀 DÉBUT DE LA TRANSCRIPTION")
    print("="*60)
    
    try:
        result = subprocess.run(cmd, cwd=PROJECT_DIR)
        
        if result.returncode == 0:
            print("\n" + "="*60)
            print("✅ TRANSCRIPTION TERMINÉE AVEC SUCCÈS")
            print("="*60)
            
            # Recherche du fichier généré
            data_dir = Path(PROJECT_DIR) / "data"
            if data_dir.exists():
                pattern = f"*.{output_format}"
                files = list(data_dir.glob(pattern))
                if files:
                    latest_file = max(files, key=lambda p: p.stat().st_mtime)
                    print(f"📁 Fichier généré: {latest_file}")
                    
                    # Affichage d'un aperçu
                    _show_file_preview(latest_file)
                    
                    return str(latest_file)
            
            print("⚠️  Fichier généré non trouvé dans data/")
            return None
            
        else:
            print("\n❌ ÉCHEC DE LA TRANSCRIPTION")
            _show_troubleshooting_tips()
            return None
            
    except KeyboardInterrupt:
        print("\n⏹️  Transcription interrompue par l'utilisateur")
        return None
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return None

def _show_file_preview(file_path: Path):
    """Affiche un aperçu du fichier généré."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            preview_length = 500
            if len(content) > preview_length:
                preview = content[:preview_length] + "...\n[Contenu tronqué]"
            else:
                preview = content
            
            print("\n📄 APERÇU DU FICHIER:")
            print("-" * 40)
            print(preview)
            print("-" * 40)
            
    except Exception as e:
        print(f"⚠️  Impossible d'afficher l'aperçu: {e}")

def _show_troubleshooting_tips():
    """Affiche des conseils de dépannage."""
    print("""
🔧 CONSEILS DE DÉPANNAGE:

1. Vidéo privée/restreinte:
   → Configurez vos cookies YouTube avec clean_cookies_interactive()

2. Modèle trop lourd:
   → Essayez un modèle plus petit: transcribe_video(url, model="base")

3. Erreur de mémoire GPU:
   → Forcez l'usage du CPU: transcribe_video(url, device="cpu")

4. URL invalide:
   → Vérifiez que l'URL YouTube est correcte et accessible

5. Problème réseau:
   → Relancez la transcription, yt-dlp a des mécanismes de retry
    """)

# === FONCTIONS DE COMMODITÉ ===
def quick_setup():
    """Setup rapide en une commande."""
    return setup_colab_environment()

def demo_transcribe():
    """Démonstration interactive."""
    print("🎯 DÉMONSTRATION INTERACTIVE")
    
    # Vérification du setup
    if not os.path.exists(PROJECT_DIR):
        print("🔧 Configuration automatique...")
        if not setup_colab_environment():
            print("❌ Configuration échouée")
            return None
    
    print("\n📋 Exemples d'utilisation:")
    print("""
# 1. Transcription simple
transcribe_video("https://youtube.com/watch?v=VIDEO_ID")

# 2. Transcription SWOOD avec modèle précis
transcribe_video(
    "https://youtube.com/watch?v=VIDEO_ID",
    model="medium",
    use_swood_glossary=True
)

# 3. Transcription en français vers texte
transcribe_video(
    "https://youtube.com/watch?v=VIDEO_ID", 
    language="fr",
    output_format="txt"
)
    """)
    
    # Entrée interactive
    try:
        url = input("\n🎬 Entrez une URL YouTube (ou Enter pour ignorer): ").strip()
        if url and ("youtube.com" in url or "youtu.be" in url):
            print("\n🚀 Lancement de la transcription...")
            return transcribe_video(url)
        else:
            print("ℹ️  Aucune URL fournie - utilisez transcribe_video(url) manuellement")
    except KeyboardInterrupt:
        print("\n⏹️  Démonstration annulée")
    
    return None

def show_project_info():
    """Affiche les informations sur le projet."""
    print("""
📊 YT-WHISPER-SCRIBE - INFORMATIONS

🎯 Fonctionnalités:
  • Transcription locale avec Whisper
  • Support vocabulaire métier SWOOD
  • Corrections post-transcription intelligentes  
  • Gestion sécurisée des cookies YouTube
  • Export SRT et TXT

📁 Structure:
  • scripts/transcribe.py - CLI principal
  • SWOOD_Glossary.json - Corrections métier
  • data/ - Fichiers de sortie
  • examples/ - Exemples et configuration Colab

🚀 Commandes rapides:
  • setup_colab_environment() - Configuration initiale
  • transcribe_video(url) - Transcription simple
  • clean_cookies_interactive() - Nettoyage cookies
  • demo_transcribe() - Démonstration interactive
    """)

# === AUTO-EXÉCUTION POUR COLAB ===
if __name__ == "__main__":
    try:
        # Détection de l'environnement Colab
        import google.colab
        print("🔍 Environnement Google Colab détecté")
        
        # Setup automatique si pas encore fait
        if not os.path.exists(PROJECT_DIR):
            print("🚀 Premier lancement - Configuration automatique...")
            setup_colab_environment()
        
        # Affichage des informations
        show_project_info()
        
        print("\n✨ Prêt à l'emploi! Utilisez transcribe_video(url) pour commencer.")
        
    except ImportError:
        print("⚠️  Ce script est optimisé pour Google Colab")
        print("   Pour usage local, consultez la documentation principale")