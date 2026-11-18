"""Leahe CLI interface for Cognitive Behavioral Therapy Mood Tracking.

Strictly NO emojis. Clean ASCII symbols.
"""

import os
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich import box

from .database import Database
from .views import (
    print_header,
    render_entries_table,
    render_entry_detail,
    render_statistics_dashboard,
    render_distortions_catalog,
    render_burns_methods_catalog,
    render_audit_verification,
    render_actions_table,
    render_procrastination_tasks_table,
    render_weekly_review,
    render_experiments_table,
    render_exposure_ladders,
)
from .session import (
    run_quick_checkin,
    run_cbt_session,
    run_belief_challenge_session,
    run_3column_technique,
    run_das_assessment,
    run_anti_procrastination_predict,
    run_anti_procrastination_complete,
    run_behavioral_experiment_new,
    run_behavioral_experiment_complete,
    run_exposure_ladder_new,
    run_exposure_practice,
    run_decatastrophize_session,
)
from .grounding import (
    run_sos_session,
    run_box_breathing,
    run_478_breathing,
    run_54321_grounding,
)
from .stats import calculate_summary_stats
from .export import export_to_json, export_to_markdown, export_to_yaml
from .models import (
    MoodEntry,
    ActionItem,
    AntiProcrastinationTask,
    DASAssessment,
    BehavioralExperiment,
    ExposureStep,
    ExposureLadder,
)
from .notes import (
    get_default_notes_dir,
    ensure_notes_dir,
    entry_to_markdown,
    markdown_to_entry,
    save_note_file,
    list_note_files,
    convert_notes_to_yaml,
    convert_yaml_to_md,
    sync_notes_with_db,
)

console = Console()

def get_db(ctx: click.Context) -> Database:
    if "db" not in ctx.obj or ctx.obj["db"] is None:
        db_path = ctx.obj.get("db_path")
        notes_dir = ctx.obj.get("notes_dir")
        ctx.obj["db"] = Database(
            db_path=Path(db_path) if db_path else None,
            notes_dir=Path(notes_dir) if notes_dir else None,
        )
    return ctx.obj["db"]

