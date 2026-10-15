# QA prompt v2

Sent to a vision model with the candidate image and two reference cards of the same category. The checks mirror rulebook section 7.

**What changed from QA v1:** the judge now sees the planned background. The fail examples now include the defects that Pavel and the external model named when rating the 120 Cinema cards (W016).

**What this judge is for:** that rating round showed it does not predict Pavel's scores. Cards it passed met his bar 73% of the time; cards it flagged, 60%. So it is a gate for brief compliance and visible defects, not a stand-in for his taste. The background colour family is checked separately, by pixels, in `colour_check.py`.

Placeholders: {name}, {subject}, {unique_detail}, {background}, {category}, {category_rule}. Literal braces are doubled, because the template goes through Python's str.format.

## PROMPT
You review card illustrations for a casual mobile game. Image 1 is the CANDIDATE. Images 2 and 3 are REFERENCE cards from the game, in the same composition category; they show the required art style.

Candidate brief: "{name}". Object: {subject}. Its charming detail: {unique_detail}. Planned background: {background}. Composition category {category}: {category_rule}

Check the candidate against each rule. Be strict, the way an art lead would be.
1. subject: it is clearly the requested object, recognisable at a glance, and complete with its standard parts (fail examples: a tea cup without its saucer; a bumper car without its pole; a dish that is not obviously the named dish).
2. category: the composition follows the category rule above (fail examples: a wooden table under a category 2 object; a busy room or scenery behind a category 3 object; a category 4 object floating in the sky or standing on a small tuft instead of wide ground).
3. clean: no text, letters, numbers, logos, card frame, border, UI or watermark; no people or characters.
4. framing: one central object with a chunky, solid silhouette and clear margins on every side; it is not oversized or crowding the edges, not too small or thin to read, and nothing important is cut off (a category 4 object may touch the bottom edge).
5. colour: bright, warm, saturated and juicy overall; the background follows the plan; the object clearly separates from the background (fail examples: a blue object on a blue background; a lamp's glow spilling onto the wall so that light and background blend); the background is not teal, grey, dark or muted.
6. detail: no micro-detail on the object (droplets, grooves, ridges, scratches, busy patterns) and no clusters of many small repeated elements (dozens of tiny roses, gems or locks; lattice; filigree); no extra props or scenery beyond what the category allows.
7. style: rendered like the references: smooth chunky volumes, satin sheen, no outlines, not painterly, not photographic, not flat; materials read correctly (fail examples: gold that looks like yellow plastic; fabric or feathers that look like moulded rubber; water that looks like solid plastic ribbons).

Answer with JSON only, in this exact shape:
{{"checks": {{"subject": {{"pass": true, "why": "..."}}, "category": {{"pass": true, "why": "..."}}, "clean": {{"pass": true, "why": "..."}}, "framing": {{"pass": true, "why": "..."}}, "colour": {{"pass": true, "why": "..."}}, "detail": {{"pass": true, "why": "..."}}, "style": {{"pass": true, "why": "..."}}}}, "pass": true, "fix": "one sentence telling the artist exactly what to change, or an empty string if everything passes"}}
