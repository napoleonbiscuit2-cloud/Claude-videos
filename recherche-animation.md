# Recherche : rendre les vidéos plus naturelles

Objectif : garder le style « planches anciennes / Muybridge », mais avec un mouvement qui fait vrai, pas « effet logiciel ».

## 1. Pourquoi la vidéo actuelle (`cerebro-es/cerebro_es.mp4`) paraît artificielle

| Problème | Ce que fait le script aujourd'hui | Pourquoi ça sonne faux |
|---|---|---|
| Tremblement | Saut aléatoire de ±4–6 px toutes les 2 images | Un vrai projecteur dérive **lentement** (gate weave), il ne saute pas au hasard |
| Scintillement | Luminosité aléatoire ±7 % à **chaque** image | Trop fort et trop rapide : ça « clignote » au lieu de « respirer » |
| Rayures | Une rayure sur 35 % des images | Beaucoup trop : sur un film réel elles sont rares |
| Transitions | Flash blanc + glissement à **chaque** changement | Effet répété 8 fois → on voit le truc |
| Zooms « punch » | Petit zoom brusque sur les mots clés | Mouvement de caméra impossible pour une photo d'archive |
| Image plate | Toute l'image bouge d'un bloc | Aucune profondeur : on voit que c'est une image fixe |
| Emojis colorés | 🚕 🤔 🍔 en couleur sur du sépia | Casse l'époque |

## 2. Techniques trouvées (de la plus simple à la plus puissante)

### A. Mouvement de caméra « documentaire » (gratuit, dans le script)
- **Easing** : démarrer et finir le mouvement en douceur (ease-in / ease-out), comme le recommande Adobe pour l'effet Ken Burns.
- **Plus lent** : un mouvement à peine visible paraît plus réel qu'un zoom marqué.
- **Hasard contrôlé** : choisir le cadrage selon le contenu (zoomer *vers* la partie du cerveau dont on parle), pas au hasard.
- **Dérive douce** : remplacer le tremblement aléatoire par un bruit lisse (type Perlin, basse fréquence), amplitude 1–2 px.

### B. Effets de film subtils (gratuit, dans le script)
Les guides sont unanimes : *chaque défaut doit rester discret, c'est une couche de finition*.
- **Gate weave** : petite dérive lente image par image (presque nulle par défaut).
- **Flicker** : doux, faible opacité, variations lentes.
- **Grain** : léger (le grain fort cache les détails de la gravure).
- **Halation** : léger halo chaud autour des zones claires → très « film ».
- **Repère** : partir d'un niveau « 35 mm discret », pas « 8 mm abîmé ».

### C. Parallaxe 2.5D (gratuit, outils Python)
On estime la **profondeur** de l'image (modèle *Depth Anything* / *MiDaS*), puis la caméra bouge et le premier plan glisse plus vite que le fond → effet 3D, la gravure « vit ».
- **DepthFlow** (Python, `pip install depthflow`) : shader de parallaxe prêt à l'emploi.
- **Parallax Maker** : découpe l'image en plans + bouche les trous (inpainting).
- Alternative simple : séparer le sujet du fond (détourage) et faire dériver le fond derrière le sujet immobile.

### D. Image → vidéo par IA (payant, crédits ElevenLabs)
Les modèles disponibles dans ton compte ElevenLabs (Kling, Seedance, Veo…) peuvent animer chaque planche quelques secondes.
- Le prompt doit décrire **seulement le mouvement** (l'image donne déjà le style) : *« slow gentle camera push-in, paper slightly flutters, no morphing »*.
- Une instruction **courte et précise** par plan, sinon le modèle improvise (déformations).
- Idée Muybridge : faire « respirer » le dessin, tourner une page, faire apparaître l'encre du cercle.

## 3. Plan proposé pour la prochaine vidéo

1. **Corriger les effets (A + B)** dans `render.py` : dérive lente, flicker doux, grain léger, halation, rayures rares, une seule sorte de transition (coupe nette ou fondu au noir court), plus de zooms « punch ».
2. **Supprimer ou désaturer les emojis** (les passer en sépia) pour rester dans l'époque.
3. **Tester la parallaxe (C)** sur 1 image → on compare avec la version actuelle.
4. Si ce n'est pas encore assez vivant : **tester l'IA image→vidéo (D)** sur 1 seule planche avant de dépenser des crédits sur toutes.

## Sources
- [Ken Burns effect — Adobe Premiere Pro (easing)](https://www.adobe.com/learn/premiere-pro/web/ken-burns-effect)
- [Ken Burns effect — Wikipedia](https://en.wikipedia.org/wiki/Ken_Burns_effect)
- [Brevet : génération d'effets Ken Burns selon le contenu](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10721388)
- [Film look : halation, grain, gate weave (Blender)](https://www.strayspark.studio/blog/blender-film-look-halation-grain-gate-weave)
- [Filmbox — niveaux 35 mm / 16 mm / 8 mm](https://videovillage.com/learn/filmbox-looks/full-guide/about-the-looks)
- [Vintage lighting & grain (couches de finition)](https://www.positioniseverything.net/how-to-match-vintage-commercial-lighting-and-film-grain-in-ai-video/)
- [Effet vintage années 20 (flicker doux)](https://filmora.wondershare.com/video-effects/vintage-film-effect-1920s.html)
- [Halation — Darkroom](https://darkroom.co/help/guide/vintage-film.md)
- [Look 35 mm — Flick](https://flick.art/blog/guides/35mm-film-look)
- [DepthFlow (parallaxe)](https://pypi.org/project/depthflow)
- [Parallax Maker](https://socket.dev/pypi/package/parallax-maker)
- [Image fixe → mouvement réel (ffmpeg + Python)](https://dev.to/dasein108/zero-to-autopilot-part-3-giving-a-still-image-real-motion-for-000-1a5b)
- [Prompts image→vidéo : décrire le mouvement](https://www.eachlabs.ai/blog/image-to-video-prompts-write-the-motion)
- [Guide Kling image→vidéo](https://kling.ai/blog/how-to-animate-a-picture)
- [Prompts d'animation Seedance 2.5](https://www.magnific.com/blog/seedance-2-5-animation-prompts/)