@click.group(invoke_without_command=True)
@click.option("--db", "db_path", type=click.Path(), default=None, help="Custom SQLite database file path.")
@click.option("--notes-dir", type=click.Path(), default=None, help="Custom directory for Markdown notes (default: ~/Notes).")
@click.pass_context
def main(ctx, db_path, notes_dir):
    """Leahe - Cognitive Behavioral Therapy Mood Terminal Utility.

    Track your mood, challenge cognitive distortions, and review therapeutic statistics.
    """
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = Path(db_path) if db_path else None
    ctx.obj["notes_dir"] = Path(notes_dir) if notes_dir else None
    ctx.obj["db"] = None

    if ctx.invoked_subcommand is None:
        db = get_db(ctx)
        from rich.prompt import Prompt
        from rich.panel import Panel

        # Action Commitment Follow-up (Behavioral Activation Loop)
        pending_actions = db.list_actions(is_done=False)
        if pending_actions:
            latest = pending_actions[0]
            date_s = latest.created_at[:10]
            console.print(Panel(
                f"[bold yellow][*] Action Commitment Follow-up:[/bold yellow]\n"
                f"  From CBT Session #{latest.entry_id or '-'}: \"[bold]{latest.action_text}[/bold]\" (set on {date_s})\n\n"
                f"[dim]Did you complete this action? (y = mark done, Enter = continue)[/dim]",
                box=box.ROUNDED,
                border_style="yellow",
            ))
            act_done = Prompt.ask("[bold cyan]Action completed? (y/N)[/bold cyan]", default="n").strip().lower()
            if act_done in ("y", "yes"):
                db.mark_action_done(latest.id, done=True)
                console.print(f"[bold green][+] Great follow-through! Action #{latest.id} marked as completed.[/bold green]\n")

        def _pause_before_menu() -> bool:
            try:
                ans = Prompt.ask("\n[dim]Press Enter to return to main menu (or '0' to exit)[/dim]", default="").strip().lower()
                if ans in ("0", "q", "exit", "quit"):
                    console.print("[dim]Goodbye.[/dim]")
                    return False
                return True
            except (EOFError, KeyboardInterrupt):
                return False

        while True:
            # Interactive grouped menu loop
            print_header("Leahe - CBT & Anxiety Terminal", subtitle="Evidence-based Cognitive Behavioral Therapy & Fear Management")
            console.print("[bold]Select Category:[/bold]")
            console.print("  [1] Thought Records & Restructuring")
            console.print("  [2] Behavioral Experiments & Exposure")
            console.print("  [3] Pleasure Predicting & Action Steps")
            console.print("  [4] Clinical Stats, DAS & Retrospective")
            console.print("  [5] Notes & Sync (Markdown in ~/Notes & YAML)")
            console.print("  [6] Settings & Reference Guides")
            console.print("  [0] Exit\n")

            try:
                cat_choice = Prompt.ask("[bold cyan]Category (1-6)[/bold cyan]", default="0").strip().lower()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Goodbye.[/dim]")
                break

            if cat_choice in ("0", "q", "exit", "quit"):
                console.print("[dim]Goodbye.[/dim]")
                break

            if cat_choice == "1":
                console.print("\n[bold cyan]== Thought Records & Restructuring ==[/bold cyan]")
                console.print("  [1] Quick Mood Check-in (30 seconds)")
                console.print("  [2] Full CBT Thought Record (Guided Session)")
                console.print("  [3] Rapid 3-Column Thought Buster (Burns)")
                console.print("  [4] Decatastrophizing Protocol (Worst / Likely / Coping)")
                console.print("  [5] Acute Distress First-Aid & Grounding (SOS)")
                console.print("  [6] Write Freeform Reflection Note (~/Notes)")
                console.print("  [0] Back\n")
                try:
                    sub = Prompt.ask("[bold cyan]Choice[/bold cyan]", default="0").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    break
                if sub in ("0", "back", "q"):
                    continue
                elif sub == "1":
                    run_quick_checkin(db)
                elif sub == "2":
                    run_cbt_session(db)
                elif sub == "3":
                    run_3column_technique(db)
                elif sub == "4":
                    run_decatastrophize_session(db)
                elif sub == "5":
                    run_sos_session(db)
                elif sub == "6":
                    ctx.invoke(note_cmd)
                if not _pause_before_menu():
                    break

            elif cat_choice == "2":
                console.print("\n[bold cyan]== Behavioral Experiments & Exposure ==[/bold cyan]")
                console.print("  [1] New Behavioral Fear Experiment (Test Catastrophic Prediction)")
                console.print("  [2] Complete Fear Experiment (Record Outcome & Prediction Error)")
                console.print("  [3] View Behavioral Experiments Lab & Disconfirmation Stats")
                console.print("  [4] New Exposure Ladder (Hierarchy 0-100 SUDS)")
                console.print("  [5] Exposure Practice Session (Log Habituation Trial)")
                console.print("  [6] View Exposure Ladders")
                console.print("  [7] Challenge a Belief / Rule (David Burns Lab)")
                console.print("  [0] Back\n")
                try:
                    sub = Prompt.ask("[bold cyan]Choice[/bold cyan]", default="0").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    break
                if sub in ("0", "back", "q"):
                    continue
                elif sub == "1":
                    run_behavioral_experiment_new(db)
                elif sub == "2":
                    run_behavioral_experiment_complete(db)
                elif sub == "3":
                    ctx.invoke(experiment_list_cmd, show_all=True)
                elif sub == "4":
                    run_exposure_ladder_new(db)
                elif sub == "5":
                    run_exposure_practice(db)
                elif sub == "6":
                    ctx.invoke(ladder_list_cmd)
                elif sub == "7":
                    run_belief_challenge_session(db)
                if not _pause_before_menu():
                    break

            elif cat_choice == "3":
                console.print("\n[bold cyan]== Pleasure Predicting & Action Steps ==[/bold cyan]")
                console.print("  [1] Pleasure Predicting Lab (Log Expected Pleasure)")
                console.print("  [2] Complete Activity (Record Actual Pleasure Received)")
                console.print("  [3] View Pleasure Predicting & Anti-Procrastination Sheet")
                console.print("  [4] Record a Win / Credit Item (Positive Data Log)")
                console.print("  [5] Action Steps Tracker")
                console.print("  [0] Back\n")
                try:
                    sub = Prompt.ask("[bold cyan]Choice[/bold cyan]", default="0").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    break
                if sub in ("0", "back", "q"):
                    continue
                elif sub == "1":
                    ctx.invoke(predict_cmd)
                elif sub == "2":
                    ctx.invoke(complete_cmd)
                elif sub == "3":
                    ctx.invoke(tasks_cmd)
                elif sub == "4":
                    ctx.invoke(win_cmd)
                elif sub == "5":
                    ctx.invoke(actions_cmd)
                if not _pause_before_menu():
                    break

            elif cat_choice == "4":
                console.print("\n[bold cyan]== Clinical Stats, DAS & Retrospective ==[/bold cyan]")
                console.print("  [1] View Detailed Statistics & Progress")
                console.print("  [2] Run Pattern Verification Audit")
                console.print("  [3] Weekly CBT Retrospective Review")
                console.print("  [4] Dysfunctional Attitude Scale (DAS Assessment)")
                console.print("  [5] Browse History Log")
                console.print("  [0] Back\n")
                try:
                    sub = Prompt.ask("[bold cyan]Choice[/bold cyan]", default="0").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    break
                if sub in ("0", "back", "q"):
                    continue
                elif sub == "1":
                    ctx.invoke(stats)
                elif sub == "2":
                    ctx.invoke(verify)
                elif sub == "3":
                    ctx.invoke(review_cmd)
                elif sub == "4":
                    run_das_assessment(db)
                elif sub == "5":
                    ctx.invoke(history)
                if not _pause_before_menu():
                    break

            elif cat_choice == "5":
                console.print("\n[bold cyan]== Notes & Sync ==[/bold cyan]")
                console.print("  [1] Browse Notes Folder (~/Notes)")
                console.print("  [2] Convert Notes to YAML")
                console.print("  [3] Sync Notes with Database")
                console.print("  [0] Back\n")
                try:
                    sub = Prompt.ask("[bold cyan]Choice[/bold cyan]", default="0").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    break
                if sub in ("0", "back", "q"):
                    continue
                elif sub == "1":
                    ctx.invoke(notes_cmd)
                elif sub == "2":
                    ctx.invoke(to_yaml_cmd)
                elif sub == "3":
                    ctx.invoke(sync_cmd)
                if not _pause_before_menu():
                    break

            elif cat_choice == "6":
                console.print("\n[bold cyan]== Settings & Reference Guides ==[/bold cyan]")
                console.print("  [1] Configure Systemd Practice Reminders & Notifications")
                console.print("  [2] Cognitive Distortions Guide")
                console.print("  [3] David Burns Restructuring Methods Guide")
                console.print("  [4] Install CLI (leahy / leahe to ~/.local/bin)")
                console.print("  [0] Back\n")
                try:
                    sub = Prompt.ask("[bold cyan]Choice[/bold cyan]", default="0").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    break
                if sub in ("0", "back", "q"):
                    continue
                elif sub == "1":
                    ctx.invoke(systemd_install_cmd)
                elif sub == "2":
                    ctx.invoke(distortions)
                elif sub == "3":
                    ctx.invoke(methods)
                elif sub == "4":
                    ctx.invoke(install_cli_cmd)
                if not _pause_before_menu():
                    break

            else:
                console.print("[dim]Goodbye.[/dim]")
                break

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

