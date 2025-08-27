"""
⚡ YT-WHISPER-SCRIBE - QUICKSTART ULTRA-RAPIDE POUR COLAB
Une seule ligne pour tout configurer et commencer!
"""

def quickstart_colab():
    """Configuration ultra-rapide en une seule fonction."""
    
    print("⚡ QUICKSTART YT-WHISPER-SCRIBE")
    print("=" * 40)
    
    import subprocess
    import os
    
    # Téléchargement du configurateur principal
    if not os.path.exists('/content/colab_setup.py'):
        print("📥 Téléchargement des outils...")
        try:
            subprocess.run([
                'wget', '-q', 
                'https://raw.githubusercontent.com/Jojo4911/yt-whisper-scribe/main/examples/colab_setup.py',
                '-O', '/content/colab_setup.py'
            ], check=True)
        except Exception as e:
            print(f"❌ Erreur de téléchargement: {e}")
            print("🔧 Configuration manuelle...")
            return _manual_setup()
    
    # Import et configuration automatique
    try:
        exec(open('/content/colab_setup.py').read())
        print("\n✨ Configuration terminée! Utilisez transcribe_video(url)")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        return _manual_setup()

def _manual_setup():
    """Configuration manuelle de secours."""
    import subprocess
    import os
    
    print("🔧 Configuration manuelle...")
    
    # Clone du projet
    if not os.path.exists('/content/yt-whisper-scribe'):
        subprocess.run([
            'git', 'clone', 
            'https://github.com/Jojo4911/yt-whisper-scribe.git',
            '/content/yt-whisper-scribe'
        ], check=True)
    
    os.chdir('/content/yt-whisper-scribe')
    
    # Installation des dépendances
    subprocess.run(['pip', 'install', '-r', 'requirements.txt', '--quiet'], check=True)
    
    print("✅ Configuration manuelle terminée!")
    return True

def transcribe_simple(url: str):
    """Transcription ultra-simple."""
    import subprocess
    import os
    
    if not os.path.exists('/content/yt-whisper-scribe'):
        print("❌ Projet non configuré. Exécutez quickstart_colab() d'abord.")
        return None
    
    os.chdir('/content/yt-whisper-scribe')
    
    print(f"🎬 Transcription: {url}")
    
    cmd = [
        'python', 'scripts/transcribe.py', url,
        '--model', 'turbo',
        '--output_format', 'srt',
        '--device', 'auto',
        '--verbose'
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Transcription terminée!")
        
        # Recherche du fichier généré
        from pathlib import Path
        data_dir = Path("data")
        if data_dir.exists():
            files = list(data_dir.glob("*.srt"))
            if files:
                latest = max(files, key=lambda p: p.stat().st_mtime)
                print(f"📁 Fichier: {latest}")
                return str(latest)
    
    print("❌ Échec de la transcription")
    return None

# === UTILISATION DIRECTE ===
if __name__ == "__main__":
    # Configuration automatique
    quickstart_colab()
    
    # Exemple interactif
    try:
        url = input("\n🎬 URL YouTube (Enter pour ignorer): ").strip()
        if url and ("youtube.com" in url or "youtu.be" in url):
            transcribe_simple(url)
        else:
            print("💡 Utilisez transcribe_simple('URL') pour transcription rapide")
    except KeyboardInterrupt:
        print("\n👋 Configuration terminée!")
        
    print("\n📖 FONCTIONS DISPONIBLES:")
    print("  • transcribe_simple('URL') - Transcription rapide")
    print("  • quickstart_colab() - Reconfiguration si besoin")