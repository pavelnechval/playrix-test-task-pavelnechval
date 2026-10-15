# Card-set rulebook v2

This file is the source of truth for the planner (the agent writing `plan.json`), the generation prompt and the automatic QA.

Each rule cites where it comes from:

- **[brief]**: the assignment pages.
- **[refs]**: observed in the reference cards and sets (Miro originals, 16×10 sheet). **[refs160]**: the review of all 160 reference cards in W016.
- **[P]**: Pavel's rating notes. **[X]**: an external model's ratings. Both are from BENCH-01–03 in `experiments/`.
- **[P2]** and **[X2]**: the same two raters on the 120 Cinema cards (W016, `sets/ratings/rating_numbers.md`). Card codes such as LC-A06 point to the rated card.
- **[est]**: our estimate, to be checked.

v2 changes (W016): category 4 ground and backdrops; materials; sparse decoration; light spill; the planned background colour is checked by pixels.

Set-level principles live in `set_guidelines.md`: one moment, mood, a crescendo by rarity, and a theme-tinted palette with a window colour. They come from the 16 set windows of the reference collection.

## 1. Collection and set structure

- A **collection** has one broad theme (here, Cinema) and 16 sets. Fifteen are object sets; the 16th is a "grand" set of gold character cards only. [brief]
- A **set** is a sub-theme with its own name, here a film genre such as "Love in the City". It has **exactly 10 cards**, and for this task all 10 are object cards: no gold cards, no characters. [brief, D-004]
- **Every set contains all 4 composition categories,** regardless of rarity. Rarity never changes how an object is drawn. [brief]
- **Default category mix:** 3 × C1, 2 × C2, 2 × C3, 3 × C4. Each category appears 1 to 4 times.
  - [est] from ~50 classified reference cards (rows 1, 2, 5, 6, 7), where per set C1 ranged 1–4, C2 1–2, C3 2–3 and C4 2–5.
- **A variant** is a complete alternative 10-card set for the same sub-theme. Variants take different angles, for example props versus places, and share at most about 3 objects. [D-006]

## 2. Choosing the 10 objects (set coherence)

- **Every object must say "this sub-theme" on its own, at thumbnail size.** These are the iconic props and places a player connects with the genre, the way the Beach set uses a sandcastle, umbrella, beach ball, cooler and lifeguard tower. [refs]
  - A generic object (a coin, key or shovel) needs a visible cue that ties it to the set, such as a coin half-buried in treasure sand. [P2: LI-B01 "do not see connection to set"]
  - The object must read as the named thing at a glance; a casserole that looks like a plain pot fails. [P2: PP-C04]
- **Mix object types:**
  - small hand-held props;
  - food or drink;
  - furniture or devices;
  - vehicles;
  - big structures, landmarks or places (usually C4). [refs]
- **Use distinct silhouettes.** No two objects of the same shape class in one set: not two bottles, not two boxes. [refs]
- **No generic filler.** Cinema equipment (camera, clapperboard, popcorn) only appears if it clearly serves the genre. Generic props would make all genre sets look alike. [W001]
- **Family-friendly, warm and inviting.** No weapons, blood, scary content, alcohol or kissing figures. [refs, est]
- **No intellectual property:**
  - no brand names, logos, film titles or famous characters;
  - no trademark designs (for example the Oscar statuette);
  - fairytale motifs must use generic public-domain forms only. [brief: production-ready assets]
- **No text anywhere.** Letters, signs, tickets and posters are blank or use simple symbols such as hearts and stars. [refs, P]
- **No people or characters.** Natural animals may appear only rarely, as part of the scenery: the references have swans, a jellyfish and a seahorse. A tiny animal detail (a ladybug) or an animal-shaped object (a horse weather vane) is fine; an animal as the card's subject is a character and is not. [refs, brief, W018]
- **Ordering:** cards follow their stars (1, 1, 2, 2, 3, 3, 4, 4, 5, 5), so the set builds from everyday props to the big places and the climax. Inside that order, mix categories and colours so the 5×2 window reads varied. [refs160: final set windows and templates]

