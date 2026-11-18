# Leahe

A terminal utility for mood tracking and cognitive restructuring powered by Cognitive Behavioral Therapy (CBT) principles. Designed with zero emojis, clean ASCII typography, and detailed statistical analytics.

---

## Features

- **Strictly No Emojis**: Clean, professional terminal interface utilizing ASCII indicators (`[*]`, `[+]`, `[-]`, `[!]`, `[x]`, `[o]`, `#`, `|`).
- **Anywhere Terminal Access (`leahy` / `leahe` / `mood`)**:
  - Install to `~/.local/bin` with `./leahe install-cli` or `pip install -e .` to execute `leahy` from any directory.
- **Markdown Notes Storage in `~/Notes`**:
  - All check-ins, CBT thought records, and freeform notes are automatically saved as clean individual `.md` files in `~/Notes` with standard YAML frontmatter.
  - Fully compatible with Obsidian, Logseq, Foam, VS Code, and static site generators.
  - Configurable directory via `--notes-dir <path>` or the `LEAHE_NOTES_DIR` environment variable.
- **Effortless YAML Conversion & Moving (`leahe to-yaml`)**:
  - Move note files anywhere and convert them into convenient, structured YAML files with `leahe to-yaml` (or alias `leahe yaml`).
  - Batch convert individual Markdown notes to `.yaml` files or combine them into a single consolidated YAML archive (`--single`).
  - Convert YAML files back into Markdown notes anytime with `leahe to-md`.
  - Bidirectional synchronization between `~/Notes` and the SQLite database (`leahe sync`).
- **Note Taking & Reflections (`leahe note` / `leahe write`)**:
  - Quick terminal reflection: `leahe note "Evening walk" --mood 8 --tags "relax,walk"`
  - Full editor mode: `leahe note --edit` opens your `$EDITOR` with a pre-filled Markdown/YAML template.
  - Browse notes directly: `leahe notes` (or `leahe list-notes`).
- **Behavioral Experiments Lab (`leahy experiment` / `leahy exp` / `leahy test-fear`)**:
  - Test catastrophic fear predictions empirically: record predicted catastrophe and belief confidence (0-100%) -> execute real-world action plan -> record actual outcome and reality severity -> calculate **Fear Prediction Error** and **Disconfirmation Rate**.
  - In `leahy stats`, displays empirical fear overestimation audit showing how consistently anxiety creates false alarms.
  - Automatically saved to `~/Notes/` as individual Markdown notes with YAML frontmatter.
- **Exposure Ladder & Fear Hierarchy (`leahy ladder` / `leahy exposure`)**:
  - Systematic desensitization with Subjective Units of Distress (SUDS 0-100).
  - Create themed fear hierarchies, add graded challenge steps, and track habituation across repeated exposure trials (`pre_suds` -> `post_suds` -> relief delta).
  - Track mastery status per step when distress consistently subsides under 25 SUDS.
- **Decatastrophizing Protocol (`leahy decatastrophize` / `leahy decat`)**:
  - Rapid 4-step emergency anti-catastrophizing session: Worst Case -> Best Case -> Most Likely Realistic Scenario -> Concrete Coping Protocol.
- **Enhanced CBT Thought Record**:
  - **Downward Arrow**: Optional technique after NAT to peel back layers ("And what would that mean to you?") and expose core schemas for Burns Lab testing.
  - **Clinical Evidence Fact-Checking**: Detects subjective opinions or feelings in evidence fields (e.g. "I feel...", "I don't think...") and prompts for verifiable objective facts.
  - **Cognitive Defusion (ACT)**: 1-line mindful reframing at the conclusion ("I notice that I am having the thought that...").
- **Acute Distress First-Aid & Grounding (`leahy sos` / `leahy breathe` / `leahy ground`)**:
  - Physiological stabilization before cognitive restructuring (reversing amygdala hijack).
  - Paced interactive Box Breathing (4-4-4-4) and 4-7-8 Relaxation Breath with real-time ASCII progress bar.
  - 5-4-3-2-1 Sensory Grounding protocol to interrupt panic and cognitive racing.
  - Optional seamless transition into a guided CBT Thought Record once calm.
- **Positive Data Log & Wins Tracker (`leahy win` / `leahy credit`)**:
  - Clinical counterweight to Mental Filter & Disqualifying the Positive (Burns & Padesky).
  - Rapidly record competence, resilience moments, or boundaries held (`leahy win "Handled critical feedback calmly"`).
- **Behavioral Action Loop Accountability**:
  - Startup check-in gently surfaces pending action commitments from past CBT sessions to ensure behavioral activation.