@main.command("log")
@click.argument("mood", type=int)
@click.option("--emotion", "-e", default="Neutral", help="Primary emotion name.")
@click.option("--intensity", "-i", type=int, default=50, help="Emotion intensity (0-100%).")
@click.option("--energy", type=int, default=5, help="Energy level (1-10).")
@click.option("--tags", "-t", default=None, help="Comma-separated tags (e.g. work, sleep).")
@click.option("--note", "-n", default=None, help="Brief situation or reflection note.")
@click.pass_context
def log_cmd(ctx, mood, emotion, intensity, energy, tags, note):
    """Fast non-interactive mood check-in (one-liner)."""
    db: Database = get_db(ctx)
    mood = max(1, min(10, mood))
    intensity = max(0, min(100, intensity))
    energy = max(1, min(10, energy)) if energy is not None else None
    tag_list = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()] if tags else []

    entry = MoodEntry(
        entry_type="quick",
        initial_mood=mood,
        primary_emotion=emotion,
        emotion_intensity_initial=intensity,
        energy_level=energy,
        situation=note,
        tags=tag_list,
        notes=note,
    )
    entry_id = db.save_entry(entry)
    console.print(f"[bold green][+] Quick log #{entry_id} saved:[/bold green] Mood {mood}/10 | {emotion} ({intensity}%)" + (f" | #{', #'.join(tag_list)}" if tag_list else ""))

@main.command("3col")
@click.argument("thought", required=False, default=None)
@click.pass_context
def three_col_alias(ctx, thought):
    """Rapid Burns 3-Column Thought Buster (Column 1: NAT | 2: Distortions | 3: Rational Response)."""
    db: Database = get_db(ctx)
    run_3column_technique(db, initial_thought=thought)

@main.command("three-column")
@click.argument("thought", required=False, default=None)
@click.pass_context
def three_column_cmd(ctx, thought):
    """Alias for '3col' - run the Burns Triple-Column Thought Buster."""
    db: Database = get_db(ctx)
    run_3column_technique(db, initial_thought=thought)

@main.command("das")
@click.option("--history", is_flag=True, help="View previous DAS assessment scores.")
@click.pass_context
def das_cmd(ctx, history):
    """Burns' Dysfunctional Attitude Scale (DAS) assessment."""
    db: Database = get_db(ctx)
    if history:
        assessments = db.list_das()
        if not assessments:
            console.print("[yellow][*] No previous DAS assessments found. Take one with 'leahe das'.[/yellow]")
            return
        from rich.table import Table
        t = Table(title="DAS Assessment History", box=box.ROUNDED, header_style="bold magenta")
        t.add_column("ID", width=4)
        t.add_column("Date", width=12)
        t.add_column("Total Score", justify="center", width=14)
        t.add_column("Top Vulnerabilities", justify="left")
        for a in assessments:
            t.add_row(str(a.id), a.timestamp[:10], f"{a.total_score}/70", a.top_vulnerabilities)
        console.print(t)
    else:
        run_das_assessment(db)

@main.command("predict")
@click.argument("task_name", required=False, default=None)
@click.option("--pleasure", "-p", type=int, default=None, help="Expected pleasure / joy (0-100%).")
@click.option("--difficulty", "-d", type=int, default=None, help="Expected difficulty (0-100%).")
@click.option("--notes", "-n", default=None, help="Notes or subtasks.")
@click.pass_context
def predict_cmd(ctx, task_name, pleasure, difficulty, notes):
    """Log an activity to the Burns Pleasure-Predicting & Anti-Procrastination Sheet."""
    db: Database = get_db(ctx)
    run_anti_procrastination_predict(
        db,
        task_name=task_name,
        predicted_pleasure=pleasure,
        predicted_difficulty=difficulty,
        notes=notes,
    )

@main.command("complete")
@click.argument("task_id", type=int, required=False, default=None)
@click.option("--pleasure", "-p", type=int, default=None, help="Actual pleasure / satisfaction experienced (0-100%).")
@click.option("--difficulty", "-d", type=int, default=None, help="Actual difficulty experienced (0-100%).")
@click.option("--notes", "-n", default=None, help="Reflection or what you learned.")
@click.pass_context
def complete_cmd(ctx, task_id, pleasure, difficulty, notes):
    """Record actual pleasure & difficulty for an activity to bust cognitive dread."""
    db: Database = get_db(ctx)
    run_anti_procrastination_complete(
        db,
        task_id=task_id,
        actual_pleasure=pleasure,
        actual_difficulty=difficulty,
        notes=notes,
    )

@main.command("complete-task")
@click.argument("task_id", type=int, required=False, default=None)
@click.option("--pleasure", "-p", type=int, default=None, help="Actual pleasure / satisfaction experienced (0-100%).")
@click.option("--difficulty", "-d", type=int, default=None, help="Actual difficulty experienced (0-100%).")
@click.option("--notes", "-n", default=None, help="Reflection or what you learned.")
@click.pass_context
def complete_task_alias(ctx, task_id, pleasure, difficulty, notes):
    """Alias for 'complete' - record actual pleasure and difficulty."""
    ctx.invoke(complete_cmd, task_id=task_id, pleasure=pleasure, difficulty=difficulty, notes=notes)

@main.command("tasks")
@click.option("--all", "show_all", is_flag=True, help="Include completed activities.")
@click.pass_context
def tasks_cmd(ctx, show_all):
    """List activities on the Burns Pleasure-Predicting & Anti-Procrastination Sheet."""
    db: Database = get_db(ctx)
    status = None if show_all else "pending"
    tasks = db.list_tasks(status=status)
    render_procrastination_tasks_table(tasks)

@main.command("notify")
@click.option("--title", "-t", default=None, help="Custom notification title.")
@click.option("--message", "-m", default=None, help="Custom notification message.")
@click.option("--test", is_flag=True, help="Send a test notification.")
@click.pass_context
def notify_cmd(ctx, title, message, test):
    """Send a desktop practice reminder or check-in notification."""
    db: Database = get_db(ctx)
    if test:
        title = "Leahe CBT: Notification Test"
        message = "Desktop notifications are working! Take a moment for your mental fitness."
    elif not title or not message:
        from .notifications import get_smart_reminder_content
        title, message = get_smart_reminder_content(db)

    from .notifications import send_notification
    success = send_notification(title, message)
    if success:
        console.print(f"[bold green][+] Notification sent successfully:[/bold green] \"{title}\"")
    else:
        console.print("[yellow][!] Could not send notification via notify-send.[/yellow]")
        console.print(f"  Title: {title}")
        console.print(f"  Message: {message}")
        console.print("[dim]Ensure 'notify-send' is installed (e.g. libnotify package on Arch/Debian/Fedora).[/dim]")

