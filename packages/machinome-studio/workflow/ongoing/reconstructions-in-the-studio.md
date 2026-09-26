# Historical reconstructions in the studio: the tools the floor lacks

**Status: provisional roadmap, 2026-09-26.** Nothing here is ratified and
no OpenSpec change has been cut from it. It records the assessment the
pilot asked for on 26 September 2026 after deciding that the historical
reconstructions made so far directly from the workspace conversation —
Poleni's 1709 calculating machine, the Leonardo gallery's sawmill and loom,
the Curta, the Pascaline module and the stopped Astrarium — should become
possible on the studio floor, with the pilot supplying every tool the agents
need. It does *not* claim that any tool named below exists, that its name or
shape is settled, or that the order in §6 is a schedule. Where it disagrees
with a baseline spec under `openspec/specs/` or an accepted ADR under
`docs/adrs/`, the spec and the ADR are right and this note is stale. Under
the rule that every studio feature needs a need, each change cut from it
names the reconstruction that needs it then.

---

## 1. Why the floor cannot do it today

The floor's tool surface is closed by design. A profile's capability list is
the whole authority a session holds (ADR 0015, ADR 0026); each capability
resolves to floor MCP tools rooted at the active project
(`floor/mcp_server.py`, `PROFILE_TOOL_MAP`); the Claude adapter passes
`--strict-mcp-config` with the floor server alone and empties the built-in
tool set. Read from the code on 26 September 2026:

- `Bash` resolves to the Git, machinome and broker tools. There is no shell
  and no HTTP.
- `WebSearch` and `WebFetch` resolve to no tool at all. The librarian's
  prompt declares itself non-functional for this reason, and the
  architecture overview records the surface as "pending a bounded research
  surface".
- `read_file` returns PNG, JPG, GIF and WEBP files whole and unresized, and
  text-decodes everything else, so a PDF fails.
- The machinome tools are `machinome_build`, `machinome_test` and
  `machinome_snapshot`. The snapshot returns its image and leaves nothing in
  the project, and passes through neither `--drive` nor `--set`.
  `machinome export` and `machinome import-step` are not exposed.
- The `machinome` command is the one in the studio's own environment.
  Nothing installs what a project's `pyproject.toml` declares.
- There is no archive extraction, no `git clone` and no downloader.
- The floor MCP config admits no second server, so Context7 never reaches a
  session although the librarian's prompt names it first.
- The browser has no file upload. A maker's message is text.

## 2. What the reconstructions actually used

Evidence: the projects' own records — the Poleni sources register and
validation record, the sawmill and loom reconstruction records of the
Leonardo gallery, the Curta credits, the Pascaline download scripts, the
Astrarium closeout. Each was made by a repository agent with a full shell,
web tools, PDF and image reading, and the workspace venv.

**Research.** Web search for museum catalogues (Milan, Bonn, Florence),
digitised manuscripts (e-Leo's Codex Atlanticus, Google Books, Wikimedia
Commons) and scholarly PDFs (Hénin 2012, Etria 2010). Pages that render in
JavaScript were loaded in Chromium, because the initial HTML was empty.
Full-resolution images were reached through their own URLs. Everything was
downloaded into an ignored `sources/reference/` or `_reference/` cache, with
text sidecars extracted from the PDFs. Folios, plates and photographs were
inspected as images; the largest images were under a megabyte, the PDFs up
to 22 MB.

**Acquisition.** A `git clone` of an upstream STEP repository (Curta), a
Printables API downloader with a host allow-list (Pascaline), a zip file
(the mechanical multiplier), and `machinome import-step` to scaffold parts
and assemblies from the STEP document.

**Library documentation.** Context7, cited in the Leonardo validation
records.

**Execution.** Ad-hoc Python for numeric exploration — tooth counts, phase
sweeps, contact searches — and for the projects' own scripts (`scripts/check`,
`scripts/build`, `gallery.py`, `markings.py`, `prepare_sources.py`); pytest
suites beside the companion tests (Poleni's arithmetic tests run under
pytest, which `machinome test` does not run); `Sim` operation sessions.

