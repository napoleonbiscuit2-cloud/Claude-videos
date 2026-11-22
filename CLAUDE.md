# Claude-videos — règles de travail

## Communication
- Parler à l'utilisateur **en français simple** (il apprend le français).
- Travailler **étape par étape** : finir une étape, montrer le résultat, attendre son accord avant la suivante.

## Vidéos
- Format : vertical **1080x1920**, pour Shorts / TikTok / Reels.
- Langue des vidéos : **espagnol** (sauf demande contraire).
- Voix : ElevenLabs **« Bryan - Narrator »** (`hEKEQC93QpOYMa6WuwWp`), modèle `eleven_v4`, 1 seule prise.
- Sous-titres : transcription `eleven_scribe_v1` → horodatage mot par mot.
- Style validé : **planches anciennes du XIXe siècle** (gravures sépia sur carte abîmée, fond noir, référence : Muybridge / zoopraxiscope). Images : `gpt-image-2.5-sunburst`, `aspect_ratio: 9:16`.
- L'utilisateur trouve les animations trop **artificielles** : suivre les règles ci-dessous.
- Toujours tester **une seule image / un seul plan** avant de dépenser des crédits sur toutes les scènes.
- Exemple complet : `cerebro-es/` (narration, images, `render.py`).

## Règles d'animation naturelle (détails dans `guide-animation.md`)
1. **Ease in / ease out** partout ; jamais de mouvement linéaire ni d'arrêt brusque.
2. Mouvement de caméra **lent**, dirigé **vers le sujet** dont parle la voix (pas au hasard).
3. Effets de film **discrets** : dérive lente (1–2 px, bruit lisse, pas aléatoire image par image), flicker doux, grain léger, halation légère, rayures rares.
4. **Une seule sorte de transition**, sobre (coupe nette sur le rythme ou fondu au noir court). Pas de flash répété.
5. Pas de zooms « punch » répétés : au maximum un moment fort par vidéo.
6. Pas d'emojis en couleur sur le style ancien (ou les passer en sépia).
7. Donner de la **profondeur** : parallaxe 2.5D (DepthFlow / Depth Anything) avant de passer à l'IA image → vidéo.
8. Accroche : du mouvement et le point principal dès les **3 premières secondes**.

## Technique
- Sorties lourdes : réencoder (`-crf 23 -maxrate 4.5M`) pour rester sous ~50 Mo (limite conseillée par GitHub).
- Le réseau de l'environnement « Claude-videos » autorise `elevenlabsusercontent.com`, `www.youtube.com`, `i.ytimg.com`.