@main.group("systemd", invoke_without_command=True)
@click.pass_context
def systemd_group(ctx):
    """Manage systemd user service and timer for automated practice notifications."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(systemd_status_cmd)

@systemd_group.command("install")
@click.option("--schedule", "-s", default="*-*-* 10,14,18,21:00:00", help="OnCalendar schedule expression.")
@click.option("--every", "-e", default=None, help="Repeat every N hours/minutes (e.g. '3h', '4h').")
@click.pass_context
def systemd_install_cmd(ctx, schedule, every):
    """Install and enable systemd user service & timer for CBT practice reminders."""
    from .notifications import install_systemd_timer
    if every:
        schedule = f"*:0/{every.rstrip('m')}" if every.endswith("m") else f"0/{every.rstrip('h')}:00:00"

    res = install_systemd_timer(schedule=schedule)
    console.print("[bold green][+] Systemd user timer files created:[/bold green]")
    console.print(f"  Service: {res['service_path']}")
    console.print(f"  Timer:   {res['timer_path']}")
    console.print(f"  Schedule: {schedule}")

    if res["enabled"]:
        console.print("[bold green][+] Systemd timer successfully enabled and started![/bold green]")
        console.print("[dim]Your system will notify you with practice reminders automatically.[/dim]")
    else:
        console.print("\n[yellow][*] Timer files written. To activate in your graphical session, run:[/yellow]")
        console.print("  systemctl --user daemon-reload")
        console.print("  systemctl --user enable --now leahy-reminder.timer")
        if res.get("error"):
            console.print(f"[dim]Note: {res['error']}[/dim]")

@systemd_group.command("status")
def systemd_status_cmd():
    """Check status of the systemd user timer."""
    from .notifications import get_systemd_timer_status
    st = get_systemd_timer_status()
    console.print("[bold]Systemd User Timer Status:[/bold]")
    if st["installed"]:
        console.print(f"  Files:    [green]Installed[/green] ({st['timer_file']})")
        console.print(f"  Schedule: [cyan]{st['schedule']}[/cyan]")
        if st["active"]:
            console.print("  Status:   [bold green]ACTIVE (Running)[/bold green]")
        else:
            console.print("  Status:   [yellow]INACTIVE (Run 'systemctl --user enable --now leahy-reminder.timer')[/yellow]")
    else:
        console.print("  Files:    [yellow]Not installed[/yellow]")
        console.print("[dim]Install with 'leahy systemd install' to get automated reminders.[/dim]")

@systemd_group.command("uninstall")
def systemd_uninstall_cmd():
    """Disable and remove systemd timer and service files."""
    from .notifications import uninstall_systemd_timer
    res = uninstall_systemd_timer()
    console.print("[bold green][+] Systemd user timer disabled and removed.[/bold green]")

@main.command("actions")
@click.option("--done", "done_id", type=int, default=None, help="Mark action item ID as completed.")
@click.option("--all", "show_all", is_flag=True, help="Show all actions including completed.")
@click.pass_context
def actions_cmd(ctx, done_id, show_all):
    """Track and manage behavioral action steps formulated in CBT sessions."""
    db: Database = get_db(ctx)
    if done_id is not None:
        success = db.mark_action_done(done_id, done=True)
        if success:
            console.print(f"[bold green][+] Action #{done_id} marked as completed![/bold green]")
        else:
            console.print(f"[red][!] Action #{done_id} not found.[/red]")
        return

    is_done_filter = None if show_all else False
    actions = db.list_actions(is_done=is_done_filter)
    render_actions_table(actions)

@main.command("review")
@click.pass_context
def review_cmd(ctx):
    """Generate weekly CBT clinical retrospective and progress digest."""
    db: Database = get_db(ctx)
    entries = db.get_all_entries()
    actions = db.list_actions()
    stats_data = calculate_summary_stats(entries)
    render_weekly_review(entries, actions, stats_data)

@main.command("backup")
@click.option("--output", "-o", "out_file", type=click.Path(), required=True, help="Destination JSON backup file.")
@click.pass_context
def backup_cmd(ctx, out_file):
    """Create a complete non-encrypted JSON backup of all database tables."""
    db: Database = get_db(ctx)
    data = db.backup_all()
    p = Path(out_file)
    import json
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"[bold green][+] Full backup created successfully:[/bold green] {p.resolve()}")

@main.command("restore")
@click.option("--input", "-i", "in_file", type=click.Path(exists=True), required=True, help="Source JSON backup file.")
@click.pass_context
def restore_cmd(ctx, in_file):
    """Restore or merge records from a JSON backup file."""
    db: Database = get_db(ctx)
    p = Path(in_file)
    import json
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        e_c, a_c, t_c, d_c = db.restore_all(data)
        console.print(f"[bold green][+] Restore completed:[/bold green] {e_c} entries, {a_c} actions, {t_c} tasks, {d_c} DAS assessments restored.")
    except Exception as ex:
        console.print(f"[red][!] Failed to restore backup: {ex}[/red]")

@main.command("stats")
@click.pass_context
def stats(ctx):
    """Display comprehensive CBT statistics, distortion frequencies, and charts."""
    db: Database = get_db(ctx)
    entries = db.get_all_entries()
    summary = calculate_summary_stats(entries)
    render_statistics_dashboard(summary, entries)

    # Render behavioral experiments statistics if any exist
    experiments = db.list_experiments()
    if experiments:
        render_experiments_table(experiments)

@main.command("decatastrophize")
@click.pass_context
def decatastrophize_cmd(ctx):
    """Run a Decatastrophizing mini-session (Worst case / Best case / Likely case / Coping plan)."""
    db: Database = get_db(ctx)
    run_decatastrophize_session(db)

@main.command("sos")
@click.pass_context
def sos_cmd(ctx):
    """Acute distress first-aid & nervous system stabilization (breathing & grounding)."""
    db: Database = get_db(ctx)
    run_sos_session(db)

@main.command("breathe")
@click.option("--relax", is_flag=True, help="Use 4-7-8 Relaxation Breath instead of Box Breathing.")
@click.option("--cycles", "-c", type=int, default=4, help="Number of breath cycles.")
def breathe_cmd(relax, cycles):
    """Run interactive breathing pacing to downregulate sympathetic stress."""
    if relax:
        run_478_breathing(cycles=cycles)
    else:
        run_box_breathing(cycles=cycles)

@main.command("ground")
def ground_cmd():
    """Run the 5-4-3-2-1 Sensory Grounding protocol for acute panic and racing thoughts."""
    run_54321_grounding()

@main.command("win")
@click.argument("text", required=False, default=None)
@click.option("--mood", "-m", type=int, default=7, help="Current mood (1-10).")
@click.option("--tags", "-t", default="win,credit", help="Tags for the win.")
@click.pass_context
def win_cmd(ctx, text, mood, tags):
    """Record an accomplishment, coping victory, or positive evidence (Positive Data Log)."""
    db: Database = get_db(ctx)
    if not text:
        from rich.prompt import Prompt
        print_header("Positive Data Log (Credit List)", subtitle="Acknowledge accomplishments, coping resilience, and positive evidence")
        console.print("[dim]Burns & Padesky CBT Principle: Anxiety and depression filter out positive evidence.[/dim]")
        console.print("[dim]Deliberately recording wins trains your brain to notice capability, resilience, and safety.[/dim]\n")
        text = Prompt.ask("[bold cyan]What win, constructive action, or positive moment happened?[/bold cyan]").strip()
        while not text:
            text = Prompt.ask("[bold cyan]Please describe the win or positive fact[/bold cyan]").strip()

    tag_list = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()]
    entry = MoodEntry(
        entry_type="credit",
        initial_mood=max(1, min(10, mood)),
        primary_emotion="Accomplished",
        emotion_intensity_initial=75,
        situation=text,
        notes="Positive Data Log / Credit Item",
        tags=tag_list,
    )
    entry_id = db.save_entry(entry)
    console.print(f"\n[bold green][+] Win recorded in Positive Data Log! (ID #{entry_id})[/bold green]")
    console.print(f"    \"{text}\"")
    console.print("[dim]Saved to ~/Notes and database as a credit item.[/dim]\n")

@main.group("experiment", invoke_without_command=True)
@click.pass_context
def experiment_group(ctx):
    """Behavioral Experiments Lab: empirically test catastrophic fears."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(experiment_list_cmd, show_all=True)

