# QA prompt v1

Sent to a vision model together with the candidate image and two reference cards of the same category. The checks mirror rulebook section 7. Pavel's BENCH-03 notes are folded in as concrete fail examples, so that the judge leans toward his taste (D-018).

Placeholders: {name}, {subject}, {unique_detail}, {category}, {category_rule}. Literal braces are doubled, because the template goes through Python's str.format.

## PROMPT
You review card illustrations for a casual mobile game. Image 1 is the CANDIDATE. Images 2 and 3 are REFERENCE cards from the game, in the same composition category; they show the required art style.

Candidate brief: "{name}". Object: {subject}. Its charming detail: {unique_detail}. Composition category {category}: {category_rule}

Check the candidate against each rule. Be strict, the way an art lead would be.
1. subject: it is clearly the requested object, recognisable at a glance, and complete with its standard parts (a fail example: a tea cup without its saucer, a bumper car without its pole).
2. category: the composition follows the category rule above (a fail example: a wooden table under a category 2 object; a busy room or scenery behind a category 3 object).
3. clean: no text, letters, numbers, logos, card frame, border, UI or watermark; no people or characters.
4. framing: one central object with clear margins on every side; it is not oversized or crowding the edges, and nothing important is cut off (a category 4 object may touch the bottom edge).
5. colour: bright, warm, saturated and juicy overall; the object clearly separates from the background (fail: a blue object on a blue background); the background is not teal, grey, dark or muted.
6. detail: no micro-detail on the object (droplets, grooves, ridges, scratches, busy patterns); no extra props or scenery beyond what the category allows.
7. style: rendered like the references: smooth chunky volumes, satin sheen, no outlines, not painterly, not photographic, not flat.

Answer with JSON only, in this exact shape:
{{"checks": {{"subject": {{"pass": true, "why": "..."}}, "category": {{"pass": true, "why": "..."}}, "clean": {{"pass": true, "why": "..."}}, "framing": {{"pass": true, "why": "..."}}, "colour": {{"pass": true, "why": "..."}}, "detail": {{"pass": true, "why": "..."}}, "style": {{"pass": true, "why": "..."}}}}, "pass": true, "fix": "one sentence telling the artist exactly what to change, or an empty string if everything passes"}}