**Dependencies.** Shapely, molejo and Playwright, present in the workspace
venv and installed by nothing the project declares.

**Delivery and evidence.** `machinome export` plus a project-owned operating
panel, served over HTTP and exercised by a Playwright check; snapshots and
logs kept under an ignored evidence directory and cited from the validation
record.

**Horizon.** The Curta took 203 commits over twelve days. The Astrarium was
stopped by the pilot on 20 September 2026 for cost and pace.

## 3. The gaps, as candidate floor tools

Each item states what the floor does today, what a reconstruction needs, and
the shape of a floor tool that would serve it. Names are placeholders.

### 3.1 Research surface

Today: none. Needed: search; fetch with JavaScript rendering, since the
museum catalogues used so far render in the browser; download of a page, a
scan, a photograph or a PDF into the project's ignored reference directory,
at full resolution. Candidate: `web_search`, `web_fetch` returning rendered
text and the links and image URLs found, and `web_download` writing only
under a project-owned, ignored `sources/reference/`, under a destination
policy (§5). This is the change the architecture overview already names as
pending.

### 3.2 Reading sources

Today: `read_file` fails on a PDF and sends an image unresized. Needed: the
text of a PDF page range, a rendered PDF page as an image, and a large scan
downscaled to what the model accepts. Candidate: `read_file` growing a PDF
branch (text with `pages`, or a page rendered to PNG) and an image branch that
downscales above a bound, so the record can still cite the original file.

### 3.3 Acquisition

Today: no archive extraction, no clone, no downloader, no `import-step`.
Needed only by reconstructions that start from an existing replica — the
Curta's STEP repository, the Pascaline's Printables files, a zip. A
reconstruction from sources alone, like Poleni's, does not need it.
Candidate: `extract_archive` into the project; `git_clone` into an ignored
vendor directory, pinned by commit as the simulate-project procedure already
requires; `machinome_import_step` as a fourth machinome tool.

### 3.4 Execution

Today: build, test and snapshot only. Needed: run a project script, run a
pytest suite, evaluate a short numeric experiment against the project's
model. Candidate: `run_script` for a file inside the project and `run_pytest`
for a path inside `tests/`, both with the project as working directory, a
time limit and captured output. This is the tool that carries the most
authority and is the one the containment work must design first (§5); a raw
shell is not the answer.

### 3.5 Dependencies

Today: the studio's environment, whatever it holds. Needed: what the project's
`pyproject.toml` declares — Shapely for Poleni, molejo for belts and cords,
Playwright for the browser check. Candidate: install the project's declared
dependencies into the studio environment at open time, or into a per-project
environment the `machinome` command then runs from, and report what was
installed. Which of the two is a decision for the isolation design.

### 3.6 Library documentation

Today: no second MCP server reaches a session. Needed: current third-party
documentation for CadQuery, build123d, Shapely and the like. Candidate: admit
Context7 as a second, named MCP server in the adapters' strict config, granted
to the roles that declare it. Cheap, and independent of the rest.

### 3.7 Delivery

Today: no export, no static server, no browser check. Needed for the
deliverable the site publishes and for a project-owned operating panel, not
for modelling: the studio viewer already covers live inspection. Candidate:
`machinome_export` as a machinome tool; a browser check is out of reach until
§3.4 and §3.5 exist.

### 3.8 Evidence

Today: a snapshot is tool output and leaves nothing behind, and cannot be
posed at a driver value. Needed: a posed view (`--drive`, `--set`) and a way
to keep the images a validation record cites. Candidate: pass the two options
through, and add an optional `save` under a project-owned, ignored evidence
directory. The Foundry rule that screenshots are never committed (§4) still
holds; the directory is ignored.

### 3.9 Maker input