@experiment_group.command("new")
@click.argument("title", required=False, default=None)
@click.option("--fear", "-f", default=None, help="Feared catastrophe or negative prediction.")
@click.option("--belief", "-b", type=int, default=None, help="Belief in prediction (0-100%).")
@click.option("--plan", "-p", default=None, help="Action plan to test the fear.")
@click.pass_context
def experiment_new_cmd(ctx, title, fear, belief, plan):
    """Design and record a new behavioral fear experiment."""
    db: Database = get_db(ctx)
    run_behavioral_experiment_new(
        db,
        title=title,
        fear_prediction=fear,
        predicted_belief=belief,
        experiment_plan=plan,
    )

@experiment_group.command("complete")
@click.argument("exp_id", type=int, required=False, default=None)
@click.option("--outcome", "-o", default=None, help="What actually happened.")
@click.option("--realized/--not-realized", default=None, help="Did the feared catastrophe happen?")
@click.option("--severity", "-s", type=int, default=None, help="Actual severity (0-100%).")
@click.option("--conclusion", "-c", default=None, help="Therapeutic conclusion / lesson learned.")
@click.pass_context
def experiment_complete_cmd(ctx, exp_id, outcome, realized, severity, conclusion):
    """Record actual outcome and calculate fear prediction error."""
    db: Database = get_db(ctx)
    run_behavioral_experiment_complete(
        db,
        experiment_id=exp_id,
        actual_outcome=outcome,
        fear_realized=realized,
        actual_severity=severity,
        conclusion=conclusion,
    )

@experiment_group.command("list")
@click.option("--all", "show_all", is_flag=True, help="Include completed experiments.")
@click.pass_context
def experiment_list_cmd(ctx, show_all):
    """List behavioral fear experiments and disconfirmation stats."""
    db: Database = get_db(ctx)
    status = None if show_all else "pending"
    exps = db.list_experiments(status=status)
    render_experiments_table(exps)

@experiment_group.command("delete")
@click.argument("exp_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Confirm deletion.")
@click.pass_context
def experiment_delete_cmd(ctx, exp_id, yes):
    """Delete a behavioral experiment by ID."""
    db: Database = get_db(ctx)
    if not yes:
        if not click.confirm(f"Are you sure you want to delete experiment #{exp_id}?"):
            console.print("[dim]Cancelled.[/dim]")
            return
    if db.delete_experiment(exp_id):
        console.print(f"[bold green][+] Experiment #{exp_id} deleted.[/bold green]")
    else:
        console.print(f"[red][!] Experiment #{exp_id} not found.[/red]")

