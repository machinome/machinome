## MODIFIED Requirements

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
