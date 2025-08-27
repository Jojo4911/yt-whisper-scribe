# 🚀 YT-Whisper-Scribe sur Google Colab

Configuration ultra-simple pour utiliser YT-Whisper-Scribe directement sur Google Colab avec intégration GitHub.

## ⚡ Démarrage Ultra-Rapide

### Option 1: Notebook Colab (Recommandée)
1. Ouvrez le notebook: [`colab.ipynb`](./colab.ipynb)
2. Activez le GPU: `Runtime` → `Change runtime type` → `Hardware accelerator: GPU`
3. Exécutez la première cellule pour configuration automatique
4. Modifiez l'URL et lancez la transcription!

### Option 2: Script Python Direct
```python
# Une seule ligne pour tout configurer
!wget -q https://raw.githubusercontent.com/Jojo4911/yt-whisper-scribe/main/examples/colab_quickstart.py && python colab_quickstart.py
```

### Option 3: Configuration Avancée
```python
# Import du configurateur avancé
!wget -q https://raw.githubusercontent.com/Jojo4911/yt-whisper-scribe/main/examples/colab_setup.py -O colab_setup.py
exec(open('colab_setup.py').read())

# Transcription simple
transcribe_video("https://youtube.com/watch?v=VIDEO_ID")
```

## 🍪 Gestion des Cookies YouTube

### Pourquoi des cookies?
Les cookies permettent d'accéder aux vidéos privées, restreintes par âge, ou géo-bloquées.

### Méthode Sécurisée (Recommandée)
1. **Exportez vos cookies** depuis votre navigateur avec une extension comme "Get cookies.txt"
2. **Nettoyez-les automatiquement**:
   ```python
   # Uploadez votre cookies.txt via l'interface Colab
   clean_cookies_interactive()  # Nettoie automatiquement
   ```
3. **Sauvegardez dans Google Drive** pour persistance entre sessions

### Options de Configuration
```python
# Option 1: Upload direct (temporaire)
# Uploadez cookies_youtube.txt via l'interface Colab

# Option 2: Google Drive (persistant)
from google.colab import drive
drive.mount('/content/drive')
# Copiez cookies_youtube.txt dans: /content/drive/MyDrive/yt-whisper-private/

# Option 3: Variable d'environnement
import os
os.environ['YT_COOKIES_FILE'] = '/chemin/vers/cookies_youtube.txt'
```

## 📊 Exemples d'Utilisation

### Transcription Simple
```python
# Configuration automatique + transcription
exec(open('colab_setup.py').read())
transcribe_video("https://youtube.com/watch?v=dQw4w9WgXcQ")
```

### Transcription Avancée SWOOD
```python
# Transcription optimisée pour contenu technique SWOOD
fichier = transcribe_video(
    url="https://youtube.com/watch?v=VIDEO_ID",
    model="medium",              # Modèle précis
    use_swood_glossary=True,     # Corrections métier
    language="en",               # Langue source
    output_format="srt"          # Format sous-titres
)

# Affichage du résultat
with open(fichier, 'r') as f:
    print(f.read()[:500])  # Premiers 500 caractères
```

### Transcription Multilingue
```python
# Transcription française vers texte
transcribe_video(
    "https://youtube.com/watch?v=VIDEO_ID",
    language="fr",
    output_format="txt",
    use_swood_glossary=False  # Pas de glossaire pour français
)
```

## 🎛️ Paramètres Disponibles

| Paramètre | Options | Description |
|-----------|---------|-------------|
| `model` | `tiny`, `base`, `small`, `medium`, `large`, `turbo` | Précision vs vitesse |
| `language` | `en`, `fr`, `auto` | Langue source (auto = détection) |
| `output_format` | `srt`, `txt` | Format de sortie |
| `use_swood_glossary` | `True`, `False` | Corrections métier SWOOD |
| `device` | `auto`, `cuda`, `cpu` | Processeur utilisé |

## 🔧 Fonctions Utiles