- **Socratic Scaffolding & Reframe Formula**:
  - Type `?` or `help` when stuck finding contradictory evidence to access targeted clinical angles (Friend Lens, Past History, Alternative Explanations, Coping Capacity).
  - Structured reframe formula starter ("Even though..., reality is..., so I can...").
- **Categorized Clean Main Menu**:
  - Organized into 6 focused categories:
    1. Thought Records & Restructuring
    2. Behavioral Experiments & Exposure
    3. Pleasure Predicting & Action Steps
    4. Clinical Stats, DAS & Retrospective
    5. Notes & Sync (Markdown Notes & YAML Storage)
    6. Settings & Reference Guides
- **David Burns Pleasure-Predicting Sheet (`leahy predict` / `leahy complete`)**:
  - Test cognitive dread empirically by rating predicted difficulty (0-100%) and pleasure (0-100%) before starting an activity.
  - Return later with `leahy complete` to record actual pleasure and difficulty.
  - Analyzes your delusion shift (e.g. "+35% more rewarding and 40% easier than feared").
  - Automatically saved to `~/Notes/` as individual Markdown documents with YAML frontmatter.
- **Automated Systemd Practice Reminders & Desktop Notifications (`leahy systemd`)**:
  - Background systemd user timer (`systemctl --user`) sends scheduled desktop notifications using `notify-send`.
  - Smart notifications: notifies you of pending pleasure-prediction activities, reminds you to do a daily mood check-in, or provides David Burns CBT practice tips.
- **Dual Check-in Modes**:
  - **Quick Mood Check-in**: Record overall mood (1-10), primary emotion and intensity (0-100%), energy level, and brief context in seconds.
  - **Guided CBT Thought Record**: Full 7-step cognitive restructuring session:
    1. Objective situation/trigger definition.
    2. Emotion & initial distress rating.
    3. Automatic Negative Thought (NAT) & belief intensity (0-100%).
    4. Identification of cognitive distortions from a clinical taxonomy.
    5. Socratic questioning & evidence examination (facts for vs facts against).
    6. Balanced, rational alternative thought formulation.
    7. Post-intervention re-rating (calculating mood shift and relief).
    8. Constructive micro-action step (behavioral activation).
- **Comprehensive Statistics (`leahe stats`)**:
  - Overall mood trajectory and distribution (low, neutral, high).
  - CBT therapeutic efficacy (pre vs post mood shift, distress relief %).
  - Ranked prevalence of cognitive distortions with ASCII frequency bar charts.
  - Emotion distribution and average distress intensity.
  - Interactive ASCII mood timeline across recent entries.
  - Logging streaks (current and longest consecutive active days).
- **Pattern Verification & Clinical Audit (`leahe verify`)**:
  - Flags sessions where distress did not improve for targeted re-evaluation.
  - Detects severe distress episodes (mood <= 3).
  - Identifies your most frequent thinking trap (e.g. Catastrophizing or Mind Reading) and provides tailored antidote questions.
- **Reference Guide (`leahe distortions`)**:
  - Full catalog of 11 classic cognitive distortions (Burns/Beck) with definitions, examples, and targeted challenge questions.
- **Exporting (`leahe export`)**:
  - Export full history to structured Markdown or JSON for offline archiving or sharing with a therapist.

---

## Installation & Running Everywhere

### 1. Direct Execution
You can run the executable script directly from the project directory:

```bash
./leahy --help
# or
./leahe --help
```

### 2. Run `leahy` Everywhere (Global Access)

To make `leahy`, `leahe`, and `mood` available anywhere in your terminal:

```bash
./leahe install-cli
```

This creates symlinks in `~/.local/bin/`. Since `~/.local/bin` is in standard Linux `$PATH`, you can immediately open any terminal in any directory and type:

```bash
leahy note "Morning reflection"
leahy stats
leahy to-yaml
```

Alternatively, install in editable mode with pip:

```bash
pip install -e .
```

---

## Command Reference

