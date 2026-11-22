# Guide d'animation pour les vidéos courtes

Ce que j'ai appris en recherchant (novembre 2026), organisé selon tes 4 demandes.
Les règles pratiques à appliquer sont résumées dans `CLAUDE.md`, que chaque nouvelle session lit automatiquement.

---

## 1. Les animations qui deviennent virales

### Ce qui compte d'abord : les 3 premières secondes
Les spécialistes ne sont pas d'accord sur le chiffre exact (entre ~1,3 et 3 secondes), mais tous disent que la décision du spectateur se joue au tout début. Ces chiffres viennent de blogs, pas d'études officielles.
- **Une accroche qui ouvre une question** : un écart de curiosité, une affirmation surprenante, un chiffre (« Tu cerebro pesa solo el 2%… »).
- **Aller droit au but** : si la première phrase met plus de 3 secondes à arriver au point, on la réécrit.
- **Montrer avant d'expliquer** : l'image la plus forte d'abord, l'explication ensuite.
- **Du mouvement dès la première image** : jamais un écran fixe au départ.
- Pour le contenu éducatif, une ouverture **directe** marche souvent mieux qu'un mystère.

### Pourquoi une vidéo se partage
- **Courte** : les vidéos courtes deviennent plus souvent virales.
- **Émotion ou humour** : les vidéos drôles ou très émouvantes ont plus de chances.
- **Nouveauté** : montrer quelque chose qu'on n'a jamais vu.
- **Ironie** : une étude marketing la trouve dans 90 % des vidéos virales étudiées.
- **Diffusion** : la manière dont la vidéo circule (partages, comptes relais) compte autant que le contenu.

### Exemples à retenir
- **Kurzgesagt** (chaîne de vulgarisation animée) : design plat, couleurs vives, personnages ronds, mouvement « rebondissant » ; **la voix off donne le rythme de toute l'animation** ; musique et sons faits sur mesure.
- **Dollar Shave Club** : explication animée simple, humour, message clair.
- **Spider-Verse** : un style visuel jamais vu (voir partie 4) a fait parler de lui partout.

---

## 2. Une animation naturelle

### Les 12 principes de Disney, appliqués à nos vidéos
Écrits en 1981 par Johnston et Thomas, adaptés aujourd'hui au motion design. Les plus utiles pour nous :

| Principe | Ce que ça veut dire | Pour nos vidéos |
|---|---|---|
| **Ease in / ease out** (ralentir au début et à la fin) | Rien ne démarre ni ne s'arrête d'un coup | Tous les zooms, panoramiques et apparitions de texte |
| **Anticipation** | Un petit mouvement inverse avant l'action | Un texte recule un peu avant de surgir |
| **Follow-through / overshoot** (dépassement) | L'objet dépasse sa cible puis revient | Un titre arrive, dépasse de 3 %, revient |
| **Action secondaire** | Un petit mouvement qui accompagne le principal | Une poussière qui flotte, une ombre qui suit — **sans voler l'attention** |
| **Timing** | Le nombre d'images donne le poids et l'émotion | Lent = sérieux / mystère ; rapide = énergie |
| **Arcs** | Les choses bougent en courbes, pas en lignes droites | Panoramiques légèrement courbes |
| **Exagération** | Pousser un peu pour que ça se lise | Avec mesure : un « punch » par vidéo, pas dix |

### Ressorts (spring physics) plutôt que courbes fixes
- Un **ressort** n'a pas de durée fixe : il s'arrête quand il a fini de bouger, comme un vrai objet.
- **Raideur (stiffness)** = vitesse ; **amortissement (damping)** = combien ça rebondit.
- Amortissement critique = pas de rebond, précis (texte sérieux) ; raideur forte + amortissement faible = rebond visible (énergique).
- Exemple de réglage : raideur 180, amortissement 12 → environ 650 ms.

