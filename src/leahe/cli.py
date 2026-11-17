"""Leahe CLI interface for Cognitive Behavioral Therapy Mood Tracking.

Strictly NO emojis. Clean ASCII symbols.
"""

from pathlib import Path
from typing import Optional
import click
from rich.console import Console

from .database import Database
from .views import (
    print_header,
    render_entries_table,
    render_entry_detail,
    render_statistics_dashboard,
    render_distortions_catalog,
    render_burns_methods_catalog,
    render_audit_verification,
)
from .session import run_quick_checkin, run_cbt_session, run_belief_challenge_session
from .stats import calculate_summary_stats
from .export import export_to_json, export_to_markdown
from .models import MoodEntry

console = Console()

def get_db(ctx: click.Context) -> Database:
    if "db" not in ctx.obj or ctx.obj["db"] is None:
        db_path = ctx.obj.get("db_path")
        ctx.obj["db"] = Database(Path(db_path) if db_path else None)
    return ctx.obj["db"]

@click.group(invoke_without_command=True)
@click.option("--db", "db_path", type=click.Path(), default=None, help="Custom SQLite database file path.")
@click.pass_context
def main(ctx, db_path):
    """Leahe - Cognitive Behavioral Therapy Mood Terminal Utility.

    Track your mood, challenge cognitive distortions, and review therapeutic statistics.
    """
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = db_path
    ctx.obj["db"] = None

    if ctx.invoked_subcommand is None:
        db = get_db(ctx)
        # If run without subcommand, prompt interactive choice
        print_header("Leahe - CBT Mood Tracker", subtitle="Evidence-based Cognitive Behavioral Therapy Mood Tracker")
        console.print("[bold]Select an action:[/bold]")
        console.print("  [1] Quick Mood Check-in")
        console.print("  [2] Full CBT Thought Record (Guided Session)")
        console.print("  [3] Challenge a Belief / Rule (David Burns Lab)")
        console.print("  [4] View Detailed Statistics & Progress")
        console.print("  [5] Run Pattern Verification Audit")
        console.print("  [6] Browse History Log")
        console.print("  [7] Cognitive Distortions Guide")
        console.print("  [8] David Burns Restructuring Methods Guide")
        console.print("  [0] Exit\n")

        from rich.prompt import Prompt
        choice = Prompt.ask("[bold cyan]Choice[/bold cyan]", default="1").strip()
        if choice == "1":
            run_quick_checkin(db)
        elif choice == "2":
            run_cbt_session(db)
        elif choice == "3":
            run_belief_challenge_session(db)
        elif choice == "4":
            ctx.invoke(stats)
        elif choice == "5":
            ctx.invoke(verify)
        elif choice == "6":
            ctx.invoke(history)
        elif choice == "7":
            ctx.invoke(distortions)
        elif choice == "8":
            ctx.invoke(methods)
        else:
            console.print("[dim]Goodbye.[/dim]")

@main.command("check")
@click.option("--quick", is_flag=True, help="Run quick check-in directly.")
@click.option("--cbt", is_flag=True, help="Run full CBT thought record session directly.")
@click.pass_context
def check(ctx, quick, cbt):
    """Start an interactive mood check-in or CBT thought record."""
    db: Database = get_db(ctx)
    if cbt:
        run_cbt_session(db)
    elif quick:
        run_quick_checkin(db)
    else:
        from rich.prompt import Prompt
        console.print("[bold]Choose check-in mode:[/bold]")
        console.print("  [1] Quick Check-in (Mood, Emotion, Energy - 30 seconds)")
        console.print("  [2] Full CBT Thought Record (Deconstruct NAT, identify distortions, reframe)")
        choice = Prompt.ask("[bold cyan]Select (1 or 2)[/bold cyan]", default="2").strip()
        if choice == "1":
            run_quick_checkin(db)
        else:
            run_cbt_session(db)

@main.command("cbt")
@click.pass_context
def cbt_cmd(ctx):
    """Run a full CBT Guided Thought Record session."""
    db: Database = get_db(ctx)
    run_cbt_session(db)

@main.command("challenge")
@click.pass_context
def challenge_cmd(ctx):
    """Challenge and test a negative belief or rule (David Burns Lab)."""
    db: Database = get_db(ctx)
    run_belief_challenge_session(db)

@main.command("test-belief")
@click.pass_context
def test_belief_cmd(ctx):
    """Alias for 'challenge' - run the David Burns Belief Testing Lab."""
    db: Database = get_db(ctx)
    run_belief_challenge_session(db)

@main.command("quick")
@click.pass_context
def quick_cmd(ctx):
    """Run a quick mood check-in."""
    db: Database = get_db(ctx)
    run_quick_checkin(db)

@main.command("stats")
@click.pass_context
def stats(ctx):
    """Display comprehensive CBT statistics, distortion frequencies, and charts."""
    db: Database = get_db(ctx)
    entries = db.get_all_entries()
    summary = calculate_summary_stats(entries)
    render_statistics_dashboard(summary, entries)

