"""Interactive Terminal Dashboard (TUI) for Leahe.

Strictly NO emojis. Clean ASCII borders and typographic layouts using Rich.
Provides a unified live dashboard for quick check-ins, CBT restructuring,
box breathing, and monitoring therapeutic streaks.
"""

import sys
import time
from typing import Optional
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich import box

from .database import Database
from .stats import calculate_summary_stats
from .session import run_quick_checkin, run_cbt_session
from .grounding import run_box_breathing

console = Console()

def generate_dashboard_layout(db: Database) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=2),
    )

    # Header
    entries_count = db.count_entries()
    header_text = Text()
    header_text.append("[LEAHE] ", style="bold cyan")
    header_text.append("CBT Mind & Mood Terminal Dashboard", style="bold white")
    header_text.append(f" | Total Sessions: {entries_count}", style="dim")
    layout["header"].update(Panel(header_text, box=box.ROUNDED, border_style="cyan"))

    # Left: Stats & Metrics
    all_entries = db.get_all_entries()
    stats = calculate_summary_stats(all_entries)

    stats_table = Table(box=box.SIMPLE, show_header=False, expand=True)
    stats_table.add_column("Metric", style="dim")
    stats_table.add_column("Value", style="bold")

    avg_mood = f"{stats.get('avg_mood', 0):.1f}/10" if stats.get("avg_mood") else "--"
    stats_table.add_row("[*] Avg Mood", avg_mood)

    streak = f"{stats.get('current_streak', 0)} days"
    stats_table.add_row("[+] Active Streak", streak)

    cbt_count = str(stats.get("cbt_entries", 0))
    stats_table.add_row("[#] CBT Sessions", cbt_count)

    relief = f"-{stats.get('avg_relief_percent', 0):.0f}%" if stats.get("avg_relief_percent") else "--"
    stats_table.add_row("[o] Distress Relief", f"[green]{relief}[/green]" if relief != "--" else "--")

    exp_list = db.list_experiments()
    active_exps = [e for e in exp_list if not e.is_completed]
    stats_table.add_row("[!] Active Experiments", str(len(active_exps)))

    left_panel = Panel(
        stats_table,
        title="[bold cyan]Analytics Summary[/bold cyan]",
        box=box.ROUNDED,
        border_style="dim",
    )
    layout["left"].update(left_panel)

    # Right: Recent Sessions Log
    recent = db.list_entries(limit=8)
    history_table = Table(box=box.SIMPLE, expand=True, show_lines=False)
    history_table.add_column("Time", style="dim", width=12)
    history_table.add_column("Type", width=6)
    history_table.add_column("Mood", justify="center", width=7)
    history_table.add_column("Thought / Context")

    if not recent:
        history_table.add_row("--", "--", "--", "[dim]No entries yet. Press 'c' or 't' to log.[/dim]")
    else:
        for r in recent:
            t_str = r.parsed_datetime.strftime("%m-%d %H:%M")
            t_type = "CBT" if r.is_cbt else "QUICK"
            mood_disp = f"{r.initial_mood} -> {r.final_mood}" if r.final_mood else str(r.initial_mood)
            thought_disp = r.automatic_thought or r.situation or r.primary_emotion or "--"
            if len(thought_disp) > 42:
                thought_disp = thought_disp[:39] + "..."
            history_table.add_row(t_str, t_type, mood_disp, thought_disp)

    right_panel = Panel(
        history_table,
        title="[bold cyan]Recent History Log[/bold cyan]",
        box=box.ROUNDED,
        border_style="dim",
    )
    layout["right"].update(right_panel)

    # Footer: Shortcuts
    shortcuts = Text()
    shortcuts.append("Commands: ", style="bold dim")
    shortcuts.append("[c] ", style="bold green")
    shortcuts.append("Check-in  ", style="dim")
    shortcuts.append("[t] ", style="bold cyan")
    shortcuts.append("CBT Record  ", style="dim")
    shortcuts.append("[b] ", style="bold yellow")
    shortcuts.append("Box Breathing  ", style="dim")
    shortcuts.append("[g] ", style="bold magenta")
    shortcuts.append("Launch GUI  ", style="dim")
    shortcuts.append("[r] ", style="bold white")
    shortcuts.append("Refresh  ", style="dim")
    shortcuts.append("[q] ", style="bold red")
    shortcuts.append("Quit", style="dim")

    layout["footer"].update(Panel(shortcuts, box=box.ROUNDED, border_style="dim"))
    return layout

def run_tui_dashboard(db: Database):
    """Run interactive full terminal dashboard loop."""
    console.clear()
    while True:
        layout = generate_dashboard_layout(db)
        console.clear()
        console.print(layout)

        try:
            choice = Prompt.ask(
                "\n[bold cyan]Select action[/bold cyan] [dim](c/t/b/g/r/q)[/dim]",
                default="r",
                show_default=False,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Exiting dashboard.[/dim]")
            break

        if choice in ("q", "quit", "exit"):
            console.print("[dim]Exiting Leahe Dashboard. Be mindful of your thoughts.[/dim]")
            break
        elif choice in ("c", "checkin", "check-in"):
            console.clear()
            run_quick_checkin(db)
            Prompt.ask("\n[dim]Press Enter to return to dashboard...[/dim]", default="")
        elif choice in ("t", "cbt", "thought"):
            console.clear()
            run_cbt_session(db)
            Prompt.ask("\n[dim]Press Enter to return to dashboard...[/dim]", default="")
        elif choice in ("b", "breath", "breathe", "sos"):
            console.clear()
            run_box_breathing()
            Prompt.ask("\n[dim]Press Enter to return to dashboard...[/dim]", default="")
        elif choice in ("g", "gui", "web"):
            console.print("[cyan][*] Launching Leahe GUI in your browser...[/cyan]")
            import webbrowser
            from .server import run_server, DEFAULT_PORT
            import threading
            try:
                server = run_server(db, port=DEFAULT_PORT)
                t = threading.Thread(target=server.serve_forever, daemon=True)
                t.start()
                webbrowser.open(f"http://127.0.0.1:{DEFAULT_PORT}")
                console.print(f"[green][+] GUI running at http://127.0.0.1:{DEFAULT_PORT}[/green]")
                time.sleep(1.5)
            except Exception as e:
                console.print(f"[red][!] Error launching GUI: {e}[/red]")
                time.sleep(2)
        elif choice in ("r", "refresh", ""):
            continue
        else:
            console.print(f"[yellow][!] Unknown command '{choice}'.[/yellow]")
            time.sleep(1)