## 3. Composition categories

| Category | Rule [brief] | Observed in the references [refs] and rater notes [P][X] |
|---|---|---|
| **C1** floating | No small details; floats in the air; background is a single colour with a gradient or a simple pattern (stripes, repeated objects, flat colour, light rays). | Slight tilt or three-quarter view. The pattern is centred behind the object: rays, concentric rings, waves, or **theme motifs** (π symbols for Finals, music notes for Music Fest, scout lilies for Boyscouts). The pattern must be clearly visible, not bleak [P]. **A chunky, solid silhouette that fills the frame;** thin or open objects (hoop, shovel, key, rings) are drawn thicker and turned to their broadest side. [est: C1 was Pavel's weakest category, 21 of 36 passed; the assistant's reading of the low-rated cards, P2] |
| **C2** on a simple surface | No small details; stands on a surface; simple background (plain or gradient wall, or a simple pattern). | The surface is a **plain one-colour plane, not wood grain** [P]. Surface and wall share one warm or bright colour family that contrasts with the object [refs]. A plain gradient beats stripes [P]. |
| **C3** on a realistic surface | Stands on, or is set into, a simple realistic surface; vertical wall behind (plain, gradient or simple pattern). | Polished wood, a glossy floor or a podium, with a soft reflection [P]. Floor and wall in **different tones** [P]. At most one context marking, such as the stripe on the rink floor [P]. Wall in one colour, no props, no theatrical lights [P][X]. |
| **C4** in an environment | Set into a realistic surrounding environment but stays central. | **Low camera angle; the object is big** [P]. **It stands on a wide band of visible ground** (grass, sand, street, deck, water), never floating or on a small tuft [P2: LC-A06 "floating in the air instead of terrain", PP-C06 "terrain is missing"]. **The backdrop is the object's natural setting**: open sky with soft, realistic clouds for seaside, fields and tall buildings [P]; garden hedges, fences or walls, forest edges, mountains, pools or sunset skies elsewhere [refs160; P2: LI-B10, LI-C06 "does not have to be sky"]. May be slightly cropped at the bottom edge [refs]. *Superseded v1 rule: "only a strip of setting, terrain mostly left out, blue sky". It was learned from the lighthouse benchmark alone, and it gave all 36 Cinema scene cards the same sky.* |

## 4. Art rules (each one learned from feedback)

**Rendering:**

- Clean, polished 3D game-asset finish: smooth, chunky, simplified volumes, rounded edges, slightly exaggerated proportions. [refs]
- Satin sheen, not wet-look or chrome. [P]
- No outlines, painterly strokes, flat cel shading or photographic lighting. [X]
- Bright, even, cheerful lighting, never theatrical or moody. [X, P]
- **Materials read at a glance:**
  - metal has bright, sharp reflections and never looks like plastic [P2: LC-C01];
  - fabric is thin with natural folds, not moulded rubber [P2: PP-B01; X2: PP-B01, PP-C08];
  - water is clear and translucent, not solid ribbons [P2: PP-C03; X2];
  - stone and rock are smooth, chunky planes [P2: LI-B06].
  - Avoid hair as a subject. [P2: OG-B03 "hair is weird"]

**Object:**

- Use the most typical silhouette, from the object's most familiar angle. [P]
- **Complete, with its standard parts:** a cup with its saucer, a dodgem with its pole. [P BENCH-03]
- **Smooth manufactured objects:** no grooves, ridges, panel lines, droplets or grip textures. [P][X]
- **One distinctive, charming detail,** like the painted flower on the reference cup, instead of generic stripes or bands. [P BENCH-03]
- **Bold, sparse decoration:** a few large shapes, never clusters of many small ones (roses, gems, locks, lattice, filigree). [P2: six "too detailed" comments, e.g. LC-C05, LC-C06, OG-B06; X2: about 15 cards]
- Built structures keep their crafted features (bricks, railings, windows). [X]
- Vehicles use two main colours. [P]
- Liquids are clearly visible and richly coloured. [P]
- Steam is soft, natural, semi-transparent vapour, like the reference tea cup's. [P2: LC-B05 "steam is far from ref"; replaces v1's "2–3 thin, wispy strands", which came out as stylized swirls]

