"""Terminal presentation layer using Rich and clean ASCII styling.

Strictly NO emojis. Uses clean ASCII symbols ([*], [+], [-], [!], [x], [o]).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from .models import MoodEntry
from .cbt_data import COGNITIVE_DISTORTIONS, DistortionInfo
from .burns_methods import BURNS_METHODS, BurnsMethod
from .stats import render_ascii_bar_chart, render_mood_timeline

console = Console()

def print_header(title: str, subtitle: Optional[str] = None):
    text = Text()
    text.append(f"=== {title.upper()} ===\n", style="bold cyan")
    if subtitle:
        text.append(subtitle, style="dim")
    console.print(Panel(text, box=box.ROUNDED, expand=False, border_style="cyan"))

def format_mood_badge(mood: Optional[int]) -> str:
    if mood is None:
        return "[dim]--[/dim]"
    if mood <= 3:
        return f"[bold red]{mood}/10[/bold red]"
    elif mood <= 6:
        return f"[bold yellow]{mood}/10[/bold yellow]"
    else:
        return f"[bold green]{mood}/10[/bold green]"

def format_delta_badge(delta: Optional[int]) -> str:
    if delta is None:
        return "[dim]n/a[/dim]"
    if delta > 0:
        return f"[bold green]+{delta}[/bold green]"
    elif delta == 0:
        return f"[bold yellow]0[/bold yellow]"
    else:
        return f"[bold red]{delta}[/bold red]"

def render_entries_table(entries: List[MoodEntry], total_count: Optional[int] = None):
    if not entries:
        console.print("[yellow][*] No entries found matching the criteria.[/yellow]")
        return

    table = Table(
        title="Mood & CBT History Log" + (f" (showing {len(entries)} of {total_count})" if total_count else ""),
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("ID", justify="right", style="dim", width=4)
    table.add_column("Date / Time", justify="left", width=16)
    table.add_column("Type", justify="center", width=8)
    table.add_column("Mood", justify="center", width=7)
    table.add_column("Shift", justify="center", width=6)
    table.add_column("Primary Emotion", justify="left", width=18)
    table.add_column("Distortions / Situation", justify="left")

    for entry in entries:
        dt_str = entry.parsed_datetime.strftime("%Y-%m-%d %H:%M")
        etype = "[cyan]CBT[/cyan]" if entry.is_cbt else "[dim]Quick[/dim]"
        mood_str = format_mood_badge(entry.initial_mood)
        if entry.is_cbt and entry.final_mood is not None:
            mood_str += f" -> {format_mood_badge(entry.final_mood)}"
        delta_str = format_delta_badge(entry.mood_delta)

        emotion_str = f"{entry.primary_emotion} ({entry.emotion_intensity_initial}%)"

        details_parts = []
        if entry.distortions:
            dist_names = [COGNITIVE_DISTORTIONS[d].name for d in entry.distortions if d in COGNITIVE_DISTORTIONS]
            if dist_names:
                details_parts.append("[magenta][" + ", ".join(dist_names[:2]) + ("..." if len(dist_names) > 2 else "") + "][/magenta]")
        if entry.situation:
            short_sit = entry.situation[:45] + ("..." if len(entry.situation) > 45 else "")
            details_parts.append(short_sit)
        elif entry.automatic_thought:
            short_th = entry.automatic_thought[:45] + ("..." if len(entry.automatic_thought) > 45 else "")
            details_parts.append(f"NAT: '{short_th}'")

        details_text = " | ".join(details_parts) if details_parts else "[dim]--[/dim]"

        table.add_row(
            str(entry.id),
            dt_str,
            etype,
            mood_str,
            delta_str,
            emotion_str,
            details_text,
        )

    console.print(table)
    console.print("[dim]Use 'leahe show <id>' to view the full CBT examination details for any entry.[/dim]\n")

def render_entry_detail(entry: MoodEntry):
    title = f"Entry #{entry.id} - {entry.parsed_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
    console.print()
    print_header(title, subtitle=f"Type: {entry.entry_type.upper()} SESSION")

    # Grid / Panels for details
    grid = Table.grid(padding=1)
    grid.add_column(style="bold cyan", width=22)
    grid.add_column()

    grid.add_row("Initial Mood:", f"{format_mood_badge(entry.initial_mood)} (Scale 1-10)")
    grid.add_row("Primary Emotion:", f"{entry.primary_emotion} at {entry.emotion_intensity_initial}% intensity")
    if entry.energy_level is not None:
        grid.add_row("Energy Level:", f"{entry.energy_level}/10")

    if entry.situation:
        grid.add_row("Trigger / Situation:", entry.situation)

    if entry.is_cbt:
        grid.add_row("---", "------------------------------------------------------------")
        if entry.technique_used:
            t_name = BURNS_METHODS[entry.technique_used].name if entry.technique_used in BURNS_METHODS else entry.technique_used
            grid.add_row("Method Applied:", f"[bold cyan]{t_name}[/bold cyan]")

        grid.add_row(
            "Automatic Thought (NAT):",
            f"[bold red]\"{entry.automatic_thought or 'N/A'}\"[/bold red]"
            + (f" [dim](Belief: {entry.belief_initial}%)[/dim]" if entry.belief_initial is not None else "")
        )

        if entry.distortions:
            dist_list = []
            for d in entry.distortions:
                info = COGNITIVE_DISTORTIONS.get(d)
                if info:
                    dist_list.append(f"[bold magenta][*] {info.name}[/bold magenta]: {info.summary}")
                else:
                    dist_list.append(f"[*] {d}")
            grid.add_row("Cognitive Distortions:", "\n".join(dist_list))
        else:
            grid.add_row("Cognitive Distortions:", "[dim]None identified[/dim]")

        if entry.technique_details:
            import json
            try:
                td = json.loads(entry.technique_details)
                steps = td.get("steps", [])
                if steps:
                    step_lines = []
                    for s in steps:
                        step_lines.append(f"[bold yellow]{s.get('prompt')}:[/bold yellow] {s.get('response')}")
                    grid.add_row("Technique Steps:", "\n".join(step_lines))
            except Exception:
                pass

        if entry.evidence_for:
            grid.add_row("Evidence Supporting:", f"[yellow]{entry.evidence_for}[/yellow]")
        if entry.evidence_against:
            grid.add_row("Evidence Contradicting:", f"[green]{entry.evidence_against}[/green]")

        if entry.alternative_thought:
            grid.add_row(
                "Rational Reframe:",
                f"[bold green]\"{entry.alternative_thought}\"[/bold green]"
                + (f" [dim](Belief: {entry.belief_final}%)[/dim]" if entry.belief_final is not None else "")
            )

        grid.add_row("---", "------------------------------------------------------------")
        grid.add_row("Post-CBT Mood:", f"{format_mood_badge(entry.final_mood)} (Shift: {format_delta_badge(entry.mood_delta)})")
        if entry.emotion_intensity_final is not None:
            grid.add_row(
                "Post-CBT Intensity:",
                f"{entry.emotion_intensity_final}% (Distress relief: {format_delta_badge(entry.intensity_delta)}%)"
            )

        if entry.action_plan:
            grid.add_row("Next Action Step:", f"[bold cyan]{entry.action_plan}[/bold cyan]")

    if entry.notes:
        grid.add_row("Additional Notes:", entry.notes)

    panel = Panel(grid, box=box.ROUNDED, border_style="cyan")
    console.print(panel)
    console.print()

def render_statistics_dashboard(stats: Dict[str, Any], entries: List[MoodEntry]):
    if not stats or stats.get("total_entries", 0) == 0:
        console.print("[yellow][*] No mood data found yet. Start by logging an entry with 'leahe check' or 'leahe check --cbt'.[/yellow]")
        return

    print_header("Comprehensive CBT Mood Analytics & Verification", subtitle="Evidence-based psychological tracking metrics")

    # 1. Summary Cards Table
    summary_table = Table(box=box.SIMPLE, show_header=False, expand=True)
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Value", style="cyan")
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Value", style="cyan")

    total = stats["total_entries"]
    cbt_count = stats["cbt_entries_count"]
    quick_count = stats["quick_entries_count"]
    avg_m = f"{stats['avg_mood']:.1f}/10"
    span_str = f"{stats['days_span']} day(s) ({stats['first_date']} to {stats['last_date']})"
    streak_str = f"{stats['current_streak']} day(s) (Longest: {stats['longest_streak']} days)"

    summary_table.add_row("Total Entries:", str(total), "Average Mood:", avg_m)
    summary_table.add_row("CBT Deep Sessions:", str(cbt_count), "Quick Check-ins:", str(quick_count))
    summary_table.add_row("Active Logging Span:", span_str, "Current Streak:", streak_str)

    console.print(Panel(summary_table, title="[bold]Overview Metrics[/bold]", box=box.ROUNDED, border_style="blue"))

    # 2. CBT Therapeutic Efficacy Section
    if stats["cbt_with_outcomes"] > 0:
        cbt_table = Table(box=box.SIMPLE, show_header=False, expand=True)
        cbt_table.add_column("Metric", style="bold")
        cbt_table.add_column("Value")

        avg_pre = f"{stats['avg_cbt_initial_mood']:.1f}/10"
        avg_post = f"{stats['avg_cbt_final_mood']:.1f}/10"
        avg_delta = f"+{stats['avg_mood_delta']:.2f}" if stats['avg_mood_delta'] and stats['avg_mood_delta'] > 0 else f"{stats['avg_mood_delta']:.2f}"
        rate_str = f"{stats['improvement_rate']:.1f}% ({stats['improved_count']} improved, {stats['unchanged_count']} steady, {stats['worsened_count']} declined)"

        cbt_table.add_row("Pre-CBT Average Mood:", avg_pre)
        cbt_table.add_row("Post-CBT Average Mood:", avg_post)
        cbt_table.add_row("Average Mood Delta:", f"[bold green]{avg_delta}[/bold green]" if stats['avg_mood_delta'] and stats['avg_mood_delta'] > 0 else avg_delta)
        cbt_table.add_row("CBT Improvement Success Rate:", f"[bold cyan]{rate_str}[/bold cyan]")

        if stats["avg_relief_percent"] is not None:
            cbt_table.add_row(
                "Emotional Distress Relief:",
                f"Distress dropped on average by [bold green]{stats['avg_relief_percent']:.1f}%[/bold green] ({stats['avg_intensity_initial']:.1f}% -> {stats['avg_intensity_final']:.1f}%)"
            )

        console.print(Panel(cbt_table, title="[bold]CBT Therapeutic Efficacy & Mood Shift[/bold]", box=box.ROUNDED, border_style="green"))

    # 3. Cognitive Distortions Frequency Breakdown
    distortions = stats.get("distortions", [])
    if distortions:
        dist_table = Table(
            title="Cognitive Distortion Prevalence (Ranked)",
            box=box.ROUNDED,
            header_style="bold magenta",
        )
        dist_table.add_column("Rank", justify="right", width=4)
        dist_table.add_column("Cognitive Distortion", justify="left", width=38)
        dist_table.add_column("Count", justify="right", width=6)
        dist_table.add_column("% of CBT", justify="right", width=10)
        dist_table.add_column("Avg Initial Mood", justify="center", width=16)

        chart_items = []
        for idx, d in enumerate(distortions, 1):
            dist_table.add_row(
                str(idx),
                d["name"],
                str(d["count"]),
                f"{d['percentage']:.1f}%",
                format_mood_badge(round(d["avg_initial_mood"])),
            )
            chart_items.append((d["name"][:25], d["count"], d["percentage"]))

        console.print(dist_table)

        # ASCII Bar chart
        bar_lines = render_ascii_bar_chart(chart_items[:6])
        bar_panel = Panel(
            Text("\n".join(bar_lines)),
            title="[bold]Top Distortions Frequency Bar Chart[/bold]",
            box=box.ROUNDED,
            border_style="magenta",
        )
        console.print(bar_panel)
    else:
        console.print("[dim][*] No cognitive distortions identified yet in CBT sessions.[/dim]\n")

    # 4. Emotions Breakdown
    emotions = stats.get("emotions", [])
    if emotions:
        emo_table = Table(
            title="Primary Emotions Identified",
            box=box.ROUNDED,
            header_style="bold yellow",
        )
        emo_table.add_column("Emotion", justify="left", width=22)
        emo_table.add_column("Occurrences", justify="right", width=12)
        emo_table.add_column("Share", justify="right", width=10)
        emo_table.add_column("Avg Initial Intensity", justify="center", width=22)

        for e in emotions:
            emo_table.add_row(
                e["emotion"],
                str(e["count"]),
                f"{e['percentage']:.1f}%",
                f"{e['avg_intensity']:.1f}%",
            )
        console.print(emo_table)

    # 5. David Burns Techniques Efficacy
    techniques = stats.get("techniques", [])
    if techniques:
        tech_table = Table(
            title="David Burns Restructuring Methods Efficacy",
            box=box.ROUNDED,
            header_style="bold cyan",
        )
        tech_table.add_column("Restructuring Method", justify="left", width=36)
        tech_table.add_column("Times Used", justify="right", width=12)
        tech_table.add_column("Avg Mood Delta", justify="center", width=16)
        tech_table.add_column("Avg Distress Relief", justify="center", width=20)

        for t in techniques:
            delta_str = format_delta_badge(round(t["avg_mood_delta"]))
            relief_str = f"[bold green]-{t['avg_distress_relief']:.1f}%[/bold green]" if t['avg_distress_relief'] > 0 else f"{t['avg_distress_relief']:.1f}%"
            tech_table.add_row(
                t["name"],
                str(t["count"]),
                delta_str,
                relief_str,
            )
        console.print(tech_table)

    # 6. Mood Timeline Plot
    timeline_lines = render_mood_timeline(entries, limit=18)
    timeline_panel = Panel(
        Text("\n".join(timeline_lines)),
        title="[bold]Recent Mood Trajectory (Last 18 Entries)[/bold]",
        box=box.ROUNDED,
        border_style="cyan",
    )
    console.print(timeline_panel)

def render_distortions_catalog():
    print_header("CBT Cognitive Distortions Reference Guide", subtitle="Catalog of standard thinking traps identified in Cognitive Behavioral Therapy")

    for idx, (code, info) in enumerate(COGNITIVE_DISTORTIONS.items(), 1):
        content = Text()
        content.append(f"Definition:\n", style="bold cyan")
        content.append(f"{info.description}\n\n")

        content.append(f"Typical Example:\n", style="bold yellow")
        content.append(f"{info.example}\n\n")

        content.append(f"CBT Challenge Questions:\n", style="bold green")
        for q in info.challenge_questions:
            content.append(f"  [?] {q}\n")

        panel = Panel(
            content,
            title=f"[bold]{idx}. {info.name} ({code})[/bold]",
            subtitle=info.summary,
            box=box.ROUNDED,
            border_style="cyan",
        )
        console.print(panel)

def render_burns_methods_catalog():
    print_header("David Burns' Cognitive Restructuring Methods", subtitle="Clinical techniques for testing automatic thoughts and irrational beliefs (Burns TEAM-CBT)")

    for idx, (code, method) in enumerate(BURNS_METHODS.items(), 1):
        content = Text()
        content.append(f"Category: {method.category}\n", style="bold magenta")
        content.append(f"{method.description}\n\n")

        content.append(f"When to Apply:\n", style="bold cyan")
        content.append(f"{method.when_to_use}\n\n")

        content.append(f"Guided Prompts / Socratic Steps:\n", style="bold green")
        for p in method.guided_prompts:
            content.append(f"  [>] {p}\n")
        content.append("\n")

        content.append(f"Clinical Example:\n", style="bold yellow")
        content.append(f"{method.example}\n")

        panel = Panel(
            content,
            title=f"[bold]{idx}. {method.name} ({code})[/bold]",
            subtitle=method.summary,
            box=box.ROUNDED,
            border_style="magenta",
        )
        console.print(panel)

def render_audit_verification(entries: List[MoodEntry]):
    """Detailed verification/audit ('проверка') of emotional patterns and unresolved thoughts."""
    print_header("CBT Thought Pattern & Mood Verification Audit", subtitle="In-depth clinical pattern analysis of logged entries")

    if not entries:
        console.print("[yellow][*] No entries to audit yet.[/yellow]")
        return

    cbt_entries = [e for e in entries if e.is_cbt]

    # 1. Unresolved or Worsened Entries Check
    unresolved = [e for e in cbt_entries if e.final_mood is not None and e.final_mood <= e.initial_mood]
    if unresolved:
        unres_table = Table(
            title=f"Flagged Entries: Sessions Without Mood Improvement ({len(unresolved)})",
            box=box.ROUNDED,
            border_style="red",
            header_style="bold red",
        )
        unres_table.add_column("ID", width=4)
        unres_table.add_column("Date", width=12)
        unres_table.add_column("Mood Shift", width=12)
        unres_table.add_column("Automatic Thought", width=30)
        unres_table.add_column("Balanced Thought", width=30)

        for u in unresolved:
            dt_s = u.parsed_datetime.strftime("%Y-%m-%d")
            shift_s = f"{u.initial_mood} -> {u.final_mood} ({format_delta_badge(u.mood_delta)})"
            nat = (u.automatic_thought[:28] + "..") if u.automatic_thought else "--"
            alt = (u.alternative_thought[:28] + "..") if u.alternative_thought else "--"
            unres_table.add_row(str(u.id), dt_s, shift_s, nat, alt)

        console.print(unres_table)
        console.print("[dim][!] Recommendation: Revisit these sessions using 'leahe show <id>' and test more realistic or compassionate reframes.[/dim]\n")
    else:
        console.print(Panel("[bold green][+] Excellent: All recorded CBT sessions produced positive mood improvement![/bold green]", box=box.ROUNDED))

    # 2. Chronic Low Mood Check (initial mood <= 3)
    low_mood_entries = [e for e in entries if e.initial_mood <= 3]
    console.print(f"[*] Total sessions logged with severe distress (mood <= 3): [bold]{len(low_mood_entries)}[/bold] ({len(low_mood_entries)/len(entries)*100:.1f}%)")

    # 3. Recurring Distortion Check
    distortion_counts: Dict[str, int] = {}
    for e in cbt_entries:
        for d in e.distortions:
            distortion_counts[d] = distortion_counts.get(d, 0) + 1

    if distortion_counts:
        top_distortion, count = max(distortion_counts.items(), key=lambda x: x[1])
        top_info = COGNITIVE_DISTORTIONS.get(top_distortion)
        top_name = top_info.name if top_info else top_distortion
        pct = (count / len(cbt_entries)) * 100

        insight_content = Text()
        insight_content.append("Primary Cognitive Habit: ", style="bold yellow")
        insight_content.append(f"Your most frequent cognitive distortion is ")
        insight_content.append(f"{top_name}", style="bold magenta")
        insight_content.append(f", appearing in ")
        insight_content.append(f"{pct:.1f}%", style="bold")
        insight_content.append(f" of your CBT sessions ({count} times).\n\n")

        insight_content.append("Antidote Strategy:\n", style="bold green")
        if top_info:
            for q in top_info.challenge_questions:
                insight_content.append(f"  [-] {q}\n")

        console.print(Panel(insight_content, title="[bold]Pattern Verification Insight[/bold]", box=box.ROUNDED, border_style="yellow"))