@main.command("verify")
@click.pass_context
def verify(ctx):
    """Run deep pattern verification audit (unresolved thoughts, severe episodes, habit traps)."""
    db: Database = get_db(ctx)
    entries = db.get_all_entries()
    render_audit_verification(entries)

@main.command("history")
@click.option("--limit", "-n", default=20, help="Number of records to display.")
@click.option("--offset", default=0, help="Offset for pagination.")
@click.option("--cbt-only", is_flag=True, help="Show only CBT thought records.")
@click.option("--quick-only", is_flag=True, help="Show only quick check-ins.")
@click.option("--distortion", "-d", help="Filter by cognitive distortion code (e.g. catastrophizing).")
@click.option("--min-mood", type=int, help="Filter by minimum initial mood.")
@click.option("--max-mood", type=int, help="Filter by maximum initial mood.")
@click.option("--query", "-q", help="Search keyword in situations and thoughts.")
@click.pass_context
def history(ctx, limit, offset, cbt_only, quick_only, distortion, min_mood, max_mood, query):
    """List previous mood entries and CBT records."""
    db: Database = get_db(ctx)
    entry_type = None
    if cbt_only:
        entry_type = "cbt_record"
    elif quick_only:
        entry_type = "quick"

    entries = db.list_entries(
        limit=limit,
        offset=offset,
        entry_type=entry_type,
        distortion=distortion,
        min_mood=min_mood,
        max_mood=max_mood,
        query=query,
    )
    total_count = db.count_entries()
    render_entries_table(entries, total_count=total_count)

@main.command("show")
@click.argument("entry_id", type=int)
@click.pass_context
def show(ctx, entry_id):
    """Inspect full CBT examination details for a specific entry ID."""
    db: Database = get_db(ctx)
    entry = db.get_entry(entry_id)
    if not entry:
        console.print(f"[red][!] Entry #{entry_id} not found.[/red]")
        return
    render_entry_detail(entry)

@main.command("delete")
@click.argument("entry_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Confirm deletion without prompt.")
@click.pass_context
def delete(ctx, entry_id, yes):
    """Delete a mood entry by ID."""
    db: Database = get_db(ctx)
    entry = db.get_entry(entry_id)
    if not entry:
        console.print(f"[red][!] Entry #{entry_id} not found.[/red]")
        return

    if not yes:
        confirm = click.confirm(f"Are you sure you want to delete entry #{entry_id}?")
        if not confirm:
            console.print("[dim]Deletion cancelled.[/dim]")
            return

    success = db.delete_entry(entry_id)
    if success:
        console.print(f"[green][+] Entry #{entry_id} successfully deleted.[/green]")
    else:
        console.print(f"[red][!] Failed to delete entry #{entry_id}.[/red]")

@main.command("distortions")
def distortions():
    """Browse the Cognitive Distortions Reference Guide."""
    render_distortions_catalog()

@main.command("methods")
def methods():
    """Browse David Burns' 10 Cognitive Restructuring Methods Guide."""
    render_burns_methods_catalog()

@main.command("techniques")
def techniques():
    """Alias for 'methods' - browse David Burns' restructuring techniques."""
    render_burns_methods_catalog()

@main.command("export")
@click.option("--format", "-f", "fmt", type=click.Choice(["markdown", "md", "json"]), default="markdown", help="Export format.")
@click.option("--output", "-o", "out_path", type=click.Path(), required=True, help="Destination file path.")
@click.pass_context
def export_cmd(ctx, fmt, out_path):
    """Export all mood records to Markdown or JSON."""
    db: Database = get_db(ctx)
    entries = db.get_all_entries()
    if not entries:
        console.print("[yellow][*] No records found to export.[/yellow]")
        return

    path = Path(out_path)
    if fmt in ["markdown", "md"]:
        export_to_markdown(entries, path)
        console.print(f"[bold green][+] Exported {len(entries)} records to Markdown:[/bold green] {path.resolve()}")
    else:
        export_to_json(entries, path)
        console.print(f"[bold green][+] Exported {len(entries)} records to JSON:[/bold green] {path.resolve()}")

