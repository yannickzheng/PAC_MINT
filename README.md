
# PacMint

Jeu multijoueur


## Déploiement

Pour lancer le projet (Linux):

### Configurer X11:

Autoriser Docker à accéder au serveur X11 :

```bash
xhost +local:docker
```
Vérifier les périphériques graphiques :
Assurez-vous que /dev/dri existe :

```bash
ls /dev/dri
```


Si /dev/dri/card1 n'existe pas, vérifiez votre pilote graphique :

```bash
glxinfo | grep "OpenGL renderer"
```

Installez les pilotes appropriés (par exemple, mesa-vulkan-drivers pour Intel/AMD).


### Construire et lancer le jeu 

```bash
docker-compose down
docker-compose build
docker-compose up -d
```