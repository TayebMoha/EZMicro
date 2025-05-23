# Projet PSID
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/TayebMoha/ProjetCancer?label=tag)
[![Release](https://img.shields.io/github/release/TayebMoha/ProjetCancer.svg?style=flat-square)](https://github.com/TayebMoha/ProjetCancer/releases)

## À propos

Dans un monde où les maladies cancéreuses figurent parmi les principales causes de mortalité, les technologies émergentes jouent un rôle essentiel pour mieux comprendre, prévenir et traiter ces pathologies. Les données médicales, lorsqu'elles sont exploitées de manière optimale, offrent des opportunités uniques pour révéler des facteurs de risque, améliorer les traitements et optimiser les résultats cliniques. 

Ce projet s'inscrit dans cette dynamique, en mettant à profit les avancées en **Data Analytics** et **Machine Learning**. Il utilise un jeu de données médicales relatif à des patients atteints de cancer pour répondre à plusieurs défis clés : 

- **Identifier des patterns significatifs** dans les données pour mieux comprendre les caractéristiques des patients et des pathologies.
- **Analyser les facteurs influençant** la survie et la réponse aux traitements.
- **Automatiser l'analyse des données** afin d'améliorer la précision et l'efficacité des diagnostics.

## Architecture du Projet

Le projet repose sur une architecture modulaire basée sur **FastAPI**, un framework web moderne et performant pour Python. 

- **Backend** : Développé avec **FastAPI**, offrant des endpoints RESTful pour interagir avec les données et les modèles de machine learning.  
  ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)  ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)  

- **Frontend** :  
  - ***Dossier `templates`*** : Contient les fichiers HTML pour l'interface utilisateur (le cas échéant).  
  - ***Dossier `static`*** : Contient les fichiers JS et CSS.  
![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)    ![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)    ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)  

- **Hébergement et CI/CD** :  https://projetcancer.onrender.com

  ![Render](https://img.shields.io/badge/Render-0468D7?style=for-the-badge&logo=render&logoColor=white)


## Installation et Démarrage

Pour exécuter ce projet localement, suivez les étapes ci-dessous :

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/TayebMoha/ProjetCancer.git
   cd ProjetPSID
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Lancez le serveur FastAPI :
   ```bash
   python -m uvicorn main:app --reload
   ```

4. Accédez à la documentation interactive générée automatiquement par FastAPI :
   - [Swagger UI](http://127.0.0.1:8000/docs)
   - [Redoc](http://127.0.0.1:8000/redoc)

## Auteurs

- Anaëlle
- Ludjie
- Tayeb

## Licence

Ce projet est sous licence [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0), offrant liberté d'utilisation et de distribution.