### Le « vieux film » sans faire faux
- **Chaque défaut doit rester discret** : c'est une finition, pas le sujet.
- **Gate weave** (dérive de l'image) : lente et très faible ; sur une image fixe on ne la voit pas, il faut la juger en lecture.
- **Flicker** : doux, variations lentes.
- **Grain** : léger (un grain fort cache les détails).
- **Halation** : léger halo chaud autour des zones claires sur fond sombre → très « pellicule ».
- **Repère** : partir d'un 35 mm discret ; 16 mm = plus de grain et de dérive ; 8 mm = beaucoup de poussière, de dérive et de flicker.

### Donner de la profondeur à une image fixe (parallaxe 2.5D)
1. Estimer la **profondeur** avec un modèle (Depth Anything, MiDaS).
2. Découper l'image en **plans** (premier plan / fond) et **reboucher** les trous derrière le sujet (inpainting).
3. Bouger la caméra : le premier plan glisse plus vite que le fond.
- Outils Python : **DepthFlow** (shader de parallaxe prêt à l'emploi), **Parallax Maker** (découpe en plans + inpainting).
- Version simple : le sujet reste fixe et le fond dérive derrière.

### Mouvement de caméra documentaire (effet Ken Burns)
- Ease out sur le premier repère, ease in sur le dernier.
- **Choisir le cadrage selon le contenu** : un mouvement purement aléatoire ne donne pas toujours un bon résultat.
- Plus lent = plus contemplatif et plus réel.

---

## 3. Les meilleurs outils et plugins pour améliorer mon travail

### Plugins Claude disponibles dans ton catalogue (pas encore installés)
| Plugin | À quoi ça sert pour nous |
|---|---|
| **Remotion** (par l'équipe Remotion) | Bonnes pratiques Remotion : animations, audio, **sous-titres**, 3D, rendu. Le plus utile. |
| **animation-studio** | Films animés « dessinés en code » avec musique synchronisée, export 9:16 pour TikTok / Shorts |
| **video-shotcraft** | « Recettes » de plans cinématiques avec Remotion, effets sonores |
| **watch-video** | Me permet de **regarder** une vidéo de référence (images clés + transcription) au lieu de deviner le style |

Tu peux les ajouter depuis claude.ai (catalogue de plugins). **Remotion** et **watch-video** sont ceux que je recommande en premier.

### Outils en code (ce que je peux utiliser ici)
| Outil | Langage | Points forts |
|---|---|---|
| **Remotion** | React | Vidéos à partir de modèles, automatisation, rendu reproductible, sous-titres |
| **Motion Canvas** | TypeScript | Animation scriptée à la main, explications animées, éditeur visuel |
| **Revideo** | TypeScript | Version de Motion Canvas pensée pour l'automatisation |
| **Manim** | Python | La référence pour la science et les maths (style 3Blue1Brown) |
| **DepthFlow / Parallax Maker** | Python | Parallaxe 2.5D sur nos planches |
| **ffmpeg** | — | Encodage, filtres, assemblage final |

### Animation par IA (crédits ElevenLabs)
- Modèles image → vidéo disponibles : **Kling, Seedance, Veo, Wan, LTX, Runway**…
- **Le prompt décrit seulement le mouvement** : l'image donne déjà le style, la lumière et le sujet. « Protéger d'abord, animer ensuite ».
- Formule Kling : **Sujet + Mouvement**, mots simples. Ex. : *« The paper card slowly drifts forward, ink lines gently shimmer, no morphing »*.
- Une instruction **courte et précise** par plan, sinon le modèle improvise.
- Toujours **tester sur une seule image** avant de lancer toutes les scènes.

### Plugins After Effects (pour un humain qui monte à la main)
**Animation Composer** (gratuit / payant, idéal pour débuter), **Saber** (gratuit, lueurs), **Element 3D**, **Trapcode Particular**, **Plexus**, **Sapphire**, **Duik** (rigging de personnages), **Motion Bro**, **Newton 3** (physique), **FX Console**.

---

## 4. Les styles d'animation

| Style | Comment c'est fait | Signature visuelle | Comment je peux l'imiter |
|---|---|---|---|
| **2D traditionnel (cel)** | Dessiné à la main image par image | Traits vivants, légère vibration du trait (Ghibli) | Images IA « hand-drawn », animation **sur 2** (12 i/s), trait qui vibre (*line boil*) |
| **2D numérique** | Dessin ou vecteurs sur ordinateur, souvent par pantins articulés | Lisse, propre, couleurs plates | Remotion / Motion Canvas, formes vectorielles, ressorts |
| **3D (CGI)** | Modèles 3D, squelettes, rendu | Volume, lumière réaliste | Blender en code (lent) ou IA image → vidéo |
| **Stop motion** | Objets réels photographiés image par image (pâte à modeler = *claymation*) | Saccadé, imparfait, artisanal | **12 i/s** (6–8 pour plus stylisé), **pas de flou de mouvement**, petits tremblements de bord, léger flicker |
| **Motion graphics** | Texte, formes et graphiques animés, pas de personnages | Infographies, typographie animée | Le plus facile en code : Remotion / Motion Canvas / Manim |
| **Anime** | Animation japonaise, *limited animation* | ~8 dessins/seconde, animation **sur 3**, poses tenues, *smears*, *impact frames* | Poses tenues + mouvements de caméra sur l'image fixe, flash d'impact sur les mots clés |
| **Rotoscopie** | On décalque une vidéo réelle | Mouvement très réaliste dans un style dessiné | Détourage IA (Roto Brush, Resolve, Beeble) puis stylisation |
| **Hybride** | Mélange de styles (souvent 2D + 3D) | Spider-Verse | Planches 2D + parallaxe 3D, ou IA + motion graphics |

### Termes clés à connaître
- **Sur 1 / sur 2 / sur 3** : un nouveau dessin à chaque image, toutes les 2 images ou toutes les 3. Spider-Verse était surtout **sur 2** (~12 i/s), ce qui donne son rythme « saccadé voulu ». Le 2ᵉ film a même mélangé les cadences sur un seul personnage (Hobie).
- **On peut raconter avec la cadence** : Miles (débutant) bouge sur 2, Peter (expérimenté) bouge sur 1.
- **Smear** : dessin étiré pour montrer un mouvement très rapide.
- **Impact frame** : image très contrastée qui clignote une fraction de seconde au moment d'un choc.
- **Limited animation** : réutiliser des dessins et tenir des poses. C'est un **choix de style**, pas seulement une économie.

### Quel style pour nos vidéos de science ?
1. **Planches anciennes + parallaxe + film discret** (notre style actuel, en mieux) → élégant, unique.
2. **Motion graphics façon Kurzgesagt** → très lisible, très partageable, facile en code.
3. **Hybride** : planche ancienne en fond + schéma animé (flèches, cercles qui se dessinent) par-dessus → le meilleur des deux.

---

## Sources
**Viralité**
- [Hook Engineering : les 3 premières secondes (DEV)](https://dev.to/bulkdl/hook-engineering-the-science-of-the-first-3-seconds-in-short-form-video-2026-2jp9)
- [Formules d'accroche YouTube Shorts (Opus)](https://www.opus.pro/blog/youtube-shorts-hook-formulas)
- [8 choses que font les TikTok virales (Opus)](https://www.opus.pro/blog/viral-tiktoks-first-3-seconds-2026)
- [Accroches pour vidéos courtes (CapCut)](https://www.capcut.com/create/short-form-video-hooks-first-3-second-patterns)
- [Vidéo virale (Wikipedia)](https://en.wikipedia.org/wiki/Viral_video)
- [Vidéos virales marketing (Wyzowl)](https://www.wyzowl.com/viral-videos/)
- [Art et science des vidéos virales (HubSpot)](https://blog.hubspot.com/marketing/art-science-viral-videos)
- [Processus vidéo Kurzgesagt](https://kurzgesagt.org/youtube/)
- [Simple, Bright, Beautiful : Kurzgesagt (U. Michigan)](https://artsatmichigan.umich.edu/ink/2019/09/27/simple-bright-beautiful-the-work-of-kurzgesagt)

**Animation naturelle**
- [Principes de l'animation (Adobe)](https://www.adobe.com/creativecloud/animation/discover/principles-of-animation.html?mv2=cch)
- [Easing, anticipation, follow-through (PremiumBeat)](https://www.premiumbeat.com/blog/animation-easing-anticipation-follow-through/)
- [Principes de l'animation en motion design (Freepik)](https://www.freepik.com/blog/animation-principles-in-motion-design)
- [12 principes de Disney appliqués à l'UI (IxDF)](https://ixdf.org/literature/article/ui-animation-how-to-apply-disney-s-12-principles-of-animation-to-ui-design)
- [Introduction à la physique des ressorts (Josh Comeau)](https://joshwcomeau.com/animation/a-friendly-introduction-to-spring-physics/)
- [Spring animation (Framer)](https://www.framer.com/dictionary/spring-animation)
- [Ressort converti en courbe CSS (CodePen)](https://codepen.io/carmenansio/pen/ZYOJGKo)
- [Effet Ken Burns (Adobe)](https://www.adobe.com/learn/premiere-pro/web/ken-burns-effect)
- [Halation, grain, gate weave (StraySpark)](https://www.strayspark.studio/blog/blender-film-look-halation-grain-gate-weave)
- [Niveaux 35 / 16 / 8 mm (Filmbox)](https://videovillage.com/learn/filmbox-looks/full-guide/about-the-looks)
- [DepthFlow](https://pypi.org/project/depthflow)
- [Parallax Maker](https://socket.dev/pypi/package/parallax-maker)

**Outils**
- [Remotion vs Motion Canvas vs Manim](https://beginnersinai.org/remotion-vs-motion-canvas-vs-manim/)
- [Remotion vs Motion Canvas vs Revideo](https://www.pkgpulse.com/guides/remotion-vs-motion-canvas-vs-revideo-programmatic-video-2026)
- [Remotion : comparaison avec Motion Canvas](https://www.remotion.dev/docs/compare/motion-canvas)
- [Meilleurs plugins After Effects 2026 (School of Motion)](https://www.schoolofmotion.com/blog/best-after-effects-plugins-and-effect-packs-you-need-in-2026)
- [Meilleurs plugins After Effects 2026 (Maxon)](https://www.maxon.net/en/article/best-after-effects-plugins-2026)
- [21+ plugins After Effects (FreeVisuals)](https://www.freevisuals.net/post/best-after-effects-plugins)
- [Prompts image → vidéo : décrire le mouvement (EachLabs)](https://www.eachlabs.ai/blog/image-to-video-prompts-write-the-motion)
- [Guide Kling image → vidéo](https://kling.ai/blog/how-to-animate-a-picture)
- [Prompts d'animation Seedance 2.5 (Magnific)](https://www.magnific.com/blog/seedance-2-5-animation-prompts/)
- [Conseils photo → vidéo (Runway)](https://runwayml.com/resources/photo-to-video-tips)

**Styles**
- [Types de styles d'animation (StudioBinder)](https://www.studiobinder.com/blog/types-of-animation-styles/)
- [Styles d'animation (Champlain College)](https://www.champlain.edu/blog/stories/animation-art-styles/)
- [Top 6 des styles d'animation (UAL)](https://www.arts.ac.uk/study-at-ual/short-courses/stories/top-6-styles-of-animation)
- [11 types d'animation (Wyzowl)](https://www.wyzowl.com/types-of-animation)
- [Comment Spider-Verse a obtenu son look (Creative Bloq)](https://creativebloq.com/features/how-into-the-spider-verse-got-its-mind-blowing-look)
- [Hobie : plusieurs cadences sur un personnage (Befores & Afters)](https://beforesandafters.com/2023/06/17/the-across-the-spider-verse-spider-punk-character-hobie-was-animated-with-different-frame-rates-for-different-parts-of-his-own-body-and-accessories/)
- [Spider-Verse : techniques d'animation](https://marilajane.substack.com/p/into-the-spider-verse-animation-techniques)
- [Animer sur 1, 2 et 3](https://publish.obsidian.md/mister-chad/animation/animating+on+the+ones%2C+two%2C+and+threes)
- [Limited animation (Wikipedia)](https://en.wikipedia.org/wiki/Limited_animation)
- [Smear frame (Wikipedia)](https://www.Wikipedia.org/wiki/Smear_frame)
- [Smears (canmom)](https://canmom.github.io/animation/smears)
- [Look stop motion en numérique](https://paper-animation.pages.dev/blog/creating-stop-motion-look)
- [Stop motion : frame rate](https://www.hitpaw.com/ai-video-enhancer-tips/stop-motion-animation-fps.html)
- [Outils de rotoscopie IA (Boris FX)](https://borisfx.com/blog/top-6-ai-rotoscoping-tools-free-and-paid/)
- [Rotoscopie IA (Neural Frames)](https://neuralframes.com/post/ai-rotoscoping)