@main.command("seed-demo")
@click.option("--count", default=10, help="Number of realistic CBT demo records to insert.")
@click.pass_context
def seed_demo(ctx, count):
    """Populate database with sample realistic CBT records for testing & exploration."""
    db: Database = get_db(ctx)
    from datetime import datetime, timedelta

    sample_scenarios = [
        {
            "situation": "Received constructive criticism on code review regarding error handling.",
            "thought": "I am an awful developer and everyone secretly thinks I don't belong here.",
            "emotions": ("Anxious", 80),
            "distortions": ["all_or_nothing", "catastrophizing", "jumping_mind_reading"],
            "evidence_for": "The reviewer highlighted 3 edge cases I missed in the PR.",
            "evidence_against": "The review was polite and professional. I solved the core feature well. Code review is standard practice to catch edge cases, not a character judgment.",
            "alternative": "Missing edge cases is a normal part of engineering. The feedback makes the codebase stronger and helps me learn.",
            "init_mood": 3,
            "final_mood": 7,
            "final_intensity": 25,
            "technique": "double_standard",
            "action": "Implement the suggested tests and thank the reviewer for the feedback.",
        },
        {
            "situation": "Invited to speak at an upcoming internal engineering meetup.",
            "thought": "I will freeze up on stage and humiliate myself in front of the whole department.",
            "emotions": ("Nervous", 85),
            "distortions": ["jumping_fortune_telling", "catastrophizing", "emotional_reasoning"],
            "evidence_for": "I feel my heart racing whenever I think about public speaking.",
            "evidence_against": "I gave two lightning talks last year that received positive feedback. Having a prepared slide deck and rehearsal eliminates the risk of total freezing.",
            "alternative": "Nervousness is adrenaline, not proof of disaster. If I prepare slides and practice, I will do a competent job.",
            "init_mood": 4,
            "final_mood": 7,
            "final_intensity": 30,
            "technique": "what_if_decatastrophize",
            "action": "Outline 5 key bullet points for the talk today.",
        },
        {
            "situation": "Friend did not reply to my text message for 12 hours.",
            "thought": "They are tired of me and our friendship is drifting away.",
            "emotions": ("Sad", 75),
            "distortions": ["jumping_mind_reading", "overgeneralization", "personalization"],
            "evidence_for": "They haven't texted back yet.",
            "evidence_against": "They work 10-hour hospital shifts and often disconnect from social media during work weeks. We had a great lunch last Saturday.",
            "alternative": "Their delayed response has nothing to do with our friendship; they are likely exhausted from work. I can check in tomorrow calmly.",
            "init_mood": 3,
            "final_mood": 6,
            "final_intensity": 25,
            "technique": "reattribution",
            "action": "Put my phone aside and focus on reading my book for 30 minutes.",
        },
        {
            "situation": "Woke up feeling sluggish and tired on a rainy Saturday morning.",
            "thought": "I must be disciplined and productive every single day, otherwise I am lazy and wasting my life.",
            "emotions": ("Guilty", 70),
            "distortions": ["should_statements", "labeling", "all_or_nothing"],
            "evidence_for": "I stayed in bed until 10 AM instead of going to the gym at 8 AM.",
            "evidence_against": "I worked 48 hours this week and met all deadlines. Rest and recovery are essential biological needs, not moral failures.",
            "alternative": "Resting on a rainy weekend is restorative and reasonable. I can take a relaxing walk later without guilt.",
            "init_mood": 4,
            "final_mood": 8,
            "final_intensity": 15,
            "technique": "cost_benefit",
            "action": "Make a warm cup of tea and enjoy a slow morning.",
        },
        {
            "situation": "Production server experienced a brief 5-minute memory spike.",
            "thought": "Everything is ruined, the infrastructure is fragile, and I should have anticipated this.",
            "emotions": ("Panicked", 90),
            "distortions": ["catastrophizing", "should_statements", "disqualifying_positive"],
            "evidence_for": "Memory reached 92% utilization for 4 minutes.",
            "evidence_against": "Auto-scaling kicked in immediately, zero client requests were dropped, and latency remained under 15ms. The system worked as designed.",
            "alternative": "The alarm worked and auto-scaling handled the load. This is useful data for tuning thresholds, not a crisis.",
            "init_mood": 2,
            "final_mood": 8,
            "final_intensity": 20,
            "technique": "shades_of_grey",
            "action": "Review memory limit configs and schedule a non-urgent tuning task for Monday.",
        },
    ]

    base_time = datetime.now() - timedelta(days=count)
    inserted = 0

    for i in range(count):
        sample = sample_scenarios[i % len(sample_scenarios)]
        entry_time = (base_time + timedelta(days=i, hours=(i * 3) % 8)).isoformat()
        entry = MoodEntry(
            timestamp=entry_time,
            entry_type="cbt_record",
            initial_mood=sample["init_mood"],
            primary_emotion=sample["emotions"][0],
            emotion_intensity_initial=sample["emotions"][1],
            energy_level=5,
            situation=sample["situation"],
            automatic_thought=sample["thought"],
            belief_initial=sample["emotions"][1],
            distortions=sample["distortions"],
            evidence_for=sample["evidence_for"],
            evidence_against=sample["evidence_against"],
            alternative_thought=sample["alternative"],
            belief_final=80,
            final_mood=sample["final_mood"],
            emotion_intensity_final=sample["final_intensity"],
            action_plan=sample["action"],
            technique_used=sample.get("technique"),
            notes="Sample demo record",
        )
        db.save_entry(entry)
        inserted += 1

    console.print(f"[bold green][+] Inserted {inserted} realistic CBT demo records into database.[/bold green]")
    console.print("[dim]Run 'leahe stats' or 'leahe history' to see the analytics in action![/dim]")

if __name__ == "__main__":
    main()