**Colour:**

- Warm, juicy, inviting palette; warm reds rather than crimson. [P]
- The background is complementary to the object's main colour and never blends with it. [P][refs]
  - The object and its background never share a colour family; the validator warns. [P2: 3 of 7 such cards passed, against 72% overall]
  - A warm object on a warm background of a different hue is fine. [P2: 69% passed vs 73% for the rest, no real difference]
- Light sources glow inside the object only, with no halo or light spill on the background. [P2: LI-C02 "background color blending with light"]
- The background is the planned colour family. This is checked by pixels, not by the vision model. [W016: two cards ignored the plan (teal instead of orange, red instead of green), both rated 3 or lower, and the QA judge missed both]
- Allowed background families: red, orange, yellow, green, blue (including bright sky), purple, pink. **No teal, grey, dark or muted.** [P]

**Framing:**

- One main object, centred.
- **Object size and breathing room,** measured on the 160 reference cards (W019, `card_metrics.py`):
  - The object's largest dimension is a median of 0.82 of the card in C1, 0.85 in C2, 0.89 in C3 and 0.85 in C4. The middle half is about 0.76–0.94.
  - Smallest margin 0.04–0.08; room above 0.12–0.16.
  - `reframe.py` brings every card to these values after generation. Prompts alone did not hold them: ChatGPT ignored numeric framing, and v4's "60–75% of the height" left Gemini's C1 objects small. [refs160, P W019: "issue with object size and breathing room"]
- **Detail must survive the card size.** Our "detail lost at 66 px" measure is a median of 9.6 for the reference cards; scenes above about 13 read as cluttered. [refs160, P W019]
- Never cut by the frame. C4 may touch the bottom edge.

**Overall:** a bright image, readable at 66 px card size. [P][brief]

## 5. Colour across a set [refs160, measured in analysis/set_palette_profile.md]

- **A leading colour family expresses the set's mood on 3–5 cards.** The 15 reference object sets: the leading family covers 2–6 cards, 3.8 on average. Diving is teal and blue, Countrystead green, Coolness orange.
- **5–6 colour families per set** (reference sets: 4–7, mean 5.5). Families other than the lead appear on at most 3 cards.
- **Warm-led sets are fine when the theme is warm.** Reference sets average 3 warm backdrops out of 10, but Coolness, the heat set, has 5. A desert Western or a sunset romance may lead with warm colours.
- **At most 2 same-colour neighbours** in the 5×2 window, left-right or above-below (reference sets: 1.7 of 13 pairs on average). A bright sky counts as blue.
- **Theme motifs** may appear in C1 patterns: hearts for romance, stars for fairytale, and so on.
- *v1 rule, kept only for schema-1 plans: no neighbouring cards in the same family, at most 4 cards of one family.*

## 6. `plan.json` schema 2 (written by the planner)

Schema 2 adds the **set bible** from `set_guidelines.md`:

- per variant: a moment, a mood, the leading colour, the window colour and a motif;
- per card: a role, stars and light.

```json
{
  "schema": 2,
  "collection": "Cinema",
  "set": "Love in the City",
  "genre": "Romantic comedy",
  "wishes": "free-form producer wishes",
  "variants": [
    {
      "id": "A",
      "concept": "one line: what makes this variant different",
      "moment": "one sentence: the single situation the ten cards belong to",
      "mood": "one word or short phrase: the feeling the set gives",
      "lead_color": "pink",
      "window_color": "pink",
      "motif": "hearts",
      "cards": [
        {
          "id": "A01",
          "name": "Matching Mugs",
          "category": 2,
          "role": "food",
          "stars": 1,
          "light": "day",
          "subject": "full description of the object and its form",
          "unique_detail": "the one charming detail",
          "main_colors": "the object's main colours",
          "background": "background colour and pattern, or for C4 the environment and its time of day",
          "bg_color": "yellow",
          "context_cue": "optional single cue, or empty",
          "why": "why it belongs in this set"
        }
      ]
    }
  ]
}
```

