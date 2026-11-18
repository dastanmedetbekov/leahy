"""Interactive guided CBT sessions and quick mood check-ins.

Strictly NO emojis. Clean ASCII prompts.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich import box

from .models import (
    MoodEntry,
    ActionItem,
    AntiProcrastinationTask,
    DASAssessment,
    BehavioralExperiment,
    ExposureStep,
    ExposureLadder,
)
from .database import Database
from .cbt_data import COGNITIVE_DISTORTIONS, STANDARD_EMOTIONS, SOCRATIC_QUESTIONS
from .burns_methods import BURNS_METHODS, BurnsMethod
from .das import DAS_QUESTIONS, DOMAIN_ANTIDOTES
from .quality_check import evaluate_rational_response
from .views import print_header, format_mood_badge, format_delta_badge

console = Console()

def ask_int_in_range(prompt_text: str, min_val: int, max_val: int, default: Optional[int] = None) -> int:
    default_str = f" [default: {default}]" if default is not None else ""
    while True:
        try:
            val_str = Prompt.ask(f"[bold cyan]{prompt_text}[/bold cyan] ({min_val}-{max_val}){default_str}").strip()
            if not val_str and default is not None:
                return default
            val = int(val_str)
            if min_val <= val <= max_val:
                return val
            console.print(f"[red][!] Please enter an integer between {min_val} and {max_val}.[/red]")
        except ValueError:
            console.print(f"[red][!] Invalid input. Please enter a number between {min_val} and {max_val}.[/red]")

def select_emotion() -> Tuple[str, int]:
    console.print("\n[bold]Select Primary Emotion Category:[/bold]")
    categories = list(STANDARD_EMOTIONS.keys())
    for idx, cat in enumerate(categories, 1):
        sample = ", ".join(STANDARD_EMOTIONS[cat][:3])
        console.print(f"  [{idx}] {cat} [dim]({sample}...)[/dim]")
    console.print(f"  [{len(categories) + 1}] Other / Custom Emotion")

    cat_choice = ask_int_in_range("Choose emotion category", 1, len(categories) + 1, default=1)

    if cat_choice <= len(categories):
        chosen_cat = categories[cat_choice - 1]
        options = STANDARD_EMOTIONS[chosen_cat]
        console.print(f"\n[bold]Select Specific Emotion from '{chosen_cat}':[/bold]")
        for idx, emo in enumerate(options, 1):
            console.print(f"  [{idx}] {emo}")
        console.print(f"  [{len(options) + 1}] Custom specific emotion")

        emo_choice = ask_int_in_range("Select specific emotion", 1, len(options) + 1, default=1)
        if emo_choice <= len(options):
            emotion_name = options[emo_choice - 1]
        else:
            emotion_name = Prompt.ask("[bold cyan]Enter custom emotion name[/bold cyan]").strip() or "Upset"
    else:
        emotion_name = Prompt.ask("[bold cyan]Enter emotion name[/bold cyan]").strip() or "Neutral"

    intensity = ask_int_in_range(f"Rate intensity of '{emotion_name}' (0% = negligible, 100% = overwhelming)", 0, 100, default=60)
    return emotion_name, intensity

def select_distortions() -> List[str]:
    console.print("\n[bold cyan]=== IDENTIFY COGNITIVE DISTORTIONS ===[/bold cyan]")
    console.print("[dim]I will ask you about each cognitive distortion one by one. Answer yes (y) or no (n).[/dim]\n")

    dist_keys = list(COGNITIVE_DISTORTIONS.keys())
    selected = []

    for key in dist_keys:
        d = COGNITIVE_DISTORTIONS[key]
        console.print(f"[bold magenta]{d.name}[/bold magenta]")
        console.print(f"  [dim]{d.description}[/dim]")
        console.print(f"  [dim]Example: {d.example}[/dim]")
        answer = Prompt.ask(
            f"  [bold cyan]Do you notice this pattern in your thought?[/bold cyan] [dim](y/n)[/dim]",
            default="n",
        ).strip().lower()
        if answer in ("y", "yes"):
            selected.append(key)
            console.print(f"  [green][+] Noted: {d.name}[/green]\n")
        else:
            console.print(f"  [dim][-] Skipped.[/dim]\n")

    if selected:
        console.print("[bold green][+] Identified Distortions:[/bold green]")
        for code in selected:
            console.print(f"    [*] [magenta]{COGNITIVE_DISTORTIONS[code].name}[/magenta]")
    else:
        console.print("[dim]No distortions identified.[/dim]")

    return selected

def prompt_evidence_against(auto_thought: str, distortions: List[str], db: Optional[Database] = None) -> str:
    """Prompt for contradictory evidence with interactive Socratic scaffolding if stuck."""
    console.print("\n[dim]Prompt B: What objective facts contradict or weaken this thought? (What would you tell a friend? Type '?' for Socratic hints)[/dim]")
    val = Prompt.ask("[bold]Evidence Against the Thought[/bold]").strip()

    while not val or val.lower() in ("?", "help", "hint"):
        console.print("\n[bold yellow][*] Socratic Reflection Scaffolding (Clinical Angles):[/bold yellow]")
        console.print("  [1] Friend Lens: What compassionate, realistic facts would you tell a friend with this thought?")
        console.print("  [2] Past Experience: What actually happened the last time you feared this outcome?")
        console.print("  [3] Alternative Explanations: What are 2-3 other plausible, mundane reasons for this situation?")
        console.print("  [4] Coping Capacity: Even if the worst occurred, how would you realistically endure and cope?")

        if db:
            try:
                past = db.list_entries(limit=5, entry_type="cbt_record")
                matching = [p for p in past if p.alternative_thought and (set(p.distortions) & set(distortions))]
                if matching:
                    console.print(f"\n  [dim]Relevant reframe from your past records:[/dim]")
                    console.print(f"  [green]  \"{matching[0].alternative_thought}\"[/green]")
            except Exception:
                pass

        console.print()
        lens = Prompt.ask("[bold cyan]Select an angle (1-4) or enter your evidence directly[/bold cyan]").strip()
        if lens == "1":
            ans = Prompt.ask("[bold cyan]What advice or perspective would you offer your friend?[/bold cyan]").strip()
            if ans:
                return f"Friend advice: {ans}"
        elif lens == "2":
            ans = Prompt.ask("[bold cyan]How did reality turn out in past similar instances?[/bold cyan]").strip()
            if ans:
                return f"Past experience: {ans}"
        elif lens == "3":
            ans = Prompt.ask("[bold cyan]What alternative explanations exist?[/bold cyan]").strip()
            if ans:
                return f"Alternative explanations: {ans}"
        elif lens == "4":
            ans = Prompt.ask("[bold cyan]How would you cope if the worst happened?[/bold cyan]").strip()
            if ans:
                return f"Coping capacity: {ans}"
        elif lens:
            return lens
        else:
            console.print("[red][!] Please enter contradictory evidence, or select 1-4.[/red]")
            val = Prompt.ask("[bold]Evidence Against the Thought[/bold]").strip()
            if val:
                return val

    return val

def prompt_balanced_reframe(auto_thought: str, evidence_against: str, distortions: List[str]) -> str:
    """Prompt for balanced reframe with structured template formula if requested."""
    console.print("\n[bold cyan]STEP 6: RATIONAL & BALANCED ALTERNATIVE THOUGHT[/bold cyan]")
    console.print("[dim]Synthesize the evidence into a balanced, realistic, compassionate perspective (type '?' for formula).[/dim]")
    val = Prompt.ask("[bold]Balanced Alternative Thought[/bold]").strip()

    while not val or val.lower() in ("?", "help", "hint"):
        console.print("\n[bold yellow][*] Reframe Formulation Formula (Burns / Beck):[/bold yellow]")
        console.print("  [cyan]Formula:[/cyan] [dim]\"Even though [trigger/fact], the reality is [contradictory evidence], so I can [constructive stance].\"[/dim]")
        console.print("  [cyan]Example:[/cyan] [dim]\"Even though I made a mistake, one error does not define my ability, and I can fix it calmly.\"[/dim]\n")

        suggested = f"Even though this situation is challenging, the facts show that {evidence_against[:60]}, and I can handle this step-by-step."
        console.print(f"[dim]Suggested starter:[/dim] [green]\"{suggested}\"[/green]\n")

        val = Prompt.ask("[bold]Balanced Alternative Thought[/bold]", default=suggested).strip()
        if val:
            return val

    return val

def execute_burns_technique(method_code: str, thought: str) -> Tuple[str, str, str, dict]:
    """Interactively walks the user through a specific David Burns technique.
    Returns: (evidence_for, evidence_against, alternative_reframe, technique_details)
    """
    method = BURNS_METHODS.get(method_code)
    if not method:
        method = BURNS_METHODS["double_standard"]

    console.print(f"\n[bold magenta]=== DAVID BURNS TECHNIQUE: {method.name.upper()} ===[/bold magenta]")
    console.print(f"[dim]{method.summary}[/dim]\n")
    console.print(f"[cyan]When to use:[/cyan] {method.when_to_use}\n")

    details = {"method_code": method.code, "method_name": method.name, "steps": []}

    if method.code == "double_standard":
        console.print("[dim]Step 1: Imagine a dear friend or respected colleague came to you having this exact thought:[/dim]")
        console.print(f"  [bold]\"{thought}\"[/bold]\n")
        friend_response = Prompt.ask("[bold cyan]What would you say to support, comfort, and realistically guide your friend?[/bold cyan]").strip()
        while not friend_response:
            friend_response = Prompt.ask("[bold cyan]What advice or perspective would you offer them?[/bold cyan]").strip()

        double_std_reason = Prompt.ask("\n[bold cyan]Why do you apply a punitive standard to yourself that you would never apply to your friend?[/bold cyan]").strip()
        reframe = Prompt.ask("\n[bold cyan]Now formulate that same compassionate advice directly to yourself[/bold cyan]", default=friend_response).strip()

        ev_for = "Self-critical automatic standards."
        ev_against = f"Friend advice: {friend_response}. Double-standard reason acknowledged: {double_std_reason}."
        details["steps"] = [
            {"prompt": "Friend Advice", "response": friend_response},
            {"prompt": "Why Double Standard", "response": double_std_reason},
            {"prompt": "Self-Compassionate Reframe", "response": reframe},
        ]
        return ev_for, ev_against, reframe, details

    elif method.code == "cost_benefit":
        console.print("[dim]List the concrete advantages and disadvantages of holding onto this thought/belief:[/dim]\n")
        advantages = Prompt.ask("[bold cyan]What are the advantages of believing this? (How do you think it protects or motivates you?)[/bold cyan]").strip() or "Keeps me cautious."
        disadvantages = Prompt.ask("[bold cyan]What are the real costs and disadvantages? (Stress, anxiety, burnout, self-doubt?)[/bold cyan]").strip()
        while not disadvantages:
            disadvantages = Prompt.ask("[bold cyan]Please list at least one major cost or disadvantage[/bold cyan]").strip()

        cost_balance = Prompt.ask("\n[bold cyan]Looking at both sides, what is a more cost-effective, healthy alternative thought?[/bold cyan]").strip()
        while not cost_balance:
            cost_balance = Prompt.ask("[bold cyan]Please formulate a balanced belief that gives benefits without the heavy costs[/bold cyan]").strip()

        ev_for = f"Perceived advantages: {advantages}"
        ev_against = f"Costs & disadvantages: {disadvantages}"
        details["steps"] = [
            {"prompt": "Advantages", "response": advantages},
            {"prompt": "Disadvantages", "response": disadvantages},
            {"prompt": "Cost-Effective Reframe", "response": cost_balance},
        ]
        return ev_for, ev_against, cost_balance, details

    elif method.code == "downward_arrow":
        console.print("[dim]Let's peel back the layers to discover the silent core assumption driving this thought:[/dim]\n")
        step1 = Prompt.ask("[bold cyan]Layer 1: If this thought were true, what would that mean to you? Why would that be upsetting?[/bold cyan]").strip()
        step2 = Prompt.ask("\n[bold cyan]Layer 2: And if that were true, what does that say about your worth or future?[/bold cyan]").strip()
        core_belief = Prompt.ask("\n[bold cyan]Core Rule: What silent rule ('I must always...', 'I am only worthy if...') is driving this?[/bold cyan]").strip()
        reframe = Prompt.ask("\n[bold cyan]How can you challenge and rewrite this silent rule with realistic human compassion?[/bold cyan]").strip()

        ev_for = f"Underlying feared chain: {step1} -> {step2}"
        ev_against = f"Core silent rule identified and challenged: {core_belief}"
        details["steps"] = [
            {"prompt": "Layer 1 Meaning", "response": step1},
            {"prompt": "Layer 2 Consequence", "response": step2},
            {"prompt": "Underlying Silent Assumption", "response": core_belief},
            {"prompt": "Challenged Core Reframe", "response": reframe},
        ]
        return ev_for, ev_against, reframe, details

    elif method.code == "shades_of_grey":
        console.print("[dim]Let's examine this on a 0-100 continuum rather than all-or-nothing black-and-white:[/dim]\n")
        zero_desc = Prompt.ask("[bold cyan]What would absolute zero (0% - total worst imaginable failure) look like?[/bold cyan]").strip() or "Complete non-attendance or catastrophe."
        hundred_desc = Prompt.ask("[bold cyan]What would 100% (superhuman perfection) look like?[/bold cyan]").strip() or "Flawless perfection."
        actual_score = ask_int_in_range("Where does reality realistically land on this 0-100 scale?", 0, 100, default=70)
        reframe = Prompt.ask("\n[bold cyan]Balanced reframe reflecting this continuum score[/bold cyan]").strip()

        ev_for = f"Binary expectation vs perfection (100%): {hundred_desc}"
        ev_against = f"Realistic continuum score: {actual_score}/100. Far above absolute zero (0%: {zero_desc})."
        details["steps"] = [
            {"prompt": "Absolute Zero (0%) Definition", "response": zero_desc},
            {"prompt": "Perfection (100%) Definition", "response": hundred_desc},
            {"prompt": "Actual Continuum Score", "response": f"{actual_score}/100"},
            {"prompt": "Continuum Reframe", "response": reframe},
        ]
        return ev_for, ev_against, reframe, details

    elif method.code == "semantic_method":
        console.print("[dim]Replace rigid 'should', 'must', or 'have to' with preferences and personal agency:[/dim]\n")
        should_part = Prompt.ask("[bold cyan]Identify the rigid 'should' or 'must' in your thought[/bold cyan]").strip()
        reframe = Prompt.ask("\n[bold cyan]Rewrite replacing 'I should' with 'I would prefer to', 'I want to', or 'It is desirable to'[/bold cyan]").strip()
        while not reframe:
            reframe = Prompt.ask("[bold cyan]Please formulate the preference-based statement[/bold cyan]").strip()

        ev_for = f"Rigid rule: {should_part}"
        ev_against = "Rigid imperatives cause needless guilt. Humans have limitations and preferences, not unbending laws."
        details["steps"] = [
            {"prompt": "Rigid Rule", "response": should_part},
            {"prompt": "Preference-Based Semantic Reframe", "response": reframe},
        ]
        return ev_for, ev_against, reframe, details

    elif method.code == "define_terms":
        console.print("[dim]Define the derogatory label under rigorous operational scrutiny:[/dim]\n")
        label = Prompt.ask("[bold cyan]What derogatory label are you using (e.g. 'loser', 'failure', 'incompetent', 'fool')?[/bold cyan]").strip()
        definition = Prompt.ask(f"\n[bold cyan]How would a dictionary rigorously define a '{label}'?[/bold cyan]").strip()
        reframe = Prompt.ask("\n[bold cyan]Describe the specific human behavior without applying that false absolute label[/bold cyan]").strip()

        ev_for = f"Applied label: '{label}'"
        ev_against = f"Definition '{definition}' cannot describe a complete, living human being with diverse actions."
        details["steps"] = [
            {"prompt": "Derogatory Label", "response": label},
            {"prompt": "Strict Definition", "response": definition},
            {"prompt": "Behavior-Specific Reframe", "response": reframe},
        ]
        return ev_for, ev_against, reframe, details

    elif method.code == "reattribution":
        console.print("[dim]Break down the responsibility pie chart across all contributing factors:[/dim]\n")
        factors = Prompt.ask("[bold cyan]List other contributing factors (environment, other people, timing, lack of info, luck)[/bold cyan]").strip()
        my_share = ask_int_in_range("What percentage of the outcome was realistically your personal responsibility?", 0, 100, default=25)
        reframe = Prompt.ask(f"\n[bold cyan]Balanced reframe taking responsibility for your {my_share}% without carrying the rest[/bold cyan]").strip()

        ev_for = f"My personal involvement estimated at {my_share}%."
        ev_against = f"External factors ({100 - my_share}% of outcome): {factors}."
        details["steps"] = [
            {"prompt": "External Contributing Factors", "response": factors},
            {"prompt": "Realistic Personal Responsibility", "response": f"{my_share}%"},
            {"prompt": "Reattribution Reframe", "response": reframe},
        ]
        return ev_for, ev_against, reframe, details

    elif method.code == "experimental_technique":
        console.print("[dim]Formulate your negative thought as a testable scientific hypothesis:[/dim]\n")
        hypothesis = Prompt.ask("[bold cyan]Scientific Hypothesis: 'If I do X, then catastrophic Y will happen'[/bold cyan]", default=thought).strip()
        experiment = Prompt.ask("\n[bold cyan]What simple, safe behavioral experiment can you run to test this in reality?[/bold cyan]").strip()
        reframe = Prompt.ask("\n[bold cyan]What is an open-minded, empirical stance to take while testing this?[/bold cyan]").strip()

        ev_for = f"Feared hypothesis: {hypothesis}"
        ev_against = f"Planned empirical experiment: {experiment}. A hypothesis is not fact until tested."
        details["steps"] = [
            {"prompt": "Testable Hypothesis", "response": hypothesis},
            {"prompt": "Experimental Design", "response": experiment},
            {"prompt": "Empirical Reframe", "response": reframe},
        ]
        return ev_for, ev_against, reframe, details

    elif method.code == "what_if_decatastrophize":
        console.print("[dim]Systematically face the worst-case scenario and build a concrete coping protocol:[/dim]\n")
        worst_case = Prompt.ask("[bold cyan]What is the absolute realistic worst-case scenario you fear?[/bold cyan]").strip()
        coping_actions = Prompt.ask("\n[bold cyan]If that worst-case happened, what concrete steps would you take in the first 48 hours to cope?[/bold cyan]").strip()
        reframe = Prompt.ask("\n[bold cyan]Balanced reframe (Worst case probability + your coping ability)[/bold cyan]").strip()

        ev_for = f"Feared scenario: {worst_case}"
        ev_against = f"Concrete coping plan: {coping_actions}. I have resources to endure and adapt."
        details["steps"] = [
            {"prompt": "Worst-Case Scenario", "response": worst_case},
            {"prompt": "Concrete 48-Hour Coping Plan", "response": coping_actions},
            {"prompt": "Decatastrophized Reframe", "response": reframe},
        ]
        return ev_for, ev_against, reframe, details

    elif method.code == "positive_reframing":
        console.print("[dim]Discover the core virtues, deep caring, and values hidden inside this negative reaction:[/dim]\n")
        caring_value = Prompt.ask("[bold cyan]What does this reaction show that you deeply care about? (e.g. excellence, fairness, relationships, integrity)[/bold cyan]").strip()
        reframe = Prompt.ask("\n[bold cyan]How can you honor and keep 100% of this positive value while letting go of the crippling self-torment?[/bold cyan]").strip()

        ev_for = f"Honorable core value: {caring_value}"
        ev_against = "Suffering and cognitive distortions are not required to maintain high standards or caring."
        details["steps"] = [
            {"prompt": "Positive Core Value", "response": caring_value},
            {"prompt": "TEAM-CBT Positive Reframe", "response": reframe},
        ]
        return ev_for, ev_against, reframe, details

    else:
        # Fallback to standard
        ev_for = Prompt.ask("[bold cyan]Evidence Supporting the Thought[/bold cyan]").strip() or "None stated."
        ev_against = Prompt.ask("[bold cyan]Evidence Contradicting the Thought[/bold cyan]").strip() or "Alternative explanations exist."
        reframe = Prompt.ask("[bold cyan]Balanced Alternative Thought[/bold cyan]").strip() or thought
        return ev_for, ev_against, reframe, details

def run_quick_checkin(db: Database) -> MoodEntry:
    print_header("Quick Mood Check-in", subtitle="Brief snapshot of your current emotional state")

    mood = ask_int_in_range("Rate overall mood (1 = very low, 5 = neutral, 10 = great)", 1, 10, default=5)
    emotion, intensity = select_emotion()
    energy = ask_int_in_range("Rate current energy level (1 = exhausted, 10 = fully energized)", 1, 10, default=5)

    situation = Prompt.ask("[bold cyan]Context / Brief note on what you are doing right now (optional)[/bold cyan]").strip()
    raw_tags = Prompt.ask("[bold cyan]Tags (comma-separated, e.g. work, sleep, health) (optional)[/bold cyan]").strip()
    tags = [t.strip().lstrip("#") for t in raw_tags.split(",") if t.strip()]
    notes = Prompt.ask("[bold cyan]Any additional thoughts / notes (optional)[/bold cyan]").strip()

    entry = MoodEntry(
        entry_type="quick",
        initial_mood=mood,
        primary_emotion=emotion,
        emotion_intensity_initial=intensity,
        energy_level=energy,
        situation=situation or None,
        tags=tags,
        notes=notes or None,
    )

    entry_id = db.save_entry(entry)
    console.print(f"\n[bold green][+] Quick check-in saved successfully! (ID: {entry_id})[/bold green]")
    console.print(f"    Mood: {format_mood_badge(mood)} | Emotion: {emotion} ({intensity}%) | Energy: {energy}/10\n")
    return entry

def run_cbt_session(db: Database) -> MoodEntry:
    print_header("CBT Guided Thought Record Session", subtitle="Step-by-step cognitive restructuring protocol")

    # Step 1: The Situation / Trigger
    console.print("\n[bold cyan]STEP 1: SITUATION & CONTEXT[/bold cyan]")
    console.print("[dim]Describe what happened. Stick to objective facts (who, what, where, when).[/dim]")
    situation = Prompt.ask("[bold]Situation / Trigger[/bold]").strip()
    while not situation:
        console.print("[red][!] Situation cannot be empty. What triggered your emotion?[/red]")
        situation = Prompt.ask("[bold]Situation / Trigger[/bold]").strip()

    # Step 2: Emotional State
    console.print("\n[bold cyan]STEP 2: EMOTIONS & INITIAL MOOD[/bold cyan]")
    initial_mood = ask_int_in_range("Rate your overall mood right now (1 = severe distress, 10 = calm/great)", 1, 10, default=4)
    primary_emotion, initial_intensity = select_emotion()
    energy = ask_int_in_range("Energy level (1 = depleted, 10 = high)", 1, 10, default=5)

    # Step 3: Automatic Negative Thought (NAT)
    console.print("\n[bold cyan]STEP 3: AUTOMATIC NEGATIVE THOUGHT (NAT)[/bold cyan]")
    console.print("[dim]What exact sentence or mental image went through your head when you felt that emotion?[/dim]")
    auto_thought = Prompt.ask("[bold]Automatic Thought[/bold]").strip()
    while not auto_thought:
        console.print("[red][!] Please state the specific thought you are having.[/red]")
        auto_thought = Prompt.ask("[bold]Automatic Thought[/bold]").strip()

    belief_initial = ask_int_in_range("How strongly do you believe this automatic thought right now? (0-100%)", 0, 100, default=80)

    # Optional Downward Arrow prompt to uncover root core schema
    core_schema = None
    use_arrow = Prompt.ask("[bold cyan]Apply Downward Arrow technique to uncover root core belief? (y/N)[/bold cyan]", default="n").strip().lower()
    if use_arrow == "y":
        console.print("\n[bold cyan]=== DOWNWARD / VERTICAL ARROW TECHNIQUE ===[/bold cyan]")
        console.print("[dim]Ask: 'If that thought were true, what would that mean to you or about you?'[/dim]")
        step1 = Prompt.ask("[bold]If that were true, why would that be terrible or what would it mean to you?[/bold]").strip()
        step2 = Prompt.ask("[bold]And if that were true, what is the worst part about that?[/bold]").strip()
        step3 = Prompt.ask("[bold]What does this reveal about your core rule/belief about yourself?[/bold]").strip()
        core_schema = step3 or step2 or step1
        if core_schema:
            console.print(f"\n[bold green][+] Core Schema Uncovered:[/bold green] \"{core_schema}\"")
            console.print("[dim]You can test and dismantle this core assumption in the Burns Lab ('leahy challenge').[/dim]\n")

    # Step 4: Identify Distortions
    distortions = select_distortions()

    # Step 5: Socratic Questioning & Evidence Examination / Burns Technique
    console.print("\n[bold cyan]STEP 5: RESTRUCTURING & BELIEF TESTING METHOD[/bold cyan]")
    console.print("[dim]Choose your cognitive restructuring strategy:[/dim]")
    console.print("  [1] Classic Evidence Examination (Facts For vs Facts Against)")
    console.print("  [2] Select a David Burns Belief Testing Technique (Double Standard, Cost-Benefit, etc.)")

    choice_strategy = ask_int_in_range("Select strategy (1 or 2)", 1, 2, default=1)

    technique_used = "classic_evidence"
    technique_details = None

    if choice_strategy == 2:
        console.print("\n[bold]Select David Burns Restructuring Method:[/bold]")
        burns_list = list(BURNS_METHODS.keys())
        for idx, key in enumerate(burns_list, 1):
            m = BURNS_METHODS[key]
            console.print(f"  [{idx:>2}] [bold magenta]{m.name}[/bold magenta] - [dim]{m.summary}[/dim]")

        b_choice = ask_int_in_range("Choose technique", 1, len(burns_list), default=1)
        selected_method_code = burns_list[b_choice - 1]
        technique_used = selected_method_code

        evidence_for, evidence_against, alt_thought_suggested, details_dict = execute_burns_technique(
            selected_method_code, auto_thought
        )
        if core_schema:
            details_dict["core_schema"] = core_schema
        import json
        technique_details = json.dumps(details_dict)

        console.print("\n[bold cyan]STEP 6: RATIONAL & BALANCED ALTERNATIVE THOUGHT[/bold cyan]")
        console.print(f"[dim]Suggested reframe from {BURNS_METHODS[selected_method_code].name}:[/dim]")
        console.print(f"  [green]\"{alt_thought_suggested}\"[/green]\n")
        alt_thought = Prompt.ask("[bold]Confirm or refine balanced thought[/bold]", default=alt_thought_suggested).strip()
    else:
        # Classic Evidence Examination
        if distortions:
            console.print("\n[bold yellow]Targeted CBT Challenge Questions for your identified distortions:[/bold yellow]")
            for d_code in distortions:
                d_info = COGNITIVE_DISTORTIONS.get(d_code)
                if d_info:
                    console.print(f"  [*] [bold magenta]{d_info.name}:[/bold magenta]")
                    for q in d_info.challenge_questions:
                        console.print(f"      - {q}")
            console.print()

        console.print("[dim]Prompt A: What objective, verifiable facts support this thought?[/dim]")
        evidence_for = Prompt.ask("[bold]Evidence Supporting the Thought[/bold]").strip() or "None stated."

        # Evidence validation: check if evidence_for starts with feeling or subjective opinion
        subjective_cues = ("i don't think", "i feel", "i doubt", "i guess", "i believe", "it seems", "i'm not sure")
        if any(evidence_for.lower().startswith(cue) for cue in subjective_cues):
            console.print("\n[yellow][*] Clinical Fact-Check Hint:[/yellow] Evidence must be verifiable, objective facts (like a video camera recording).")
            console.print(f"[dim]    \"{evidence_for}\" sounds like an interpretation or feeling, not a hard observable fact.[/dim]")
            rephrase = Prompt.ask("[bold cyan]Would you like to refine it to an objective fact? (y/N)[/bold cyan]", default="n").strip().lower()
            if rephrase == "y":
                evidence_for = Prompt.ask("[bold]Refined Objective Fact[/bold]").strip() or evidence_for

        evidence_against = prompt_evidence_against(auto_thought, distortions, db=db)
        alt_thought = prompt_balanced_reframe(auto_thought, evidence_against, distortions)


    belief_final = ask_int_in_range("How much do you believe this new, balanced thought? (0-100%)", 0, 100, default=75)

    # Burns Thought Quality Check
    q_report = evaluate_rational_response(auto_thought, alt_thought, belief_final, belief_initial, distortions)
    console.print(f"\n[dim]Burns Thought Quality Audit: [bold]{q_report.rating}[/bold] ({q_report.overall_score}/100)[/dim]")
    for rec in q_report.recommendations:
        console.print(f"  [!] {rec}")

    # Step 7: Outcome & Mood Re-rating
    console.print("\n[bold cyan]STEP 7: OUTCOME & RE-RATING[/bold cyan]")
    console.print("[dim]Re-assess how you feel now after examining the evidence and framing a balanced thought.[/dim]")
    final_mood = ask_int_in_range("Re-rate overall mood (1-10)", 1, 10, default=min(10, initial_mood + 2))
    final_intensity = ask_int_in_range(f"Re-rate intensity of '{primary_emotion}' (0-100%)", 0, 100, default=max(0, initial_intensity - 30))

    # Step 8: Behavioral Activation / Micro-Action & Tags
    console.print("\n[bold cyan]STEP 8: CONSTRUCTIVE ACTION & TAGS (OPTIONAL)[/bold cyan]")
    console.print("[dim]What is one small, concrete step you can take right now to help yourself or address the situation?[/dim]")
    action_plan = Prompt.ask("[bold]Small Constructive Action Step (optional)[/bold]").strip()
    raw_tags = Prompt.ask("[bold]Tags (comma-separated, e.g. work, deadline, sleep) (optional)[/bold]").strip()
    tags = [t.strip().lstrip("#") for t in raw_tags.split(",") if t.strip()]

    # Step 9: Acceptance & Cognitive Defusion (ACT)
    console.print("\n[bold cyan]STEP 9: COGNITIVE DEFUSION (ACT MINDFULNESS)[/bold cyan]")
    console.print(f"  Fused with thought:  [dim]\"{auto_thought}\"[/dim]")
    console.print(f"  Defused observation: [bold green]\"I notice that I am having the thought that: '{auto_thought}'.\"[/bold green]")
    console.print("  [dim]Thoughts are cognitive events passing through awareness, not objective commands or reality.[/dim]\n")

    entry = MoodEntry(
        entry_type="cbt_record",
        initial_mood=initial_mood,
        primary_emotion=primary_emotion,
        emotion_intensity_initial=initial_intensity,
        energy_level=energy,
        situation=situation,
        automatic_thought=auto_thought,
        belief_initial=belief_initial,
        distortions=distortions,
        evidence_for=evidence_for,
        evidence_against=evidence_against,
        alternative_thought=alt_thought,
        belief_final=belief_final,
        final_mood=final_mood,
        emotion_intensity_final=final_intensity,
        action_plan=action_plan or None,
        technique_used=technique_used,
        technique_details=technique_details,
        tags=tags,
        notes=f"Core Schema: {core_schema}" if core_schema else None,
    )

    entry_id = db.save_entry(entry)

    # Show post-session outcome banner
    mood_shift = final_mood - initial_mood
    distress_relief = initial_intensity - final_intensity

    console.print(f"\n[bold green][+] CBT Thought Record #{entry_id} successfully saved![/bold green]\n")

    res_text = Text()
    res_text.append(f"Session Results:\n", style="bold cyan")
    if technique_used and technique_used in BURNS_METHODS:
        res_text.append(f"  Method Used: {BURNS_METHODS[technique_used].name}\n")
    res_text.append(f"  Overall Mood: {initial_mood}/10 -> {final_mood}/10 (Shift: {format_delta_badge(mood_shift)})\n")
    res_text.append(f"  {primary_emotion} Intensity: {initial_intensity}% -> {final_intensity}% (Distress Relief: {format_delta_badge(distress_relief)}%)\n")
    res_text.append(f"  Belief in Balanced Thought: {belief_final}%\n")
    if action_plan:
        res_text.append(f"  Action Plan: {action_plan}\n")

    console.print(Panel(res_text, title="[bold]CBT Session Summary[/bold]", box=box.ROUNDED, border_style="green"))
    return entry

def run_belief_challenge_session(db: Database) -> MoodEntry:
    """Dedicated David Burns Belief-Testing Laboratory."""
    print_header("David Burns Belief-Testing Laboratory", subtitle="Targeted cognitive restructuring to deconstruct irrational beliefs and silent rules")

    console.print("[dim]State the negative automatic thought, self-criticism, or rigid belief you want to test:[/dim]")
    thought = Prompt.ask("[bold cyan]Belief / Thought to Challenge[/bold cyan]").strip()
    while not thought:
        thought = Prompt.ask("[bold cyan]Please state the belief or thought[/bold cyan]").strip()

    belief_initial = ask_int_in_range("How strongly do you believe this thought right now? (0-100%)", 0, 100, default=85)

    situation = Prompt.ask("\n[bold cyan]Context / Situation that triggered this belief (optional)[/bold cyan]").strip()
    primary_emotion, initial_intensity = select_emotion()
    initial_mood = ask_int_in_range("Overall mood right now (1 = distress, 10 = great)", 1, 10, default=4)

    # Optional distortion selection
    console.print("\n[dim]Do you want to identify cognitive distortions in this thought? (optional)[/dim]")
    check_dist = Prompt.ask("Check distortions? (y/n)", default="y").strip().lower()
    distortions = select_distortions() if check_dist in ["y", "yes"] else []

    # Select Burns Technique
    console.print("\n[bold cyan]SELECT DAVID BURNS TESTING METHOD:[/bold cyan]")
    burns_keys = list(BURNS_METHODS.keys())
    for idx, key in enumerate(burns_keys, 1):
        m = BURNS_METHODS[key]
        console.print(f"  [{idx:>2}] [bold magenta]{m.name}[/bold magenta] [dim]({m.category})[/dim]")
        console.print(f"       [dim]{m.summary}[/dim]")

    b_choice = ask_int_in_range("Select Burns method", 1, len(burns_keys), default=1)
    chosen_method_code = burns_keys[b_choice - 1]

    ev_for, ev_against, alt_suggested, details_dict = execute_burns_technique(chosen_method_code, thought)
    import json
    technique_details = json.dumps(details_dict)

    console.print("\n[bold cyan]STEP: RATIONAL ALTERNATIVE / BALANCED THOUGHT[/bold cyan]")
    console.print(f"[dim]Suggested reframe from {BURNS_METHODS[chosen_method_code].name}:[/dim]")
    console.print(f"  [green]\"{alt_suggested}\"[/green]\n")
    alt_thought = Prompt.ask("[bold]Refine or confirm your balanced thought[/bold]", default=alt_suggested).strip()
    belief_final_alt = ask_int_in_range("How strongly do you believe this new, balanced thought? (0-100%)", 0, 100, default=80)

    # Re-rate original thought!
    console.print("\n[bold cyan]RE-EVALUATION & OUTCOME[/bold cyan]")
    belief_after_original = ask_int_in_range(f"Re-rate belief in the ORIGINAL thought: '{thought[:40]}...' (0-100%)", 0, 100, default=max(0, belief_initial - 40))
    final_mood = ask_int_in_range("Re-rate overall mood (1-10)", 1, 10, default=min(10, initial_mood + 3))
    final_intensity = ask_int_in_range(f"Re-rate intensity of '{primary_emotion}' (0-100%)", 0, 100, default=max(0, initial_intensity - 35))

    action_step = Prompt.ask("\n[bold cyan]Constructive micro-action step based on this insight (optional)[/bold cyan]").strip()

    entry = MoodEntry(
        entry_type="cbt_record",
        initial_mood=initial_mood,
        primary_emotion=primary_emotion,
        emotion_intensity_initial=initial_intensity,
        situation=situation or None,
        automatic_thought=thought,
        belief_initial=belief_initial,
        distortions=distortions,
        evidence_for=ev_for,
        evidence_against=ev_against,
        alternative_thought=alt_thought,
        belief_final=belief_final_alt,
        final_mood=final_mood,
        emotion_intensity_final=final_intensity,
        action_plan=action_step or None,
        technique_used=chosen_method_code,
        technique_details=technique_details,
    )

    entry_id = db.save_entry(entry)

    belief_drop = belief_initial - belief_after_original
    mood_shift = final_mood - initial_mood
    distress_relief = initial_intensity - final_intensity

    console.print(f"\n[bold green][+] Belief challenge session #{entry_id} saved successfully![/bold green]\n")

    summary_text = Text()
    summary_text.append(f"Belief Challenge Outcome:\n", style="bold cyan")
    summary_text.append(f"  Method Applied: {BURNS_METHODS[chosen_method_code].name}\n")
    summary_text.append(f"  Belief in Negative Thought: {belief_initial}% -> {belief_after_original}% (Shift: -{belief_drop}%)\n", style="bold yellow")
    summary_text.append(f"  Belief in Balanced Reframe: {belief_final_alt}%\n", style="bold green")
    summary_text.append(f"  Mood Shift: {initial_mood}/10 -> {final_mood}/10 ({format_delta_badge(mood_shift)})\n")
    summary_text.append(f"  {primary_emotion} Intensity Relief: {format_delta_badge(distress_relief)}%\n")
    if action_step:
        summary_text.append(f"  Action Step: {action_step}\n")

    console.print(Panel(summary_text, title="[bold]Burns Belief Test Results[/bold]", box=box.ROUNDED, border_style="green"))
    return entry

def run_3column_technique(db: Database, initial_thought: Optional[str] = None) -> MoodEntry:
    """David Burns' Triple-Column Technique for rapid cognitive restructuring."""
    print_header("Burns 3-Column Thought Buster", subtitle="Automatic Thought | Cognitive Distortions | Rational Response")

    if initial_thought:
        nat = initial_thought.strip()
        console.print(f"[bold cyan]Automatic Negative Thought:[/bold cyan] {nat}")
    else:
        nat = Prompt.ask("[bold cyan]Automatic Negative Thought (NAT)[/bold cyan]").strip()
        while not nat:
            nat = Prompt.ask("[bold cyan]Please enter your automatic thought[/bold cyan]").strip()

    belief_initial = ask_int_in_range("How strongly do you believe this thought right now? (0-100%)", 0, 100, default=80)
    primary_emotion, initial_intensity = select_emotion()
    initial_mood = ask_int_in_range("Overall mood right now (1 = distress, 10 = great)", 1, 10, default=4)

    # Column 2: Cognitive Distortions
    distortions = select_distortions()

    # Column 3: Rational Response
    console.print("\n[bold cyan]COLUMN 3: RATIONAL RESPONSE (REFRAME)[/bold cyan]")
    console.print("[dim]Write an objective, compassionate statement that directly refutes the distortions in Column 2.[/dim]")
    rational_response = Prompt.ask("[bold]Rational Response[/bold]").strip()
    while not rational_response:
        rational_response = Prompt.ask("[bold]Rational Response[/bold]").strip()

    belief_final = ask_int_in_range("How strongly do you believe this rational response? (0-100%)", 0, 100, default=80)

    # Quality Check
    q_report = evaluate_rational_response(nat, rational_response, belief_final, belief_initial, distortions)
    console.print(f"\n[dim]Rational Response Audit: [bold]{q_report.rating}[/bold] ({q_report.overall_score}/100)[/dim]")
    for r in q_report.recommendations:
        console.print(f"  [!] {r}")

    # Re-rate
    belief_after = ask_int_in_range(f"Re-rate belief in the negative thought (0-100%)", 0, 100, default=max(0, belief_initial - 40))
    final_mood = ask_int_in_range("Re-rate overall mood (1-10)", 1, 10, default=min(10, initial_mood + 2))
    final_intensity = ask_int_in_range(f"Re-rate intensity of '{primary_emotion}' (0-100%)", 0, 100, default=max(0, initial_intensity - 30))

    entry = MoodEntry(
        entry_type="cbt_record",
        initial_mood=initial_mood,
        primary_emotion=primary_emotion,
        emotion_intensity_initial=initial_intensity,
        automatic_thought=nat,
        belief_initial=belief_initial,
        distortions=distortions,
        alternative_thought=rational_response,
        belief_final=belief_final,
        final_mood=final_mood,
        emotion_intensity_final=final_intensity,
        technique_used="triple_column",
        notes="3-Column Thought Buster",
    )
    entry_id = db.save_entry(entry)

    # Print 3-column table
    from rich.table import Table
    table = Table(title=f"3-Column Record #{entry_id}", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("1. Automatic Thought (NAT)", style="red", width=28)
    table.add_column("2. Cognitive Distortions", style="magenta", width=26)
    table.add_column("3. Rational Response", style="green", width=34)

    dist_names = [COGNITIVE_DISTORTIONS[d].name for d in distortions if d in COGNITIVE_DISTORTIONS]
    dist_str = "\n".join(f"[*] {name}" for name in dist_names) if dist_names else "None identified"

    table.add_row(
        f"\"{nat}\"\n(Belief: {belief_initial}% -> {belief_after}%)",
        dist_str,
        f"\"{rational_response}\"\n(Belief: {belief_final}%)",
    )
    console.print()
    console.print(table)
    console.print(f"[green][+] Saved successfully! Mood: {initial_mood}/10 -> {final_mood}/10 ({format_delta_badge(final_mood - initial_mood)})[/green]\n")
    return entry

def run_das_assessment(db: Database) -> DASAssessment:
    """Burns' Dysfunctional Attitude Scale (DAS) questionnaire."""
    print_header("Burns' Dysfunctional Attitude Scale (DAS)", subtitle="Identify deep-seated silent assumptions and psychological vulnerabilities")

    console.print("[dim]Rate each statement from 1 (Strongly Disagree) to 7 (Strongly Agree).[/dim]")
    console.print("[dim]1 = Strongly Disagree | 4 = Neutral / Unsure | 7 = Strongly Agree[/dim]\n")

    scores_by_domain: Dict[str, List[int]] = {}
    answers = {}

    for q in DAS_QUESTIONS:
        console.print(f"[bold cyan]Item {q.id}/10:[/bold cyan] \"{q.text}\"")
        score = ask_int_in_range("Your rating (1-7)", 1, 7, default=4)
        answers[str(q.id)] = score
        if q.domain not in scores_by_domain:
            scores_by_domain[q.domain] = []
        scores_by_domain[q.domain].append(score)
        console.print()

    total_score = sum(answers.values())

    # Calculate average per domain
    domain_averages = []
    for dom, score_list in scores_by_domain.items():
        avg = sum(score_list) / len(score_list)
        domain_averages.append((dom, avg))

    domain_averages.sort(key=lambda x: x[1], reverse=True)
    top_vulns = [d[0] for d in domain_averages if d[1] >= 4.5]
    if not top_vulns and domain_averages:
        top_vulns = [domain_averages[0][0]]

    import json
    assessment = DASAssessment(
        scores_json=json.dumps(answers),
        total_score=total_score,
        top_vulnerabilities=", ".join(top_vulns),
        notes=f"Top: {', '.join(top_vulns)}",
    )
    db.save_das(assessment)

    # Display Results
    from rich.table import Table
    table = Table(title="DAS Psychological Vulnerability Profile", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Vulnerability Domain", width=34)
    table.add_column("Avg Score (1-7)", justify="center", width=16)
    table.add_column("Vulnerability Level", justify="center", width=22)

    for dom, avg in domain_averages:
        if avg >= 5.5:
            level_str = "[bold red]HIGH VULNERABILITY[/bold red]"
        elif avg >= 4.0:
            level_str = "[bold yellow]MODERATE RISK[/bold yellow]"
        else:
            level_str = "[bold green]HEALTHY / RESILIENT[/bold green]"
        table.add_row(dom, f"{avg:.1f}/7", level_str)

    console.print(table)

    # Print Antidotes for top vulnerabilities
    console.print("\n[bold cyan]=== DAVID BURNS' CLINICAL ANTIDOTES FOR YOUR PROFILE ===[/bold cyan]")
    for v in top_vulns[:2]:
        antidote = DOMAIN_ANTIDOTES.get(v, "Challenge rigid assumptions with Socratic questioning.")
        console.print(Panel(antidote, title=f"[bold]{v}[/bold]", box=box.ROUNDED, border_style="yellow"))

    return assessment

def run_anti_procrastination_predict(
    db: Database,
    task_name: Optional[str] = None,
    predicted_pleasure: Optional[int] = None,
    predicted_difficulty: Optional[int] = None,
    notes: Optional[str] = None,
) -> AntiProcrastinationTask:
    """Add task to Burns Anti-Procrastination & Pleasure-Predicting Sheet."""
    if not task_name:
        print_header("Burns Anti-Procrastination Sheet", subtitle="Step 1: Predict task difficulty and pleasure before starting")
        task_name = Prompt.ask("[bold cyan]Task Name / Activity to Tackle[/bold cyan]").strip()
        while not task_name:
            task_name = Prompt.ask("[bold cyan]Please enter a task name[/bold cyan]").strip()

    if predicted_difficulty is None:
        console.print("\n[dim]Before starting, people with anxiety or depression grossly overestimate difficulty and underestimate pleasure.[/dim]")
        pred_diff = ask_int_in_range("Predict difficulty (0% = effortless, 100% = excruciatingly hard)", 0, 100, default=70)
    else:
        pred_diff = max(0, min(100, predicted_difficulty))

    if predicted_pleasure is None:
        pred_pleas = ask_int_in_range("Predict satisfaction / pleasure (0% = zero joy, 100% = deeply rewarding)", 0, 100, default=20)
    else:
        pred_pleas = max(0, min(100, predicted_pleasure))

    if notes is None and not (task_name and predicted_pleasure is not None):
        notes_input = Prompt.ask("\n[bold cyan]Notes / Subtasks to do first (optional)[/bold cyan]").strip()
        notes = notes_input or None

    task = AntiProcrastinationTask(
        task_name=task_name,
        predicted_difficulty=pred_diff,
        predicted_pleasure=pred_pleas,
        status="pending",
        notes=notes or None,
    )
    task_id = db.save_task(task)
    task.id = task_id

    console.print(f"\n[bold green][+] Activity #{task_id} logged to Pleasure Prediction Sheet![/bold green]")
    console.print(f"    Activity: \"{task_name}\"")
    console.print(f"    Predicted: Pleasure {pred_pleas}% | Difficulty {pred_diff}%")
    console.print(f"[dim]After doing even 10 minutes of this activity, run 'leahy complete {task_id}' to record actual pleasure vs prediction.[/dim]\n")
    return task

def run_anti_procrastination_complete(
    db: Database,
    task_id: Optional[int] = None,
    actual_pleasure: Optional[int] = None,
    actual_difficulty: Optional[int] = None,
    notes: Optional[str] = None,
):
    """Complete a task on the Anti-Procrastination Sheet and record reality vs expectation."""
    if task_id is None:
        print_header("Burns Anti-Procrastination Sheet", subtitle="Step 2: Record actual difficulty and pleasure to bust cognitive distortions")
        pending_tasks = db.list_tasks(status="pending")
        if not pending_tasks:
            console.print("[yellow][*] No pending activities found. Log one first with 'leahy predict'.[/yellow]")
            return
        console.print("[bold]Select pending activity to complete:[/bold]")
        for t in pending_tasks:
            console.print(f"  [{t.id}] {t.task_name} (Predicted: Pleas {t.predicted_pleasure}%, Diff {t.predicted_difficulty}%)")
        task_id = ask_int_in_range("Activity ID", min(t.id for t in pending_tasks), max(t.id for t in pending_tasks))

    task = db.get_task(task_id)
    if not task:
        console.print(f"[red][!] Activity #{task_id} not found.[/red]")
        return

    console.print(f"\n[bold cyan]Completing Activity #{task.id}:[/bold cyan] \"{task.task_name}\"")
    console.print(f"[dim]Originally predicted: Pleasure {task.predicted_pleasure}%, Difficulty {task.predicted_difficulty}%[/dim]")

    if actual_pleasure is None:
        act_pleas = ask_int_in_range("Actual satisfaction / pleasure experienced (0-100%)", 0, 100, default=70)
    else:
        act_pleas = max(0, min(100, actual_pleasure))

    if actual_difficulty is None:
        act_diff = ask_int_in_range("Actual difficulty in reality (0-100%)", 0, 100, default=30)
    else:
        act_diff = max(0, min(100, actual_difficulty))

    if notes is None and (actual_pleasure is None or actual_difficulty is None):
        refl_input = Prompt.ask("[bold cyan]Reflection / What did you learn? (optional)[/bold cyan]").strip()
        notes = refl_input or None

    task.actual_difficulty = act_diff
    task.actual_pleasure = act_pleas
    task.status = "completed"
    task.completed_at = datetime.now().isoformat()
    if notes:
        task.notes = f"{task.notes or ''} | {notes}".strip(" | ")

    db.update_task(task)

    diff_delta = task.difficulty_delta
    pleas_delta = task.pleasure_delta

    diff_str = f"Easier by [bold green]{diff_delta}%[/bold green]" if (diff_delta and diff_delta > 0) else f"{diff_delta}%"
    pleas_str = f"More satisfying by [bold green]+{pleas_delta}%[/bold green]" if (pleas_delta and pleas_delta > 0) else f"{pleas_delta}%"

    console.print(f"\n[bold green][+] Activity #{task.id} marked completed![/bold green]\n")
    res_text = Text()
    res_text.append("Reality vs Prediction Analysis:\n", style="bold cyan")
    res_text.append(f"  Pleasure / Satisfaction: Predicted {task.predicted_pleasure}% -> Actual {act_pleas}% ({pleas_str})\n")
    res_text.append(f"  Difficulty / Effort:      Predicted {task.predicted_difficulty}% -> Actual {act_diff}% ({diff_str})\n")
    res_text.append("\nBurns Clinical Insight: Procrastination is fueled by the illusion that tasks will be excruciating and unrewarding. Reality almost always delivers far more pleasure than your anxious mind predicts.\n", style="dim")

    console.print(Panel(res_text, title="[bold]Anti-Procrastination & Pleasure Victory[/bold]", box=box.ROUNDED, border_style="green"))


def run_behavioral_experiment_new(
    db: Database,
    title: Optional[str] = None,
    fear_prediction: Optional[str] = None,
    predicted_belief: Optional[int] = None,
    experiment_plan: Optional[str] = None,
) -> BehavioralExperiment:
    """Set up an empirical behavioral experiment to test a catastrophic fear."""
    if not title:
        print_header("Behavioral Experiment Lab", subtitle="Step 1: Formulate feared hypothesis and empirical test")
        title = Prompt.ask("[bold cyan]Experiment Title / Challenge[/bold cyan]").strip()
        while not title:
            title = Prompt.ask("[bold cyan]Please enter a title[/bold cyan]").strip()

    if not fear_prediction:
        console.print("\n[dim]State exactly what catastrophic consequence your anxiety predicts will happen:[/dim]")
        fear_prediction = Prompt.ask("[bold cyan]What exactly do you fear will happen? (Feared Catastrophe)[/bold cyan]").strip()
        while not fear_prediction:
            fear_prediction = Prompt.ask("[bold cyan]Please describe the feared outcome[/bold cyan]").strip()

    if predicted_belief is None:
        predicted_belief = ask_int_in_range("How strongly do you believe this catastrophe will occur? (0-100%)", 0, 100, default=80)

    if not experiment_plan:
        console.print("\n[dim]Describe a concrete, observable action you will take to empirically test this fear:[/dim]")
        experiment_plan = Prompt.ask("[bold cyan]Experiment Action Plan (What will you do?)[/bold cyan]").strip()
        while not experiment_plan:
            experiment_plan = Prompt.ask("[bold cyan]Please enter your action plan[/bold cyan]").strip()

    exp = BehavioralExperiment(
        title=title,
        fear_prediction=fear_prediction,
        predicted_belief=predicted_belief,
        experiment_plan=experiment_plan,
        status="pending",
    )

    exp_id = db.save_experiment(exp)
    exp.id = exp_id

    console.print(f"\n[bold green][+] Behavioral Experiment #{exp_id} created![/bold green]")
    console.print(f"    Challenge: \"{title}\"")
    console.print(f"    Feared Prediction: \"{fear_prediction}\" (Belief: {predicted_belief}%)")
    console.print(f"    Action: \"{experiment_plan}\"")
    console.print(f"[dim]Perform this real-world test, then run 'leahy experiment complete {exp_id}' to record the outcome.[/dim]\n")
    return exp


def run_behavioral_experiment_complete(
    db: Database,
    exp_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    actual_outcome: Optional[str] = None,
    actual_severity: Optional[int] = None,
    fear_realized: Optional[bool] = None,
    conclusion: Optional[str] = None,
) -> Optional[BehavioralExperiment]:
    """Record reality and empirical conclusion for a behavioral experiment."""
    exp_id = exp_id or experiment_id
    if exp_id is None:
        print_header("Behavioral Experiment Lab", subtitle="Step 2: Compare empirical reality against catastrophic fear")
        pending_exps = db.list_experiments(status="pending")
        if not pending_exps:
            console.print("[yellow][*] No pending behavioral experiments found. Design one with 'leahy experiment new'.[/yellow]\n")
            return None
        console.print("[bold]Select pending experiment to evaluate:[/bold]")
        for e in pending_exps:
            console.print(f"  [{e.id}] {e.title} (Fear: \"{e.fear_prediction}\", Belief: {e.predicted_belief}%)")
        exp_id = ask_int_in_range("Experiment ID", min(e.id for e in pending_exps), max(e.id for e in pending_exps))

    exp = db.get_experiment(exp_id)
    if not exp:
        console.print(f"[red][!] Experiment #{exp_id} not found.[/red]")
        return None

    console.print(f"\n[bold cyan]Evaluating Experiment #{exp.id}:[/bold cyan] \"{exp.title}\"")
    console.print(f"  Feared prediction was: [dim]\"{exp.fear_prediction}\" (Belief: {exp.predicted_belief}%)[/dim]")
    console.print(f"  Planned action was:   [dim]\"{exp.experiment_plan}\"[/dim]\n")

    if not actual_outcome:
        actual_outcome = Prompt.ask("[bold cyan]What actually happened when you did the experiment?[/bold cyan]").strip()
        while not actual_outcome:
            actual_outcome = Prompt.ask("[bold cyan]Please describe what actually happened[/bold cyan]").strip()

    if actual_severity is None:
        actual_severity = ask_int_in_range("In reality, how bad was the outcome? (0% = completely fine/positive, 100% = total disaster)", 0, 100, default=20)

    if fear_realized is None:
        realized_ans = Prompt.ask("[bold cyan]Did the feared catastrophe actually materialize? (y/N)[/bold cyan]", default="n").strip().lower()
        fear_realized = (realized_ans == "y")

    if not conclusion:
        console.print("\n[dim]What does this experiment prove about your anxiety and catastrophic predictions?[/dim]")
        conclusion = Prompt.ask("[bold cyan]Conclusion / Key Takeaway[/bold cyan]").strip()
        if not conclusion:
            conclusion = "Reality was far more manageable than my catastrophic prediction."

    exp.actual_outcome = actual_outcome
    exp.actual_severity = actual_severity
    exp.fear_realized = fear_realized
    exp.conclusion = conclusion
    exp.status = "completed"
    exp.completed_at = datetime.now().isoformat()

    db.update_experiment(exp)

    err = exp.prediction_error
    gap_str = f"Reality was [bold green]+{err}% better[/bold green] than feared!" if (err and err > 0) else f"{err}%"

    console.print(f"\n[bold green][+] Behavioral Experiment #{exp.id} marked completed![/bold green]\n")

    res_text = Text()
    res_text.append("Empirical Reality vs Catastrophic Dread:\n", style="bold cyan")
    res_text.append(f"  Feared Prediction:  \"{exp.fear_prediction}\" (Belief: {exp.predicted_belief}%)\n")
    res_text.append(f"  Actual Outcome:     \"{actual_outcome}\" (Severity: {actual_severity}%)\n")
    res_text.append(f"  Fear Disproven?     {'YES (Catastrophe averted)' if not fear_realized else 'Catastrophe occurred'}\n", style="bold green" if not fear_realized else "bold yellow")
    res_text.append(f"  Prediction Error:   {gap_str}\n\n")
    res_text.append(f"Empirical Conclusion:\n  \"{conclusion}\"\n", style="bold green")

    console.print(Panel(res_text, title="[bold]Cognitive Reality Check[/bold]", box=box.ROUNDED, border_style="green"))
    return exp


def run_exposure_ladder_new(
    db: Database,
    fear_theme: Optional[str] = None,
    theme: Optional[str] = None,
    notes: Optional[str] = None,
) -> ExposureLadder:
    """Create a new Exposure Hierarchy / Ladder of Fear."""
    print_header("Exposure Hierarchy Builder", subtitle="Create step-by-step ladder of fear with SUDS ratings (0-100)")

    fear_theme = theme or fear_theme
    if not fear_theme:
        fear_theme = Prompt.ask("[bold cyan]Theme of Fear (e.g. Social Rejection, Public Speaking, Heights)[/bold cyan]").strip()
        while not fear_theme:
            fear_theme = Prompt.ask("[bold cyan]Please specify the fear theme[/bold cyan]").strip()

    ladder = ExposureLadder(fear_theme=fear_theme, notes=notes)
    ladder_id = db.save_ladder(ladder)
    ladder.id = ladder_id

    console.print(f"\n[bold green][+] Fear Hierarchy #{ladder_id} created:[/bold green] \"{fear_theme}\"")
    console.print("[dim]Now add hierarchical steps graded by SUDS (Subjective Units of Distress: 0 = relaxed, 100 = extreme panic).[/dim]\n")

    step_order = 1
    while True:
        try:
            desc = Prompt.ask(f"[bold cyan]Step #{step_order} Challenge description (or press Enter to finish ladder)[/bold cyan]", default="").strip()
            if not desc:
                break
            suds = ask_int_in_range(f"Rate distress/difficulty for '{desc}' (SUDS 0-100)", 0, 100, default=25 * min(4, step_order))
            step = ExposureStep(
                ladder_id=ladder_id,
                step_order=step_order,
                description=desc,
                target_suds=suds,
                status="pending",
            )
            db.save_exposure_step(step)
            ladder.steps.append(step)
            step_order += 1
            console.print(f"  [+] Added Step #{step_order - 1}: \"{desc}\" [SUDS: {suds}/100]\n")
        except (EOFError, KeyboardInterrupt):
            break

    console.print(f"\n[bold green][+] Ladder #{ladder_id} finalized with {len(ladder.steps)} steps.[/bold green]")
    console.print(f"[dim]Inspect with 'leahy ladder show {ladder_id}' and practice with 'leahy ladder practice <step_id>'.[/dim]\n")
    return ladder


def run_exposure_practice(
    db: Database,
    step_id: Optional[int] = None,
    pre_suds: Optional[int] = None,
    post_suds: Optional[int] = None,
    notes: Optional[str] = None,
    mastered: Optional[bool] = None,
):
    """Run an exposure trial to practice desensitization and record habituation."""
    print_header("Exposure Trial Practice", subtitle="Face feared situation and observe natural anxiety habituation")

    if step_id is None:
        ladders = db.list_ladders()
        if not ladders:
            console.print("[yellow][*] No exposure ladders found. Create one with 'leahy ladder new'.[/yellow]\n")
            return
        all_steps = []
        for lad in ladders:
            for s in lad.steps:
                if s.status != "mastered":
                    all_steps.append((lad.fear_theme, s))

        if not all_steps:
            console.print("[bold green][+] Incredible! All steps across your ladders are mastered![/bold green]\n")
            return

        console.print("[bold]Select an exposure step to practice:[/bold]")
        for theme, s in all_steps:
            console.print(f"  [{s.id}] [{theme}] {s.description} (Target SUDS: {s.target_suds}, Reps: {s.repetitions_done})")
        step_id = ask_int_in_range("Step ID", min(s.id for _, s in all_steps), max(s.id for _, s in all_steps))

    step = db.get_exposure_step(step_id)
    if not step:
        console.print(f"[red][!] Step #{step_id} not found.[/red]")
        return

    console.print(f"\n[bold cyan]Practicing Exposure Step #{step.id}:[/bold cyan] \"{step.description}\"")
    console.print(f"[dim]Target SUDS: {step.target_suds}/100 | Repetitions completed so far: {step.repetitions_done}[/dim]\n")

    if pre_suds is None:
        pre_suds = ask_int_in_range("Rate current distress / anxiety BEFORE starting (SUDS 0-100)", 0, 100, default=step.target_suds)

    if post_suds is None:
        console.print("\n[bold yellow][*] EXPOSURE IN PROGRESS [*][/bold yellow]")
        console.print("[dim]Stay in the situation. Do not use safety behaviors. Let the anxiety peak and subside naturally (habituation).[/dim]")
        Prompt.ask("[bold cyan]Press Enter once you have completed the exposure trial...[/bold cyan]")
        post_suds = ask_int_in_range("Rate anxiety / distress AFTER staying in the situation (SUDS 0-100)", 0, 100, default=max(0, pre_suds - 30))

    if notes is None and not mastered:
        refl = Prompt.ask("[bold cyan]What did you learn? (optional)[/bold cyan]", default="").strip()
        if refl:
            notes = refl

    step.repetitions_done += 1
    step.last_pre_suds = pre_suds
    step.last_post_suds = post_suds
    step.status = "in_progress"

    if notes:
        step.notes = f"{step.notes or ''} | Rep {step.repetitions_done}: {notes}".strip(" | ")

    if mastered:
        step.status = "mastered"
        step.completed_at = datetime.now().isoformat()
    elif post_suds <= 25 and step.repetitions_done >= 2:
        mark_mastered = Prompt.ask("[bold green]Anxiety has dropped below 25 across multiple reps. Mark step as MASTERED? (Y/n)[/bold green]", default="y").strip().lower()
        if mark_mastered != "n":
            step.status = "mastered"
            step.completed_at = datetime.now().isoformat()

    db.update_exposure_step(step)

    hab_delta = pre_suds - post_suds
    relief_str = f"Reduced by [bold green]-{hab_delta} SUDS points[/bold green]" if hab_delta > 0 else f"{hab_delta}"

    console.print(f"\n[bold green][+] Exposure Trial #{step.repetitions_done} recorded![/bold green]")
    console.print(f"    Pre-Exposure Distress:  {pre_suds}/100")
    console.print(f"    Post-Exposure Distress: {post_suds}/100 ({relief_str})")
    if step.status == "mastered":
        console.print("[bold green][*] STEP MASTERED! You have desensitized this level of fear.[/bold green]\n")
    else:
        console.print("[dim]Repeat this step a few more times until anxiety remains consistently under 25 SUDS.[/dim]\n")


def run_decatastrophize_session(db: Database, situation: Optional[str] = None):
    """Run a structured David Burns Decatastrophizing mini-session (Worst / Likely / Coping Protocol)."""
    print_header("Decatastrophizing Protocol", subtitle="Method: 'What-If' worst case, best case, most likely, and coping plan")

    if not situation:
        situation = Prompt.ask("[bold cyan]What situation or threat is triggering anxiety?[/bold cyan]").strip()
        while not situation:
            situation = Prompt.ask("[bold cyan]Please enter the situation[/bold cyan]").strip()

    initial_fear = ask_int_in_range("Rate current anxiety / dread intensity (0-100%)", 0, 100, default=80)

    console.print("\n[bold cyan]STEP 1: THE WORST-CASE SCENARIO[/bold cyan]")
    console.print("[dim]Face the dragon directly: If your worst nightmare occurred, what is the absolute worst that could happen?[/dim]")
    worst_case = Prompt.ask("[bold]Worst-case scenario[/bold]").strip()

    console.print("\n[bold cyan]STEP 2: THE BEST-CASE SCENARIO[/bold cyan]")
    console.print("[dim]Now consider the opposite extreme: What would the best possible outcome look like?[/dim]")
    best_case = Prompt.ask("[bold]Best-case scenario[/bold]").strip()

    console.print("\n[bold cyan]STEP 3: THE MOST LIKELY REALISTIC SCENARIO[/bold cyan]")
    console.print("[dim]Based on facts, logic, and past history, what is the most probable outcome in reality?[/dim]")
    likely_case = Prompt.ask("[bold]Most likely outcome[/bold]").strip()

    console.print("\n[bold cyan]STEP 4: ACTIONABLE COPING PROTOCOL[/bold cyan]")
    console.print("[dim]Even in the unlikely event the worst happened, what concrete steps would you take to cope and survive?[/dim]")
    coping_plan = Prompt.ask("[bold]How I would cope and handle it[/bold]").strip()

    final_fear = ask_int_in_range("Re-rate anxiety intensity after looking at reality & coping (0-100%)", 0, 100, default=max(0, initial_fear - 35))

    details = {
        "worst_case": worst_case,
        "best_case": best_case,
        "likely_case": likely_case,
        "coping_plan": coping_plan,
    }
    import json

    reframe_thought = f"The most likely outcome is: '{likely_case}'. Even if the worst happened ('{worst_case}'), I have a coping protocol: '{coping_plan}'."

    entry = MoodEntry(
        entry_type="cbt_record",
        initial_mood=max(1, 10 - round(initial_fear / 10)),
        primary_emotion="Anxious",
        emotion_intensity_initial=initial_fear,
        situation=situation,
        automatic_thought=f"Worst case: {worst_case}",
        distortions=["catastrophizing", "jumping_fortune_telling"],
        evidence_against=f"Most likely realistic outcome: {likely_case}",
        alternative_thought=reframe_thought,
        belief_final=80,
        final_mood=min(10, 10 - round(final_fear / 10)),
        emotion_intensity_final=final_fear,
        action_plan=coping_plan,
        technique_used="what_if_decatastrophize",
        technique_details=json.dumps(details),
        notes=f"Decatastrophizing: Best case: {best_case}",
    )
    entry_id = db.save_entry(entry)

    relief = initial_fear - final_fear
    console.print(f"\n[bold green][+] Decatastrophizing session saved as CBT record #{entry_id}![/bold green]")
    console.print(f"    Anxiety Relief: {initial_fear}% -> {final_fear}% (Relief: -{relief}%)")
    console.print(f"    Empowering Reframe: \"{reframe_thought}\"\n")


