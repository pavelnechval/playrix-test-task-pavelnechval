# Card generation prompt v7

Template used by `cardgen.py` and, with the same card text, by the ChatGPT route (`codex_images.py`).

**What changed from v6 (W019):** this is Pavel's final pass. It applies to both models.

- **Size and breathing room** are now targets measured on the 160 reference cards (`card_metrics.py`):
  - the object's largest dimension is about 80–88% of the card;
  - at least 5% clear on every side;
  - about 12–16% of the card height clear above the object;
  - a safe area for the crop to the card shape.
  - Before this, ChatGPT drew objects bigger, with 0–2% margins and little room above. The old "60–75% of the height" left Gemini's C1 objects small and its C2 objects low under an empty wall.
- **Simplicity at card size:** a few big shapes, and no details too small to read on the card. Scene backdrops are simple masses.
- **Highlights:** moderate and consistent across a set.

**What changed from v5 to v6 (W018):** plans now carry a set bible (`set_guidelines.md`). A plan may set 1–2 cards at sunset or at night as a mood accent. Such a card must stay bright and saturated, so the lighting and colour rules below say how.

**v5 was prompt v4 plus the lessons from rating the 120 Cinema cards (W016):**

- **Scene cards (category 4) stand on wide, visible ground.** The backdrop is the object's natural setting; open sky is one option, not the default. Sources: Pavel's comments and a review of all 160 reference cards.
- **Materials read at a glance:** metal, glass, fabric, water and stone. Steam is natural and soft. Source: Pavel's comments.
- **Bold, sparse decoration and chunky silhouettes.** Thin objects are drawn thicker. Sources: Pavel and the external model.
- **Light sources never spill a glow onto the background.** Source: Pavel.

Every rule's source is listed in `pipeline/rulebook.md`. The steam line names reference R4 (the tea cup in `refs_production.json`).

Placeholders: {n_refs}, {ref_id}, {category_short}, {name}, {subject}, {unique_detail}, {main_colors}, {background}, {context_cue}, {category}, {category_rules}, {fix}.

## INTRO
You will create one illustration for a collectible card in a casual mobile game. The next {n_refs} images are existing cards from this game. Use them only to learn the art style; never copy their objects.

## REFERENCE_LABEL
Reference {ref_id} ({category_short}):

## TASK
Task: draw a NEW card illustration that looks as if the same artist made it for the same card album, so that a player would not notice any difference next to the reference cards.

Card brief:
- Card: {name}.
- Object: {subject}.
- Its one charming, distinctive detail: {unique_detail}.
- Main colours of the object: {main_colors}.
- Background: {background}.
- Context cue: {context_cue}.

Rendering, matched exactly to the references:
- A clean, polished 3D game-asset finish: smooth, chunky, simplified volumes with soft rounded edges and slightly exaggerated proportions, with crisp, clearly defined materials.
- Materials read at a glance. Metal has bright, sharp reflections and looks like real metal, never like matte plastic. Glass is clear, with crisp highlights. Fabric is thin, with soft natural folds and fine edges, never puffy or moulded. Water is clear and translucent, with white foam and highlights, never solid ribbons. Stone and rock are smooth, chunky planes without noisy texture.
- Highlights are moderate and even, like on the reference cards: one or two broad, soft highlights per main form, never glare, sparkle or mirror reflections. Every card of a set shares the same finish.
- Bright, even, cheerful lighting from the upper front, with soft-edged highlight shapes and a satin sheen. Never wet-look, chrome or mirror-like gloss, and never dim, moody, theatrical or photographic lighting. The whole image is bright.
- If the brief sets the scene at sunset or at night, keep it bright and saturated: a glowing, warm orange-pink sunset sky, or a clear, deep-blue night lit by warm lights. The object itself stays brightly lit. Never murky, grey or dark.
- No outlines or dark contour lines, no painterly brush strokes, no flat cel shading, no photographic depth of field, no realistic micro-textures.

