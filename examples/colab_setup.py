"""
Configuration sécurisée pour Google Colab
Utilise Google Drive pour stocker les cookies de manière privée
"""

# === SETUP COLAB ===
def setup_colab_environment():
    """Configure l'environnement Colab avec gestion sécurisée des cookies."""
    
    print("🔧 Configuration de l'environnement Colab...")
    
    # Monte Google Drive
    from google.colab import drive
    drive.mount('/content/drive')
    
    # Clone le projet
    import os
    if not os.path.exists('/content/yt-whisper-scribe'):
        !git clone https://github.com/Jojo4911/yt-whisper-scribe.git
        os.chdir('/content/yt-whisper-scribe')
    
    # Install dependencies
    !pip install -r requirements.txt
    !pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    
    print("✅ Environnement configuré!")

def setup_secure_cookies():
    """Guide pour configurer les cookies de manière sécurisée."""
    
    print("""
🔐 CONFIGURATION SÉCURISÉE DES COOKIES

Option 1 - Stockage Drive privé:
1. Crée un dossier privé dans ton Google Drive: /My Drive/yt-whisper-private/
2. Upload ton fichier cookies.txt nettoyé dans ce dossier
3. Utilise le code ci-dessous:

    import os
    os.environ['YT_COOKIES_FILE'] = '/content/drive/My Drive/yt-whisper-private/cookies.txt'

Option 2 - Upload temporaire:
1. Upload ton fichier via l'interface Colab (icône dossier à gauche)
2. Utilise:
    
    import os
    os.environ['YT_COOKIES_FILE'] = '/content/cookies.txt'

⚠️  SÉCURITÉ:
- Utilise SEULEMENT des cookies YouTube nettoyés
- N'upload jamais ton fichier cookies.txt complet
- Utilise le script clean_cookies.py avant upload
    """)

# === UTILISATION ===
def transcribe_with_secure_cookies(url, model="turbo"):
    """Transcrit une vidéo avec gestion sécurisée des cookies."""
    
    import os
    import subprocess
    
    # Vérifie si les cookies sont configurés
    cookies_path = os.getenv('YT_COOKIES_FILE')
    if cookies_path and os.path.exists(cookies_path):
        print(f"🍪 Utilisation des cookies: {cookies_path}")
        cmd = f"python scripts/transcribe.py '{url}' --model {model} --cookies-file '{cookies_path}'"
    else:
        print("⚠️  Pas de cookies configurés, tentative sans cookies")
        cmd = f"python scripts/transcribe.py '{url}' --model {model}"
    
    # Execute transcription
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Transcription réussie!")
        print(result.stdout)
    else:
        print("❌ Erreur de transcription:")
        print(result.stderr)
    
    return result.returncode == 0

# === EXEMPLE D'USAGE ===
if __name__ == "__main__":
    # Setup
    setup_colab_environment()
    setup_secure_cookies()
    
    # Exemple de transcription
    url = input("Entre l'URL YouTube: ")
    transcribe_with_secure_cookies(url)