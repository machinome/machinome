# Text animation

## Purpose

Let Leonardo's *Revolutions* words and titles follow the intended spoken or
even rhythm, and bring the syntax study's measured source-word emphasis into
ordinary Videomaker episodes.
## Requirements
### Requirement: An overlay's words appear as the narration speaks them

In format `machinome-video-draft/0.4` the author SHALL be able to declare that an
overlay's words appear one by one as the same shot's narration speaks them, and
in a movie document that a title's `show` reveals its words as its chapter's
narration speaks them. The spoken passage SHALL be the overlay's or title's text
or an explicit phrase of the narration that differs from it only in case and
punctuation, word for word, and it MUST be spoken exactly once in that shot's
narration, or in a movie document in the chapter's. Each word SHALL appear at
the instant the cached narration starts to say it and stay until the overlay or
the title's `show` ends. Words not yet shown MUST keep their place, so the text
never reflows as words arrive. Timing MUST come from the recorded speech, never
from an estimated reading speed.

#### Scenario: Propose, inspect, correct
- **WHEN** *Revolutions* `judgment`, restaged in 0.4, reveals "Propose. Inspect.
  Correct." with spoken timing
- **THEN** "Propose." appears on the first frame at or after the narrator starts
  saying it (3.532 s into the shot with today's take), "Inspect." and "Correct."
  join it as they are said, and all three stay in place until the overlay ends.

#### Scenario: Displayed in capitals
- **WHEN** the overlay shows "PROPOSE. INSPECT. CORRECT." with the phrase
  "Propose. Inspect. Correct."
- **THEN** each capitalized word appears when its spoken word begins.

#### Scenario: A spoken alias
- **WHEN** the displayed word is "Machinome" and production speaks it as
  "machine-ohm"
- **THEN** the word appears when "machine-ohm" begins.

#### Scenario: A title spoken in a later shot of its chapter
- **WHEN** a title of *Cut and Advance* reveals "One wheel, two jobs" as spoken,
  in the second shot of its chapter
- **THEN** each word appears at its measured onset in the chapter's take,
  counted from that shot's start.

### Requirement: Spoken timing is refused when the words cannot be matched

`check`, `speech`, `preview` and `render` MUST refuse a spoken reveal, naming the shot
and the overlay, when its phrase is not in the shot's narration or is there more than
once; when the displayed words differ from the phrase's words other than in case and
punctuation, or in number; when a displayed word cannot be spoken (punctuation only);
when the phrase is not in the recorded speech of that shot exactly once; when the
recorded timing is malformed or its words do not follow in order; when a word is
spoken a frame or more before the overlay begins; and when a word would appear on no
global output frame before the overlay ends.

#### Scenario: Words the narrator does not say
- **WHEN** *Revolutions* `genome` asks for "Pause. Inspect. Test." to appear as
  spoken, while the narration says "Pause it. Look inside. Test a connection."
- **THEN** `check` refuses, naming the first word that differs, and the author
  chooses an even reveal or none.

#### Scenario: An ambiguous phrase
- **WHEN** the phrase is "the", said several times in the shot
- **THEN** the reveal is refused as ambiguous before any frame is drawn.

#### Scenario: Speech regenerated
- **WHEN** a new take moves "Correct." past the overlay's end
- **THEN** `speech` reports the refusal after caching the take, and `check`,
  `preview` and `render` refuse until the cue or the narration is revised.

### Requirement: Words can appear at an even pace

The author SHALL be able to reveal an overlay's words across a span at the start of
the overlay, with a named easing from the campaign vocabulary, `linear` when none is
named. The first word SHALL appear with the overlay, each word SHALL take an equal
share of the eased span, and every word SHALL be shown once the span is over. A span
longer than the overlay, and a word that would appear on no frame, MUST be refused.

#### Scenario: Pause, inspect, test
- **WHEN** `genome`'s "Pause. Inspect. Test." is revealed evenly over 2.4 seconds
  from 6.899 s
- **THEN** "Pause." shows at 6.899 s, "Inspect." joins at 7.699 s and "Test." at
  8.499 s, and all three stay to the overlay's end.

### Requirement: Measured timing never buys speech

Measured timing (spoken reveals and source emphasis) SHALL be read only from the
speech that the `speech` command has already cached for that shot, the same take the
film's narration is mixed from. `check`, `preview` and `render`, including a silent
render, MUST NOT generate or purchase speech; when a needed take is missing or its
narration has changed, they MUST refuse, naming the shot and asking for the `speech`
command to be run first. A silent render MUST use the same measured timing as the
narrated film and MUST NOT substitute another timing. Episodes without measured
timing MUST need no speech for `check`, `preview` or a silent render.

#### Scenario: Checked before speech exists
- **WHEN** a new episode with a spoken reveal is checked before `speech` has run
- **THEN** `check` refuses with "run the speech command first" and nothing is
  requested from the speech provider.

#### Scenario: A silent look
- **WHEN** an episode whose speech is cached is rendered with `--silent`
- **THEN** its words appear at the same frames as in the narrated render.

#### Scenario: A silent look without speech
- **WHEN** the same episode is rendered with `--silent` before `speech` has run
- **THEN** the render refuses rather than revealing the words at other instants.

### Requirement: A title with a line beneath it, fading in and out over the model

The author SHALL be able to show a title: text with an optional line beneath
it, shown for a timed interval, which MAY fade in at its start and out at its
end over a stated duration with a named easing (`smooth` when none is named).
In a movie document a title SHALL be a `title` element the chapter declares,
placed by a shot in a slot of its set and shown by a `show` action; the set
decides where the slot is and how the title looks in it. In a 0.4 episode a
title SHALL be an overlay at `position: title`, and every overlay SHALL be
drawn in the paper sets' slot for its position (`top`, `lower-third`,
`center`, `title`), large and centred for a title, over the model. The model
beneath MUST keep its pose, motion, camera and visibility exactly as the shot
declares. The first frame of a fade-in MUST show no title, and a title that
has faded out MUST stay out. Two titles of one shot MUST NOT overlap in time,
fades MUST fit within the title's interval, and a title whose text leaves the
frame MUST be refused at the frame where it does, naming the shot and time.
Preview MUST compare a fading title as authored, fully drawn and absent at the
same model and video instant; model motion between frames MUST NOT stand in
for evidence that the fade reached the pixels.