```python
# Configuration initiale
setup_colab_environment()

# Reconfiguration complète
setup_colab_environment(force_reinstall=True)

# Transcription simple
transcribe_video("URL_YOUTUBE")

# Nettoyage cookies interactif
clean_cookies_interactive()

# Démonstration interactive
demo_transcribe()

# Informations projet
show_project_info()
```

## 🔍 Résolution de Problèmes

### GPU Non Détecté
```
⚠️  CPU seulement - Activez le GPU
```
**Solution**: `Runtime` → `Change runtime type` → `Hardware accelerator: GPU`

### Vidéo Inaccessible
```
❌ Erreur de téléchargement
```
**Solutions**:
1. Vérifiez que l'URL est correcte
2. Configurez vos cookies YouTube
3. Essayez une vidéo publique pour tester

### Mémoire Insuffisante
```
❌ CUDA out of memory
```
**Solutions**:
```python
# Utilisez un modèle plus petit
transcribe_video(url, model="base")

# Ou forcez l'usage du CPU
transcribe_video(url, device="cpu")
```

### Erreur de Clonage GitHub
```
❌ Erreur de clonage
```
**Solutions**:
1. Vérifiez votre connexion réseau
2. Utilisez la configuration manuelle:
   ```python
   !git clone https://github.com/Jojo4911/yt-whisper-scribe.git
   %cd yt-whisper-scribe
   !pip install -r requirements.txt
   ```

## 🔒 Sécurité

### ✅ Pratiques Sécurisées
- Utilisez uniquement des cookies YouTube nettoyés
- Stockage dans Google Drive privé
- Pas de cookies dans le code source
- Variables d'environnement pour chemins

### ⚠️ À Éviter
- Ne partagez jamais votre fichier cookies complet
- N'incluez pas de cookies dans des notebooks partagés
- Ne commitez pas de cookies dans Git

## 📁 Structure des Fichiers

```
examples/
├── colab.ipynb           # Notebook principal (recommandé)
├── colab_setup.py        # Configuration avancée
├── colab_quickstart.py   # Configuration ultra-rapide
├── vocab_example.txt     # Exemple de vocabulaire
└── README.md            # Cette documentation

# Fichiers générés dans Colab:
/content/
├── yt-whisper-scribe/   # Projet cloné depuis GitHub
│   ├── data/            # Transcriptions générées
│   │   ├── video1.srt
│   │   └── video2.txt
│   └── SWOOD_Glossary.json
├── drive/
│   └── MyDrive/
│       └── yt-whisper-private/
│           └── cookies_youtube.txt  # Cookies sécurisés
└── colab_setup.py       # Configuration téléchargée
```

## 🚀 Avantages de Cette Configuration

1. **🔄 Toujours à jour**: Clone automatique depuis GitHub
2. **🍪 Sécurité renforcée**: Gestion avancée des cookies
3. **⚡ Ultra-simple**: Une cellule pour tout configurer
4. **💾 Persistance**: Sauvegarde Google Drive
5. **🔧 Robuste**: Gestion d'erreurs et fallbacks
6. **📊 Complet**: Toutes les fonctionnalités du projet

## 💡 Conseils d'Utilisation

- **Première fois**: Utilisez le notebook `colab.ipynb`
- **Usage régulier**: Bookmarkez votre setup dans Google Drive
- **Cookies**: Nettoyez toujours vos cookies avant utilisation
- **Modèles**: Commencez par `turbo`, passez à `medium` si besoin
- **Erreurs**: Consultez les conseils de dépannage intégrés

---

## 📞 Support

Pour toute question:
1. Consultez les messages d'erreur détaillés
2. Utilisez `show_project_info()` pour les informations système
3. Vérifiez la [documentation principale](../README.md)
4. Ouvrez une issue sur GitHub si nécessaire

---

## 📝 Exemples Locaux

### Vocabulaire Personnalisé
- Créez un fichier vocabulaire (un terme par ligne), ex: `vocab_example.txt`
- Utilisez-le avec `--vocab_file examples/vocab_example.txt`

### Fichiers Locaux
- Les fichiers média et sorties doivent être placés dans `data/` (ignoré par Git)
- Le projet détecte automatiquement `data/cookies.txt`
- Alternativement, utilisez `--cookies-file <chemin>`