**Field rules (`cardgen.py validate` checks them):**

- **Card order is star order:** 1, 1, 2, 2, 3, 3, 4, 4, 5, 5.
  - **Commons are small but unmistakable props of the theme.** Every card must pass the name test on its own, commons included: Sandcastle, Diving Mask, Grad Cap, not generic pancakes or a handbag. W018: the commons were the weak end of all three Western variants.
  - **The 4–5-star cards are the big places plus the most iconic or precious objects.** With 3 category 4 scenes, one top slot holds a signature object (a saddle, a guitar). At least one 4–5-star card is a category 4 scene, and the last card is the climax.
- **`role`:** one of `carry` (a thing you carry or wear), `food` (food or drink), `gear` (a gadget, furniture or gear), `vehicle`, `place` (a place, building or landmark) or `nature` (a natural thing: a plant, animal, rock, shell or celestial body). At least 4 roles, at most 4 cards per role.
- **Settings without ground (space, underwater, sky)** [W030]: ships and stations float as category 1. A category 4 scene stands on a planet surface, a deck or the sea floor. Open space counts as a night scene in saturated blue.
- **Category 3 surface** [W030]: prefer a wooden or textured tabletop or a podium. A plain glossy floor is often read as category 2 by the measurement, and it is harder to tell apart for players too.
- **`light`:** `day`, `sunset` or `night`. At most 2 cards that are not `day`. Describe the light in `background` too.
- **Colours:**
  - `bg_color` and `lead_color` are one of red, orange, yellow, green, blue, purple, pink.
  - **For a C4 card, `bg_color` is the colour of the upper backdrop.** That is usually the sky: blue by day, orange at sunset, blue at night. Plan green, for example, only when no sky shows, as with a forest wall, a hedge or a building filling the top. W018: two "green" scenes with sky above them measured blue.
  - `window_color` is one of the 4 templates: orange, pink, violet, blue. ("violet" names the template; the backdrop family is "purple".)
  - **Reusing a window colour within a collection is normal.** The "Summer" collection has 4 blue, 3 green and 3 orange windows.
- **`name`:** 1–2 words, up to 16 characters, like the reference labels ("Tea Cup", "Hoop Shot"). One or two playful names per set.

## 7. QA checklist (an automatic fail triggers a retry with a fix sentence)

Checks 1–7 are made by the vision judge (`prompts/qa_v3.md`), and check 8 by pixels (`colour_check.py`).

1. **Subject:** clearly the specified object, recognisable at a glance, complete with its standard parts.
2. **Category:** the composition matches the card's category rule. A category 4 object stands on wide ground.
3. **Clean:** no text, letters, numbers, logos, frames, borders, UI or watermark; no people or characters.
4. **Framing:** one central object with a chunky silhouette and clear margins; nothing important cut by the frame.
5. **Colour:** bright, warm and saturated; the background follows the plan; the object separates clearly from the background; no light spill; no teal, grey or dark background.
6. **Detail:** no micro-detail on the object; no clusters of many small repeated elements; no props or scenery beyond what the category allows.
7. **Style:** matches the reference rendering (smooth, chunky, satin, no outlines, not painterly or photographic), and the materials read correctly.
8. **Background colour (pixels):** in categories 1–3, the measured colour family is the planned one or its neighbour on the colour wheel, and the background is not teal.

**What the QA can and cannot do (W016):**

- The vision judge is a gate for following the brief and for visible defects. It does not predict Pavel's taste: 73% of the cards it passed met Pavel's bar, against 60% of those it flagged.
- Taste is settled by the human rating loop: the rating workbook, then `rating_report.py`, then `redo.py`.
- A producer's note given to `regen` or `redo` is kept in every retry. The reviewer's fix is added to it, never swapped in.