#### Scenario: The title arrives after the first sentence
- **WHEN** *Revolutions* `revolution`, restaged in 0.4, sets "REVOLUTIONS" as a title
  from 2.941 s with a one-second fade-in
- **THEN** the wheel keeps turning beneath it, the title is absent at 2.941 s, grows
  in over the next second, and stays until the cut.

#### Scenario: Title and line
- **WHEN** `river` sets "Leonardo's hydraulic sawmill" as a title with the line
  "Digital reconstruction of a later museum interpretation" beneath it
- **THEN** both appear, fade and leave together, over the pulling-out camera.

#### Scenario: A title in the template's headline
- **WHEN** a shot of *Cut and Advance* places the title "CUT AND ADVANCE" in
  `LeonardoSplit`'s `headline` and shows it with a fade-in
- **THEN** it fades in inside the box `LeonardoSplit` draws for `headline`, in
  the type the set gives that slot, above the source panel and the view.

### Requirement: Source words light up as the narrator says them

A code shot of a 0.4 episode, and a source panel of a movie document, SHALL be
able to light chosen tokens of the shown excerpt as the narrator says chosen
words of a stated phrase: each token lights at the instant its spoken word
begins, the lit tokens accumulate, and all clear together a stated hold after
the phrase ends. The phrase MUST be spoken exactly once in the shot (in a
movie document, in the chapter), each spoken word MUST occur exactly once in
the phrase, the words MUST follow the order in which they are spoken, and each
token MUST already be typed on screen when its word is spoken.

In an episode the spoken word and the token SHALL be the same identifier,
found exactly once in the one line the emphasis names. In a movie document a
token SHALL be an identifier or a dotted path of identifiers, bounded by
anything other than an ASCII letter, digit or underscore, a dot being a
boundary; it MAY differ from its spoken word; and it MUST occur exactly once in
the whole excerpt, on any line, or, when the emphasis names a `line`, exactly
once on that line. The source text MUST NOT change; only its tokens are marked.
Marking MUST preserve every source character and safe HTML escaping.

#### Scenario: The waterwheel drives the crankshaft
- **WHEN** a 0.4 code shot showing export-pinned `model.py` line 415 lights
  `waterwheel`, `drives` and `crankshaft` on "Here, the waterwheel drives the
  crankshaft." with a 0.9-second hold
- **THEN** `waterwheel` lights as it is said, `drives` and `crankshaft` join it as
  they are said, and all three clear together 0.9 seconds after "crankshaft." ends.

#### Scenario: A word that is not in the line
- **WHEN** the author of an episode lists `waterwheeel`, or a word that appears
  twice in the line
- **THEN** loading the episode refuses it, naming the word, the line and the shot.

#### Scenario: A dotted token on another line
- **WHEN** a movie document's emphasis pairs the spoken "the driving pawl" with
  the token `feed.pawl.turn`, which occurs once in the excerpt, on its third
  line, typed before the phrase is spoken
- **THEN** `feed.pawl.turn` lights on that line when "driving" is spoken,
  though the emphasis names no line.

#### Scenario: A token that repeats
- **WHEN** a movie document's emphasis lights `spin`, which occurs on two lines
  of the excerpt, without naming a `line`
- **THEN** it is refused naming the token and the excerpt; naming the line on
  which it occurs once lights it there.

#### Scenario: Lit before it is typed
- **WHEN** typing reaches line 415 only after "waterwheel" is spoken
- **THEN** the emphasis is refused, naming the word and the time.

### Requirement: Animated text is reproducible and proven in preview

A frame with revealed words, a fading title or lit source words MUST depend only on
its video time, the episode and the cached speech; seeking away and back, or resuming
a render, SHALL yield identical pixels. `preview` MUST show each reveal at its start,
midpoint and end with the number of words the rule gives, each title fade reaching
the pixels (nothing at a fade-in's first frame, part of the title halfway), and each
lit source word at its onset with the right text, and MUST refuse any frame where the
drawn words differ from the rule.

#### Scenario: Revisit a half-revealed instant
- **WHEN** preview poses an instant with two of three words shown, poses another
  instant, and returns
- **THEN** the same two words and the model pixels match the first capture.

### Requirement: Older episodes are handled explicitly

Episodes in formats 0.2 and 0.3 SHALL parse and render without the fields of
format 0.4, their overlays drawn in the paper sets' position slots as every
episode's are. The new fields and the title position MUST be refused in them,
naming the shot and asking for format 0.4. In 0.4, overlays, the code field,
typing cues and every new cue MUST refuse fields they do not know, naming the
field, the cue and the shot. An overlay declaring no 0.4 field SHALL be drawn
in 0.4 exactly as in 0.3, on the same sets.

#### Scenario: A reveal in a 0.3 episode
- **WHEN** a 0.3 episode gives an overlay `reveal`
- **THEN** `check` refuses it and asks for format 0.4, rather than showing all the
  words at once.

#### Scenario: A misspelled field
- **WHEN** a 0.4 overlay spells `revael`
- **THEN** `check` refuses the unknown field instead of ignoring it.