| Command | Description |
|---|---|
| `leahy` / `leahe` | Interactive main menu (check-in, notes, stats, history, YAML converter). |
| `leahy note [title]` | Write a reflection note stored in `~/Notes` as Markdown with YAML frontmatter. |
| `leahy note --edit` | Open `$EDITOR` with a pre-filled Markdown/YAML template. |
| `leahy notes` | List all Markdown notes saved in `~/Notes`. |
| `leahy to-yaml [path]` | Convert Markdown notes from `~/Notes` (or folder) to structured YAML. |
| `leahy to-yaml --single -o out.yaml` | Merge all notes in `~/Notes` into a single consolidated YAML file. |
| `leahy to-md <file.yaml>` | Convert a YAML file back to a Markdown note with frontmatter. |
| `leahy sync` | Bidirectional sync between `~/Notes` and the SQLite database. |
| `leahy predict [name] [-p %] [-d %]` | Log an activity to Pleasure Prediction Sheet (expected pleasure & difficulty). |
| `leahy complete [id] [-p %] [-d %]` | Record actual pleasure & difficulty experienced to bust cognitive dread. |
| `leahy tasks` | View Pleasure Predicting & Anti-Procrastination Sheet with shift analysis. |
| `leahy notify` | Trigger a smart desktop notification / practice reminder via notify-send. |
| `leahy systemd install` | Install & enable automated systemd user timer for practice reminders. |
| `leahy systemd status` | Inspect status of systemd reminder timer. |
| `leahy systemd uninstall` | Disable and remove systemd user reminder timer. |
| `leahy experiment new [title]` | Create a new Behavioral Fear Experiment (aliases: `exp`, `test-fear`). |
| `leahy experiment complete [id]` | Record reality outcome and calculate fear prediction error. |
| `leahy experiment list [--all]` | View Behavioral Experiments Lab & empirical disconfirmation stats. |
| `leahy ladder new [theme]` | Create a new Exposure Hierarchy / Fear Ladder (alias: `exposure`). |
| `leahy ladder add-step <id> <desc>` | Add a graded challenge step with target SUDS (0-100) to a ladder. |
| `leahy ladder practice [step_id]` | Log an exposure practice trial to track anxiety habituation. |
| `leahy ladder list` / `show <id>` | Inspect fear ladders, hierarchy steps, and habituation progress. |
| `leahy decatastrophize` / `decat` | Run a 4-step Decatastrophizing mini-session (Worst/Best/Likely/Coping). |
| `leahy sos` | Acute distress first-aid session (Breathing + 5-4-3-2-1 Grounding). |
| `leahy breathe [--relax] [-c N]` | Interactive Box Breathing (4-4-4-4) or 4-7-8 relaxation breath pacing. |
| `leahy ground` | 5-4-3-2-1 Sensory Grounding protocol for acute panic and overwhelm. |
| `leahy win [text]` / `credit` | Record an achievement or positive evidence in Positive Data Log. |
| `leahy check` | Interactive check-in launcher (choose quick or full CBT). |
| `leahy check --quick` | Direct launch of Quick Mood Check-in. |
| `leahy check --cbt` | Direct launch of Guided CBT Thought Record session. |
| `leahy 3col [thought]` | Rapid David Burns 3-Column Thought Buster. |
| `leahy challenge` | David Burns Belief-Testing Laboratory (challenge specific beliefs/rules). |
| `leahy stats` | Display detailed analytics, CBT efficacy, and ASCII charts. |
| `leahy verify` | Run clinical pattern verification audit. |
| `leahy history` | Browse previous check-ins and CBT records in tabular format. |
| `leahy show <id>` | Inspect full CBT examination details for a specific entry. |
| `leahy export -f yaml -o out.yaml` | Export full record history to structured YAML. |
| `leahy export -f md -o out.md` | Export full record history to formatted Markdown. |
| `leahy export -f json -o out.json` | Export full record history to JSON. |
| `leahy delete <id>` | Delete a specific record. |
| `leahy install-cli` | Link `leahy`, `leahe`, `mood` into `~/.local/bin` for system-wide access. |
| `leahy seed-demo --count 10` | Populate database with sample realistic CBT records for testing. |

---

## Notes Storage Format (`~/Notes`)

Every check-in, CBT thought record, and note is stored as a standard `.md` file in `~/Notes/` (or `LEAHE_NOTES_DIR`):

```markdown
---
id: 1
timestamp: '2026-11-17T20:00:00'
type: cbt_record
initial_mood: 3
final_mood: 7
mood_shift: 4
primary_emotion: Anxious
emotion_intensity_initial: 80
relief_percent: 55
energy_level: 6
situation: Code review feedback
distortions:
  - all_or_nothing
  - catastrophizing
technique: double_standard
tags:
  - work
---

# Code review feedback

- **Date:** 2026-11-17 20:00
- **Initial Mood:** 3/10
- **Final Mood:** 7/10 (Shift: +4)

## Automatic Negative Thought (NAT)
> "I made mistakes so I am terrible at this" (Belief: 85%)

## Cognitive Distortions Identified
- **All-or-Nothing Thinking**: Viewing situations in extreme black-and-white terms.
- **Catastrophizing**: Exaggerating problems or shrinking positive traits.

## Evidence Against
Fixed the edge cases in 20 minutes, review was approved, and the team appreciated the tests.

## Rational Alternative Thought / Reframe
> "Bugs are normal and finding them makes the system robust." (Belief: 90%)

## Action Step
- [ ] Add 2 unit tests for edge cases tomorrow morning.
```

