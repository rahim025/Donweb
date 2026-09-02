# Donweb 🎓

Réseau social interne réservé aux enseignants et professeurs du **Lycée Don Bosco**, inspiré de Facebook.

## Fonctionnalités
- Inscription réservée aux emails du domaine du lycée (validation par un admin ensuite)
- Profils enseignants (photo, matière, bio)
- Fil d'actualité (posts, likes, commentaires)
- Réseau de collègues (demandes, acceptation)
- Messagerie privée
- Annuaire des enseignants

## Installation locale

```bash
python -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

L'application démarre sur http://127.0.0.1:5000

## Configuration

Variables d'environnement (optionnelles, voir `config.py`) :
- `SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_EMAIL_DOMAIN` (par défaut : `donbosco.edu`)

## Valider un compte enseignant

Pour l'instant, la validation des comptes (`is_approved`) se fait directement en base de données.
Une interface d'administration pourra être ajoutée par la suite.

## Déploiement sur GitHub

```bash
git init
git add .
git commit -m "Premier commit - squelette Donweb"
git branch -M main
git remote add origin https://github.com/<ton-utilisateur>/donweb.git
git push -u origin main
```

## Pistes d'amélioration
- Interface d'administration pour valider les comptes
- Groupes par matière / niveau
- Partage de documents pédagogiques
- Notifications en temps réel