@main.group("ladder", invoke_without_command=True)
@click.pass_context
def ladder_group(ctx):
    """Exposure Hierarchy & Fear Ladder for systematic desensitization."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(ladder_list_cmd)

@ladder_group.command("new")
@click.argument("theme", required=False, default=None)
@click.option("--notes", "-n", default=None, help="Notes or context for fear hierarchy.")
@click.pass_context
def ladder_new_cmd(ctx, theme, notes):
    """Create a new Exposure Hierarchy / Fear Ladder."""
    db: Database = get_db(ctx)
    run_exposure_ladder_new(db, theme=theme, notes=notes)

@ladder_group.command("add-step")
@click.argument("ladder_id", type=int)
@click.argument("description")
@click.option("--suds", "-s", type=int, default=50, help="Expected Subjective Units of Distress (0-100).")
@click.pass_context
def ladder_add_step_cmd(ctx, ladder_id, description, suds):
    """Add an exposure step to an existing fear hierarchy."""
    db: Database = get_db(ctx)
    ladder = db.get_ladder(ladder_id)
    if not ladder:
        console.print(f"[red][!] Fear hierarchy #{ladder_id} not found.[/red]")
        return
    step = ExposureStep(
        ladder_id=ladder_id,
        step_order=len(ladder.steps) + 1,
        description=description,
        target_suds=max(0, min(100, suds)),
    )
    step_id = db.save_exposure_step(step)
    console.print(f"[bold green][+] Step #{step_id} added to ladder #{ladder_id}:[/bold green] {description} (SUDS: {step.target_suds})")

@ladder_group.command("practice")
@click.argument("step_id", type=int, required=False, default=None)
@click.option("--pre", type=int, default=None, help="Pre-exposure distress rating (0-100).")
@click.option("--post", type=int, default=None, help="Post-exposure distress rating (0-100).")
@click.option("--notes", default=None, help="Exposure session reflection.")
@click.option("--mastered", is_flag=True, help="Mark this step as mastered.")
@click.pass_context
def ladder_practice_cmd(ctx, step_id, pre, post, notes, mastered):
    """Log an exposure practice trial to measure habituation."""
    db: Database = get_db(ctx)
    run_exposure_practice(
        db,
        step_id=step_id,
        pre_suds=pre,
        post_suds=post,
        notes=notes,
        mastered=mastered,
    )

@ladder_group.command("list")
@click.pass_context
def ladder_list_cmd(ctx):
    """List all exposure hierarchies and fear ladders."""
    db: Database = get_db(ctx)
    ladders = db.list_ladders()
    render_exposure_ladders(ladders)

@ladder_group.command("show")
@click.argument("ladder_id", type=int)
@click.pass_context
def ladder_show_cmd(ctx, ladder_id):
    """Show a specific fear ladder with all its steps."""
    db: Database = get_db(ctx)
    ladder = db.get_ladder(ladder_id)
    if not ladder:
        console.print(f"[red][!] Ladder #{ladder_id} not found.[/red]")
        return
    render_exposure_ladders([ladder])

@ladder_group.command("delete")
@click.argument("ladder_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Confirm deletion.")
@click.pass_context
def ladder_delete_cmd(ctx, ladder_id, yes):
    """Delete an entire fear ladder and its steps."""
    db: Database = get_db(ctx)
    if not yes:
        if not click.confirm(f"Are you sure you want to delete fear hierarchy #{ladder_id}?"):
            console.print("[dim]Cancelled.[/dim]")
            return
    if db.delete_ladder(ladder_id):
        console.print(f"[bold green][+] Ladder #{ladder_id} deleted.[/bold green]")
    else:
        console.print(f"[red][!] Ladder #{ladder_id} not found.[/red]")

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
@click.option("--format", "-f", "fmt", type=click.Choice(["markdown", "md", "json", "yaml", "yml"]), default="markdown", help="Export format.")
@click.option("--output", "-o", "out_path", type=click.Path(), required=True, help="Destination file path.")
@click.pass_context
def export_cmd(ctx, fmt, out_path):
    """Export all mood records to Markdown, YAML, or JSON."""
    db: Database = get_db(ctx)
    entries = db.get_all_entries()
    if not entries:
        console.print("[yellow][*] No records found to export.[/yellow]")
        return

    path = Path(out_path)
    if fmt in ["markdown", "md"]:
        export_to_markdown(entries, path)
        console.print(f"[bold green][+] Exported {len(entries)} records to Markdown:[/bold green] {path.resolve()}")
    elif fmt in ["yaml", "yml"]:
        export_to_yaml(entries, path)
        console.print(f"[bold green][+] Exported {len(entries)} records to YAML:[/bold green] {path.resolve()}")
    else:
        export_to_json(entries, path)
        console.print(f"[bold green][+] Exported {len(entries)} records to JSON:[/bold green] {path.resolve()}")

@main.command("note")
@click.argument("title", required=False, default=None)
@click.option("--mood", "-m", type=int, default=None, help="Mood rating (1-10).")
@click.option("--emotion", "-e", default=None, help="Primary emotion name.")
@click.option("--intensity", "-i", type=int, default=None, help="Emotion intensity (0-100%).")
@click.option("--energy", type=int, default=None, help="Energy level (1-10).")
@click.option("--tags", "-t", default=None, help="Comma-separated tags (e.g. habit, reflection).")
@click.option("--content", "-c", default=None, help="Note content / reflection text.")
@click.option("--edit", is_flag=True, help="Open default editor ($EDITOR) with Markdown/YAML template.")
@click.pass_context
def note_cmd(ctx, title, mood, emotion, intensity, energy, tags, content, edit):
    """Write a reflection note stored in ~/Notes as Markdown with YAML frontmatter."""
    db: Database = get_db(ctx)
    notes_dir = Path(ctx.obj.get("notes_dir")) if ctx.obj.get("notes_dir") else get_default_notes_dir()

    if edit:
        import tempfile
        import subprocess
        initial_mood = mood if mood is not None else 5
        initial_emo = emotion or "Neutral"
        initial_intensity = intensity if intensity is not None else 50
        initial_energy = energy if energy is not None else 5
        tag_list = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()] if tags else []

        draft_entry = MoodEntry(
            entry_type="note",
            initial_mood=initial_mood,
            primary_emotion=initial_emo,
            emotion_intensity_initial=initial_intensity,
            energy_level=initial_energy,
            situation=title or "Note reflection",
            tags=tag_list,
            notes=content or "Write your thoughts here...",
        )
        template_text = entry_to_markdown(draft_entry)

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as tf:
            tf.write(template_text)
            temp_path = Path(tf.name)

        editor = os.getenv("EDITOR") or "nano"
        try:
            subprocess.run([editor, str(temp_path)], check=True)
            edited_text = temp_path.read_text(encoding="utf-8")
            entry = markdown_to_entry(edited_text)
            entry.entry_type = "note"
            entry_id = db.save_entry(entry)
            entry.id = entry_id
            saved_file = save_note_file(entry, notes_dir)
            console.print(f"[bold green][+] Note #{entry_id} saved successfully:[/bold green] {saved_file.resolve()}")
        finally:
            if temp_path.exists():
                temp_path.unlink()
        return

    # Non-interactive CLI flags provided
    if title or content or (mood is not None):
        mood_val = max(1, min(10, mood)) if mood is not None else 5
        intensity_val = max(0, min(100, intensity)) if intensity is not None else 50
        energy_val = max(1, min(10, energy)) if energy is not None else 5
        tag_list = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()] if tags else []

        entry = MoodEntry(
            entry_type="note",
            initial_mood=mood_val,
            primary_emotion=emotion or "Neutral",
            emotion_intensity_initial=intensity_val,
            energy_level=energy_val,
            situation=title or "Freeform Note",
            notes=content or title,
            tags=tag_list,
        )
        entry_id = db.save_entry(entry)
        entry.id = entry_id
        saved_file = save_note_file(entry, notes_dir)
        console.print(f"[bold green][+] Note #{entry_id} saved:[/bold green] {saved_file.resolve()}")
        return

    # Interactive prompt mode
    from rich.prompt import Prompt
    print_header("Leahe - New Markdown Note", subtitle="Store your reflections in ~/Notes with YAML frontmatter")

    note_title = Prompt.ask("[bold cyan]Note title / Situation[/bold cyan]", default="General Reflection").strip()
    mood_str = Prompt.ask("[bold cyan]Current Mood (1-10)[/bold cyan]", default="5").strip() or "5"
    try:
        mood_val = max(1, min(10, int(mood_str)))
    except ValueError:
        mood_val = 5

    emo_val = Prompt.ask("[bold cyan]Primary Emotion[/bold cyan]", default="Neutral").strip()
    intensity_str = Prompt.ask("[bold cyan]Emotion Intensity (0-100%)[/bold cyan]", default="50").strip() or "50"
    try:
        intensity_val = max(0, min(100, int(intensity_str)))
    except ValueError:
        intensity_val = 50

    energy_str = Prompt.ask("[bold cyan]Energy Level (1-10)[/bold cyan]", default="5").strip() or "5"
    try:
        energy_val = max(1, min(10, int(energy_str)))
    except ValueError:
        energy_val = 5

    raw_tags = Prompt.ask("[bold cyan]Tags (comma-separated, e.g. habit, ideas)[/bold cyan]", default="").strip()
    tag_list = [t.strip().lstrip("#") for t in raw_tags.split(",") if t.strip()]

    console.print("[dim]Enter your reflection / note text below (press Enter to finish):[/dim]")
    note_body = Prompt.ask("[bold cyan]Content[/bold cyan]").strip()

    entry = MoodEntry(
        entry_type="note",
        initial_mood=mood_val,
        primary_emotion=emo_val,
        emotion_intensity_initial=intensity_val,
        energy_level=energy_val,
        situation=note_title,
        notes=note_body,
        tags=tag_list,
    )
    entry_id = db.save_entry(entry)
    entry.id = entry_id
    saved_file = save_note_file(entry, notes_dir)
    console.print(f"\n[bold green][+] Note #{entry_id} saved successfully:[/bold green] {saved_file.resolve()}")
    console.print(f"[dim]Stored in {notes_dir} as Markdown with YAML frontmatter.[/dim]")

@main.command("to-yaml")
@click.argument("source", required=False, default=None)
@click.option("--output", "-o", "out_path", type=click.Path(), default=None, help="Output YAML file or destination directory.")
@click.option("--single", "-s", is_flag=True, help="Combine all converted notes into a single YAML file.")
@click.pass_context
def to_yaml_cmd(ctx, source, out_path, single):
    """Convert Markdown notes in ~/Notes (or a custom path) into convenient YAML."""
    notes_dir = ctx.obj.get("notes_dir") or get_default_notes_dir()
    src = Path(source) if source else notes_dir

    if not src.exists():
        console.print(f"[red][!] Source path not found:[/red] {src}")
        return

    dest = Path(out_path) if out_path else None
    results = convert_notes_to_yaml(src, output_path=dest, single_file=single)

    if not results:
        console.print(f"[yellow][*] No Markdown (.md) note files found in:[/yellow] {src}")
        return

    if len(results) == 1 and (single or (dest and dest.suffix.lower() in [".yaml", ".yml"])):
        console.print(f"[bold green][+] Successfully converted notes into single YAML file:[/bold green] {results[0].resolve()}")
    else:
        console.print(f"[bold green][+] Successfully converted {len(results)} note(s) to YAML:[/bold green]")
        for r in results[:10]:
            console.print(f"  [+] {r.name}")
        if len(results) > 10:
            console.print(f"  [dim]... and {len(results) - 10} more files[/dim]")

@main.command("to-md")
@click.argument("source", type=click.Path(exists=True), required=True)
@click.option("--output", "-o", "out_path", type=click.Path(), default=None, help="Destination directory for Markdown notes.")
@click.pass_context
def to_md_cmd(ctx, source, out_path):
    """Convert a YAML file or directory of YAML files into Markdown notes with YAML frontmatter."""
    src = Path(source)
    notes_dir = Path(out_path) if out_path else (ctx.obj.get("notes_dir") or get_default_notes_dir())
    notes_dir.mkdir(parents=True, exist_ok=True)

    if src.is_file():
        saved = convert_yaml_to_md(src, notes_dir)
        console.print(f"[bold green][+] Converted YAML to Markdown note:[/bold green] {saved.resolve()}")
    else:
        yaml_files = sorted(src.glob("*.yaml")) + sorted(src.glob("*.yml"))
        count = 0
        for yf in yaml_files:
            try:
                convert_yaml_to_md(yf, notes_dir)
                count += 1
            except Exception:
                pass
        console.print(f"[bold green][+] Converted {count} YAML file(s) to Markdown notes in:[/bold green] {notes_dir.resolve()}")

@main.command("sync")
@click.option("--dir", "notes_dir", type=click.Path(), default=None, help="Custom notes directory.")
@click.pass_context
def sync_cmd(ctx, notes_dir):
    """Sync notes in ~/Notes with the SQLite database (bidirectional)."""
    db: Database = get_db(ctx)
    folder = Path(notes_dir) if notes_dir else (ctx.obj.get("notes_dir") or get_default_notes_dir())
    stats = sync_notes_with_db(db, folder)
    console.print(f"[bold green][+] Sync completed with {folder.resolve()}:[/bold green]")
    console.print(f"  [+] Exported to ~/Notes : {stats['exported']} notes")
    console.print(f"  [+] Imported from files : {stats['imported']} notes")
    console.print(f"  [*] Updated in DB       : {stats['updated']} notes")

@main.command("notes")
@click.option("--dir", "notes_dir", type=click.Path(), default=None, help="Custom notes directory.")
@click.option("--limit", "-n", default=25, help="Maximum number of notes to display.")
@click.pass_context
def notes_cmd(ctx, notes_dir, limit):
    """List markdown notes stored in ~/Notes."""
    folder = Path(notes_dir) if notes_dir else (ctx.obj.get("notes_dir") or get_default_notes_dir())
    if not folder.exists():
        console.print(f"[yellow][*] Notes directory does not exist yet: {folder.resolve()}[/yellow]")
        console.print("[dim]Create a note with 'leahe note' to get started.[/dim]")
        return

    notes_list = list_note_files(folder)
    if not notes_list:
        console.print(f"[yellow][*] No Markdown notes found in {folder.resolve()}[/yellow]")
        console.print("[dim]Create your first note with 'leahe note' or 'leahe check'.[/dim]")
        return

    from rich.table import Table
    from rich import box
    t = Table(title=f"Markdown Notes in {folder.resolve()} (Total: {len(notes_list)})", box=box.ROUNDED, header_style="bold cyan")
    t.add_column("Filename", justify="left", style="cyan")
    t.add_column("Type", justify="center", width=8)
    t.add_column("Mood", justify="center", width=6)
    t.add_column("Emotion", justify="left", width=12)
    t.add_column("Situation / Title", justify="left")

    for file_path, fm in notes_list[:limit]:
        ntype = str(fm.get("type") or "note")
        mood = f"{fm.get('initial_mood')}/10" if fm.get("initial_mood") is not None else "-"
        emo = f"{fm.get('primary_emotion', '-')}"
        situation = str(fm.get("situation") or file_path.stem)
        t.add_row(file_path.name, ntype, mood, emo, situation)

    console.print(t)
    if len(notes_list) > limit:
        console.print(f"[dim]... showing {limit} of {len(notes_list)} notes. Use --limit to see more.[/dim]")

@main.command("install-cli")
@click.option("--dest", type=click.Path(), default=None, help="Destination directory (default: ~/.local/bin).")
def install_cli_cmd(dest):
    """Install 'leahy', 'leahe', and 'mood' to ~/.local/bin for system-wide terminal access."""
    bin_dir = Path(dest) if dest else (Path.home() / ".local" / "bin")
    bin_dir.mkdir(parents=True, exist_ok=True)

    project_root = Path(__file__).resolve().parent.parent.parent
    scripts = ["leahy", "leahe", "mood"]
    linked = []
    failed = []

    for s in scripts:
        src_file = project_root / s
        if not src_file.exists():
            continue
        try:
            st = src_file.stat()
            src_file.chmod(st.st_mode | 0o755)
        except Exception:
            pass

        target_link = bin_dir / s
        try:
            if target_link.is_symlink() or target_link.exists():
                target_link.unlink()
            target_link.symlink_to(src_file)
            linked.append(s)
        except Exception as ex:
            failed.append((s, str(ex)))

    if linked:
        console.print(f"[bold green][+] Successfully installed CLI commands into {bin_dir.resolve()}:[/bold green]")
        for s in linked:
            console.print(f"  [+] {s} -> {(bin_dir / s).resolve()}")

        path_env = os.getenv("PATH", "")
        if str(bin_dir) in path_env or str(bin_dir.resolve()) in path_env:
            console.print("\n[bold green][+] Verified: Directory is in your PATH![/bold green]")
            console.print("[dim]You can now run 'leahy' or 'leahe' from any terminal directory.[/dim]")
        else:
            console.print("\n[yellow][!] Notice: Destination is not in your PATH.[/yellow]")
            console.print("[dim]Add the following line to your ~/.bashrc or ~/.zshrc:[/dim]")
            console.print(f'  export PATH="{bin_dir.resolve()}:$PATH"')
    if failed:
        for s, err in failed:
            console.print(f"[red][!] Failed to link {s}: {err}[/red]")

# Aliases
main.add_command(note_cmd, name="write")
main.add_command(to_yaml_cmd, name="yaml")
main.add_command(to_yaml_cmd, name="md2yaml")
main.add_command(to_md_cmd, name="yaml2md")
main.add_command(sync_cmd, name="sync-notes")
main.add_command(notes_cmd, name="list-notes")
main.add_command(notes_cmd, name="ls-notes")
main.add_command(install_cli_cmd, name="install")
main.add_command(predict_cmd, name="pleasure")
main.add_command(complete_cmd, name="actual")
main.add_command(tasks_cmd, name="pleasure-sheet")
main.add_command(notify_cmd, name="remind")
main.add_command(decatastrophize_cmd, name="decat")
main.add_command(experiment_group, name="exp")
main.add_command(experiment_group, name="test-fear")
main.add_command(ladder_group, name="exposure")
main.add_command(win_cmd, name="credit")
main.add_command(sos_cmd, name="first-aid")
main.add_command(breathe_cmd, name="breath")

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

