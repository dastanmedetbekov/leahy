# Leahe

A terminal utility for mood tracking and cognitive restructuring powered by Cognitive Behavioral Therapy (CBT) principles. Designed with zero emojis, clean ASCII typography, and detailed statistical analytics.

---

## Features

- **Strictly No Emojis**: Clean, professional terminal interface utilizing ASCII indicators (`[*]`, `[+]`, `[-]`, `[!]`, `[x]`, `[o]`, `#`, `|`).
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

## Installation & Quick Start

### 1. Direct Execution

The repository is self-contained. You can run the executable script directly from the project directory:

```bash
./leahe --help
```

Or via Python:

```bash
python3 main.py --help
```

*(Note: `./mood` is also maintained as an alias).*

### 2. Optional: Install via Pip

To install into your user environment or virtual environment:

```bash
pip install -e .
```

After installation, the `leahe` command is available system-wide in your terminal.

---

## Command Reference

| Command | Description |
|---|---|
| `./leahe` | Interactive main menu (check-in, stats, history, guide). |
| `./leahe check` | Interactive check-in launcher (choose quick or full CBT). |
| `./leahe check --quick` | Direct launch of Quick Mood Check-in. |
| `./leahe check --cbt` | Direct launch of Guided CBT Thought Record session. |
| `./leahe challenge` | David Burns Belief-Testing Laboratory (challenge specific beliefs/rules). |
| `./leahe stats` | Display detailed analytics, CBT efficacy, and ASCII charts. |
| `./leahe verify` | Run clinical pattern verification audit. |
| `./leahe history` | Browse previous check-ins and CBT records in tabular format. |
| `./leahe show <id>` | Inspect full CBT examination details for a specific entry. |
| `./leahe distortions` | Browse the complete Cognitive Distortions Reference Guide. |
| `./leahe methods` | Browse David Burns' 10 Cognitive Restructuring Methods Guide. |
| `./leahe export -f md -o out.md` | Export records to formatted Markdown. |
| `./leahe export -f json -o out.json` | Export records to JSON. |
| `./leahe delete <id>` | Delete a specific record. |
| `./leahe seed-demo --count 10` | Populate database with sample realistic CBT records for demo/testing. |

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