Object:
- The most typical, instantly recognizable version of the object, complete with its standard parts and seen from its most familiar angle.
- A chunky, solid, clear silhouette. Thin or open objects (hoops, tools, keys, rings) are drawn thicker and turned to show their broadest side, so they still fill the frame.
- Manufactured objects have smooth, clean surfaces and simple flowing lines: no grooves, ridges, panel lines, droplets, grip textures or busy decoration. Instead of generic stripes or bands, give the object the one charming detail from the brief.
- Decoration stays bold and sparse: a few large decorative shapes, never clusters of many small ones (many little flowers, gems or locks, lattice, lace or filigree).
- Built structures keep their crafted structural details (bricks or planks, railings, windows), drawn in the same smooth, simplified way.
- Vehicles use two main colours. Liquids are clearly visible and richly coloured. Steam, if any, is soft, natural, semi-transparent white vapour like the steam over the cup in reference R4; never stylized swirls or ribbons.

Colour:
- A warm, juicy, inviting palette with bright, highly saturated colours. Never pastel, muddy or washed out.
- The background contrasts clearly with the object, ideally in its complementary colour, so the object never blends into it. No teal, grey, dark or muted backgrounds.
- Light sources (flames, lamps, glowing magic) glow inside the object only. No halo or light spill onto the background, which stays an even colour.

Background and context:
- Follow the background from the brief exactly, including its colour. Any pattern (rays, rings, motifs) is clearly visible and centred behind the object, and never bleak or empty-looking.
- For categories 1-3: floor or surface and wall are in clearly different tones. At most the one context cue from the brief; never a full scene, props or scenery.

Framing (sizes measured on the reference cards):
- One main object, centred. Its largest dimension spans about 80-88% of the image, never below about 75% and never above about 90%.
- Leave clear, empty background around it: at least 5% of the image on every side, and about 12-16% of the image height above it. Nothing touches or crosses an edge (only the ground of a category 4 scene may run to the bottom edge).
- The card is cropped to a slightly narrower shape (9 wide by 10 tall), so keep the object and its side margins inside the central 90% of the image width.
- The object sits in the vertical middle of the frame. On a surface (categories 2 and 3) it is not pushed down to the bottom with a big empty wall above it.
- Keep it readable at small card size: a few big, simple shapes. Leave out any detail smaller than about a twentieth of the image width (tiny rivets, fine textures, thin lines, many small repeated parts). In a category 4 scene, keep the environment to a few large, simple masses too: no fine fence slats, shingles, bricks or leafy clutter.

Composition, category {category}: {category_rules}

Output requirements:
- A single full-bleed illustration.
- No card frame, border, stars, ribbon, label, text, letters, numbers, logos or watermark.
- No people or characters, and no extra objects beyond the subject and what its category allows.
{fix}

## CATEGORY_1
The object has no small details and floats in the air, with no table, floor or ground under it, shown with a slight tilt or in three-quarter view. The background is a single saturated colour with a smooth gradient and one clearly visible pattern centred behind the object: radiating light rays, concentric rings or small repeated theme motifs.

## CATEGORY_2
The object has no small details and stands on a plain, flat surface of a single colour (not wood grain or a detailed table), seen from slightly above. Behind it is a plain vertical wall with a smooth single-colour gradient and no stripes. The surface and the wall share one warm or bright colour family that contrasts with the object, with the surface clearly lighter or darker than the wall.

## CATEGORY_3
The object stands on, or is set into, a simple realistic surface suited to it, such as a polished wooden tabletop, a glossy floor or a podium. The surface is painted in a smooth, stylized way, not photographically textured, with a soft reflection or contact shadow under the object. Behind it is a vertical wall in one colour, clearly different in tone from the surface: a smooth gradient, optionally with subtle rays or rings centred behind the object. Keep the background free of props, lights and scenery.

## CATEGORY_4
The object stands firmly on the ground of a realistic environment suited to it. A clear, wide band of ground (grass, sand, a street, a deck, rock or water) runs across the bottom of the image, so the object never floats or sits on a small tuft. The camera is low, so the object looks big, centred and heroic. The backdrop is the object's natural setting, as given in the brief, kept simple and bright. Open sky with a few soft, realistic clouds suits seaside, fields and tall buildings; a garden hedge, fence or wall, a forest edge, a mountainside, a pool or a warm sunset sky suit other places. No crowds, scattered props or busy terrain: the object stays the clear, central focus. The environment is painted in the same stylized way as the object.
