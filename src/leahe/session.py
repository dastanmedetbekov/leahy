"""Interactive guided CBT sessions and quick mood check-ins.

Strictly NO emojis. Clean ASCII prompts.
"""

from typing import List, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich import box

from .models import MoodEntry
from .database import Database
from .cbt_data import COGNITIVE_DISTORTIONS, STANDARD_EMOTIONS, SOCRATIC_QUESTIONS
from .burns_methods import BURNS_METHODS, BurnsMethod
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
    console.print("[dim]Select which cognitive distortions appear in this automatic thought (enter numbers separated by commas, e.g. 1, 7):[/dim]\n")

    dist_keys = list(COGNITIVE_DISTORTIONS.keys())
    for idx, key in enumerate(dist_keys, 1):
        d = COGNITIVE_DISTORTIONS[key]
        console.print(f"  [{idx:>2}] [bold magenta]{d.name}[/bold magenta]: [dim]{d.summary}[/dim]")

    console.print("  [ 0] None / Skip identification\n")

    while True:
        raw = Prompt.ask("[bold cyan]Enter distortion numbers (e.g. 1, 3, 7)[/bold cyan]").strip()
        if not raw or raw == "0":
            return []

        selected = []
        valid = True
        for part in raw.replace(";", ",").split(","):
            part = part.strip()
            if not part:
                continue
            try:
                num = int(part)
                if 1 <= num <= len(dist_keys):
                    code = dist_keys[num - 1]
                    if code not in selected:
                        selected.append(code)
                else:
                    console.print(f"[red][!] Number {num} is out of range (1-{len(dist_keys)}).[/red]")
                    valid = False
            except ValueError:
                console.print(f"[red][!] Invalid input '{part}'. Please enter numbers.[/red]")
                valid = False

        if valid and selected:
            console.print("\n[bold green][+] Identified Distortions:[/bold green]")
            for code in selected:
                console.print(f"    [*] [magenta]{COGNITIVE_DISTORTIONS[code].name}[/magenta]")
            return selected
        elif valid and not selected:
            return []

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
    notes = Prompt.ask("[bold cyan]Any additional thoughts / notes (optional)[/bold cyan]").strip()

    entry = MoodEntry(
        entry_type="quick",
        initial_mood=mood,
        primary_emotion=emotion,
        emotion_intensity_initial=intensity,
        energy_level=energy,
        situation=situation or None,
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

        console.print("\n[dim]Prompt B: What objective facts contradict or weaken this thought? (What would you tell a friend? Are there alternative explanations?)[/dim]")
        evidence_against = Prompt.ask("[bold]Evidence Against the Thought[/bold]").strip()
        while not evidence_against:
            console.print("[red][!] Please identify at least one piece of contradictory evidence or an alternative view.[/red]")
            evidence_against = Prompt.ask("[bold]Evidence Against the Thought[/bold]").strip()

        # Step 6: Alternative / Balanced Reframe
        console.print("\n[bold cyan]STEP 6: RATIONAL & BALANCED ALTERNATIVE THOUGHT[/bold cyan]")
        console.print("[dim]Synthesize the evidence into a balanced, realistic, compassionate perspective.[/dim]")
        alt_thought = Prompt.ask("[bold]Balanced Alternative Thought[/bold]").strip()
        while not alt_thought:
            console.print("[red][!] Please formulate a balanced alternative thought.[/red]")
            alt_thought = Prompt.ask("[bold]Balanced Alternative Thought[/bold]").strip()

    belief_final = ask_int_in_range("How much do you believe this new, balanced thought? (0-100%)", 0, 100, default=75)

    # Step 7: Outcome & Mood Re-rating
    console.print("\n[bold cyan]STEP 7: OUTCOME & RE-RATING[/bold cyan]")
    console.print("[dim]Re-assess how you feel now after examining the evidence and framing a balanced thought.[/dim]")
    final_mood = ask_int_in_range("Re-rate overall mood (1-10)", 1, 10, default=min(10, initial_mood + 2))
    final_intensity = ask_int_in_range(f"Re-rate intensity of '{primary_emotion}' (0-100%)", 0, 100, default=max(0, initial_intensity - 30))

    # Step 8: Behavioral Activation / Micro-Action
    console.print("\n[bold cyan]STEP 8: CONSTRUCTIVE ACTION (OPTIONAL)[/bold cyan]")
    console.print("[dim]What is one small, concrete step you can take right now to help yourself or address the situation?[/dim]")
    action_plan = Prompt.ask("[bold]Small Constructive Action Step (optional)[/bold]").strip()

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