Because files contain clean YAML frontmatter between `---`, they are directly ready for:
- **Obsidian / Logseq / Foam**: Tags, metadata, and links are parsed natively.
- **`leahy to-yaml`**: Convert to pure YAML files whenever you want to move or process data.
- **Static site generators**: Jekyll, Hugo, Astro, etc.

### Filter Options for `leahe history`

- `--limit / -n <int>`: Number of records to display (default: 20).
- `--cbt-only`: Filter only full CBT thought records.
- `--quick-only`: Filter only quick check-ins.
- `--distortion / -d <code>`: Filter by distortion code (e.g. `catastrophizing`).
- `--min-mood <int>`: Filter by minimum initial mood score (1-10).
- `--max-mood <int>`: Filter by maximum initial mood score (1-10).
- `--query / -q <text>`: Search keywords in situations, thoughts, or reframes.

---

## Cognitive Distortions Catalog

The tool identifies 11 clinically validated cognitive distortions:

1. **All-or-Nothing Thinking** (`all_or_nothing`): Viewing situations in extreme black-and-white terms.
2. **Overgeneralization** (`overgeneralization`): Viewing a single negative event as an endless pattern of defeat.
3. **Mental Filter** (`mental_filter`): Dwelling solely on a single negative detail while ignoring positives.
4. **Disqualifying the Positive** (`disqualifying_positive`): Rejecting positive experiences by insisting they don't count.
5. **Mind Reading** (`jumping_mind_reading`): Assuming you know others are judging you negatively without proof.
6. **Fortune Telling** (`jumping_fortune_telling`): Arbitrarily predicting worst-case scenarios as foregone conclusions.
7. **Catastrophizing** (`catastrophizing`): Exaggerating problems or shrinking positive traits.
8. **Emotional Reasoning** (`emotional_reasoning`): Assuming that because you feel bad, external reality must be bad.
9. **'Should' & 'Must' Statements** (`should_statements`): Rigid, punishing rules about how you or others ought to act.
10. **Labeling and Mislabeling** (`labeling`): Attaching a global derogatory label to yourself or others instead of describing errors.
11. **Personalization and Blame** (`personalization`): Holding yourself solely responsible for events outside your control.

---

## David Burns' Belief-Testing Methods (TEAM-CBT)

Integrated methods based on Dr. David Burns (*Feeling Good*, *Feeling Great*):

1. **The Double-Standard Technique** (`double_standard`): Speak to yourself with the same realism and compassion you would offer a dear friend.
2. **Cost-Benefit Analysis** (`cost_benefit`): Weigh the perceived advantages against the severe emotional and practical costs of holding onto a belief.
3. **The Downward / Vertical Arrow Technique** (`downward_arrow`): Repeatedly ask "If that were true, what would it mean to me?" to uncover core schemas and silent assumptions.
4. **Thinking in Shades of Grey** (`shades_of_grey`): Plot performance and events on a 0-100% continuum rather than evaluating in binary black-or-white terms.
5. **The Semantic Method** (`semantic_method`): Transform rigid "shoulds", "musts", and "have tos" into preferences ("I would prefer to", "It is desirable to").
6. **Define Terms** (`define_terms`): Demand precise operational definitions for derogatory labels ("loser", "failure") to expose their logical impossibility.
7. **Reattribution / Responsibility Pie Chart** (`reattribution`): Brainstorm all contributing external and internal factors to distribute responsibility realistically.
8. **The Experimental Technique** (`experimental_technique`): Frame negative assumptions as scientific hypotheses and design empirical behavioral tests.
9. **The 'What-If' Technique (Decatastrophizing)** (`what_if_decatastrophize`): Systematically follow a worst-case fear to its conclusion and devise a concrete coping protocol.
10. **Positive Reframing** (`positive_reframing`): Identify the positive values, integrity, and noble intentions reflected in negative emotions.

---

## Data Storage

By default, entries are stored in a local SQLite database:

- Path: `~/.local/share/leahe/leahe.db` (with automatic fallback to `./data/leahe.db` if the home directory is read-only).
- Override with the `--db <path>` flag or by setting the `LEAHE_DB` environment variable:
  ```bash
  export LEAHE_DB="/path/to/my_leahe.db"
  ```

---

## Running Tests

Run the test suite using `pytest`:

```bash
pytest
```
# leahy