Today: text only. Needed: a maker handing the agent a photograph, a scan or a
PDF they hold. On a local install the maker can copy the file into the project
directory by hand, which is a workaround. For browser delivery it is a
requirement. Candidate: an upload into the project's reference directory from
the workspace page, out of scope until the browser-delivery architecture is
chosen.

## 4. Process and policy gaps

These are not tools, but they decide where the tools go.

- **Nobody owns the historical research record.** A reconstruction begins
  with a source register, a documented-versus-inferred ledger and numbered
  decisions, before any drawing. The fordesmac designer owns parameters and
  contracts, the librarian owns library recipes and is switched off, and the
  foreman's pipeline starts at the first drawing. Builder could carry the
  whole job alone if it had the tools. Either fordesmac gains a research
  phase and an owner for that record, or historical reconstructions run on
  the builder profile first.
- **The committed screenshot conflicts with the Foundry policy.** The hub
  serves a project's committed preview, and `git_commit` refreshes and stages
  `screenshot.png` whenever model content is committed. The Foundry
  licensing policy of 20 September 2026 (recorded in the workspace) forbids
  committed screenshots in Foundry repositories, and Poleni ignores the file;
  for such a project the stage fails on the ignore rule, the commit proceeds
  with a warning and the hub card shows the placeholder. That is a decision
  for the pilot: an ignored, uncommitted preview the hub renders on demand, or
  an exception to the policy for the preview alone.
- **Creation seeds no licensing.** A new project is `machinome new` and one
  commit, "Initial machinome scaffold". The policy requires `CREDITS`,
  `NOTICE` and the licence texts, and no prompt asks for them. A creation
  option or a prompt line, once the policy's shape is settled.
- **Horizon and models.** Sessions are ephemeral and the project record must
  carry all state, which the roles already require. The profiles pin Sonnet
  for machinist and builder, where the reconstructions were made with
  Opus-class models; the project's `[tool.machinome-studio]` table can already
  select otherwise, and a reconstruction should.

## 5. Constraints the design must respect

The containment recommendations of 26 September 2026 (recorded in the
workspace, not ratified) ask for two things: role authority enforced at the
executor, not only in the backend's tool list; and project-code execution
isolated in a worker with a minimal environment, network denied by default
and any destination an explicit policy, resource limits, and the whole
process tree terminated on cancellation. Everything above is shaped by that:

- no raw shell returns; each capability is a floor tool with validated
  arguments and a project-rooted path;
- downloads land only inside the project's ignored reference directory, and
  the web tools are the floor's, with a destination policy the pilot sets;
- the script runner and the dependency install are the isolated worker's
  first two customers, so they are designed with it, not before it;
- reads of PDFs and images are bounded in size and page count like the
  existing text reads.

## 6. Proposed order

Each step is one or more OpenSpec changes, each cut only when the
reconstruction that needs it is named. Nothing is cut from this note yet.

1. **Bounded research surface** — §3.1, §3.2, §3.6. Without it a
   reconstruction cannot begin on the floor, and it is the gap the
   architecture overview already acknowledges.
2. **Project-bounded execution** — §3.4, §3.5, designed together with the
   isolation worker the containment recommendations ask for.
3. **Acquisition** — §3.3, when the first replica-based reconstruction is
   chosen for the floor.
4. **Evidence and delivery** — §3.8, §3.7.
5. **Roles and policy** — §4, with the screenshot decision and the research
   record's owner settled before the first floor reconstruction commits.

The first historical-queue reconstruction the pilot runs on the floor
validates the set. The workspace's historical queue has Poleni done and the
Astrarium stopped; its next open items are al-Jazari's twin-cylinder pump and
elephant clock. Which one, and on which profile, is the pilot's choice.

## 7. What this note does not decide

Tool names and signatures; the worker technology; whether the librarian, a
new role or the builder owns the research record; which profiles declare
which of the new capabilities; the screenshot policy; and whether browser
delivery changes any of it.
