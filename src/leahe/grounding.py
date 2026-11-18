"""Acute distress first-aid, grounding techniques, and nervous system pacing.

Clinical purpose:
When acute emotional distress, panic, or hyperarousal (amygdala hijack) occurs,
prefrontal cognitive restructuring cannot occur effectively until physiological arousal
is reduced. Grounding techniques activate the parasympathetic nervous system (vagal brake)
to restore cognitive capacity.

Strictly NO emojis. Clean ASCII symbols.
"""

import os
import time
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich import box

from .database import Database
from .views import print_header, format_delta_badge

console = Console()

def _safe_sleep(seconds: float) -> bool:
    """Sleep in short increments to allow responsive KeyboardInterrupt."""
    if os.getenv("PYTEST_CURRENT_TEST"):
        return True
    end_time = time.time() + seconds
    while time.time() < end_time:
        time.sleep(0.1)
    return True

def run_box_breathing(cycles: int = 4, phase_seconds: int = 4) -> None:
    """Rhythmic Box Breathing (4s Inhale, 4s Hold, 4s Exhale, 4s Hold).
    
    Used by clinical protocols and high-stress professionals to rapidly downregulate
    sympathetic arousal.
    """
    console.print("\n[bold cyan]=== BOX BREATHING (4-4-4-4 PROTOCOL) ===[/bold cyan]")
    console.print("[dim]Sit comfortably. Rest your hands in your lap. Focus solely on the pacing bar.[/dim]")
    console.print("[dim]Press Ctrl+C at any time to finish early.[/dim]\n")

    phases = [
        ("INHALE", "Inhale slowly through your nose, expanding your diaphragm..."),
        ("HOLD",   "Hold your breath gently without straining..."),
        ("EXHALE", "Exhale smoothly and completely through your mouth..."),
        ("HOLD",   "Hold empty and relaxed before the next breath..."),
    ]

    total_width = 24

    try:
        for c in range(1, cycles + 1):
            console.print(f"[bold yellow]-- Cycle {c} of {cycles} --[/bold yellow]")
            for name, cue in phases:
                console.print(f"[cyan]{name}:[/cyan] [dim]{cue}[/dim]")
                for elapsed in range(1, phase_seconds + 1):
                    filled = int((elapsed / phase_seconds) * total_width)
                    bar = "[" + "=" * filled + " " * (total_width - filled) + "]"
                    sys.stdout.write(f"\r  {bar} {elapsed}/{phase_seconds}s  ")
                    sys.stdout.flush()
                    _safe_sleep(1.0)
                sys.stdout.write("\n")
                sys.stdout.flush()
            console.print()
        console.print("[bold green][+] Box breathing completed. Your autonomic nervous system is settling.[/bold green]\n")
    except KeyboardInterrupt:
        console.print("\n[dim]Breathing session concluded.[/dim]\n")


def run_478_breathing(cycles: int = 4) -> None:
    """Dr. Andrew Weil's 4-7-8 Relaxing Breath.
    
    Inhale 4s, Hold 7s, Exhale 8s. Proven to stimulate the vagus nerve and reduce heart rate.
    """
    console.print("\n[bold cyan]=== 4-7-8 RELAXATION BREATHING ===[/bold cyan]")
    console.print("[dim]Place the tip of your tongue against the ridge behind your upper front teeth.[/dim]")
    console.print("[dim]Press Ctrl+C at any time to finish early.[/dim]\n")

    phases = [
        ("INHALE", 4, "Inhale quietly through your nose..."),
        ("HOLD",   7, "Hold your breath calmly..."),
        ("EXHALE", 8, "Exhale completely making a gentle whoosh sound..."),
    ]

    total_width = 24

    try:
        for c in range(1, cycles + 1):
            console.print(f"[bold yellow]-- Cycle {c} of {cycles} --[/bold yellow]")
            for name, duration, cue in phases:
                console.print(f"[cyan]{name} ({duration}s):[/cyan] [dim]{cue}[/dim]")
                for elapsed in range(1, duration + 1):
                    filled = int((elapsed / duration) * total_width)
                    bar = "[" + "=" * filled + " " * (total_width - filled) + "]"
                    sys.stdout.write(f"\r  {bar} {elapsed}/{duration}s  ")
                    sys.stdout.flush()
                    _safe_sleep(1.0)
                sys.stdout.write("\n")
                sys.stdout.flush()
            console.print()
        console.print("[bold green][+] 4-7-8 breathing completed. Heart rate and muscle tension lowered.[/bold green]\n")
    except KeyboardInterrupt:
        console.print("\n[dim]Breathing session concluded.[/dim]\n")


def run_54321_grounding() -> None:
    """5-4-3-2-1 Sensory Grounding Technique for acute anxiety, dissociation, and panic.
    
    Forces sensory processing in the parietal and occipital lobes, interrupting the catastrophic loop.
    """
    console.print("\n[bold cyan]=== 5-4-3-2-1 SENSORY GROUNDING PROTOCOL ===[/bold cyan]")
    console.print("[dim]This protocol redirects focus away from internal catastrophic thoughts to concrete physical reality.[/dim]\n")

    # 5 SEE
    console.print("[bold cyan][5] SEE:[/bold cyan] Look around the room. Name 5 specific things you can see right now.")
    console.print("[dim]Examples: the texture of the desk, a lamp, shadows on the wall, a pen, your shoes.[/dim]")
    Prompt.ask("Press Enter when you have identified 5 distinct visual objects", default="")
    console.print("  [+] Visual cortex engaged.\n")

    # 4 TOUCH / FEEL
    console.print("[bold cyan][4] FEEL / TOUCH:[/bold cyan] Notice 4 physical sensations you can feel right now.")
    console.print("[dim]Examples: the pressure of your feet against the floor, fabric on your shoulders, cool air on skin.[/dim]")
    Prompt.ask("Press Enter when you have registered 4 tactile contact points", default="")
    console.print("  [+] Somatosensory awareness activated.\n")

    # 3 HEAR
    console.print("[bold cyan][3] HEAR:[/bold cyan] Listen closely to your surroundings. Name 3 distinct sounds.")
    console.print("[dim]Examples: computer fan hum, distant traffic, your own breathing, clock ticking.[/dim]")
    Prompt.ask("Press Enter when you have noticed 3 distinct auditory sounds", default="")
    console.print("  [+] Auditory grounding established.\n")

    # 2 SMELL
    console.print("[bold cyan][2] SMELL:[/bold cyan] Name 2 things you can smell, or 2 comforting scents you remember.")
    console.print("[dim]Examples: coffee, fresh air, wood, citrus, rain.[/dim]")
    Prompt.ask("Press Enter when you have noted 2 scents", default="")
    console.print("  [+] Olfactory memory anchored.\n")

    # 1 GROUNDED TRUTH
    console.print("[bold cyan][1] GROUNDED TRUTH:[/bold cyan] State 1 objective fact about this immediate moment.")
    console.print("[dim]Example: 'Right now, in this chair, I am physically safe.'[/dim]")
    truth = Prompt.ask("[bold]Your grounded true statement[/bold]", default="Right now, in this moment, I am safe and breathing.").strip()
    console.print(f"\n[bold green][+] Grounded Anchor:[/bold green] \"{truth}\"\n")


def run_sos_session(db: Database) -> None:
    """Full SOS / First-Aid distress downregulation flow with pre/post ratings."""
    print_header("Acute Distress First-Aid (SOS)", subtitle="Physiological de-escalation and nervous system stabilization")

    console.print("[dim]When distress is severe (panic, overwhelm, racing pulse), logical cognitive restructuring[/dim]")
    console.print("[dim]does not work until physiological arousal is brought down to a manageable level.[/dim]\n")

    # Initial distress rating
    while True:
        try:
            val_str = Prompt.ask("[bold cyan]Rate current distress / overwhelm level (0-100%)[/bold cyan]", default="80").strip()
            initial_distress = max(0, min(100, int(val_str)))
            break
        except ValueError:
            initial_distress = 80
            break

    console.print("\n[bold]Select First-Aid Grounding Technique:[/bold]")
    console.print("  [1] Box Breathing (4-4-4-4 Protocol - 4 cycles / 64s)")
    console.print("  [2] 4-7-8 Relaxation Breath (Vagus nerve activation - 4 cycles / 76s)")
    console.print("  [3] 5-4-3-2-1 Sensory Grounding (Interrupt panic & racing thoughts)")
    console.print("  [4] Emergency Decatastrophizing Protocol (Face worst case & coping plan)")

    choice = Prompt.ask("[bold cyan]Select technique (1-4)[/bold cyan]", default="1").strip()

    if choice == "2":
        run_478_breathing(cycles=4)
    elif choice == "3":
        run_54321_grounding()
    elif choice == "4":
        from .session import run_decatastrophize_session
        run_decatastrophize_session(db)
        return
    else:
        run_box_breathing(cycles=4)

    # Re-rate distress
    while True:
        try:
            val_str = Prompt.ask("[bold cyan]Re-rate your distress level now (0-100%)[/bold cyan]", default=str(max(0, initial_distress - 30))).strip()
            final_distress = max(0, min(100, int(val_str)))
            break
        except ValueError:
            final_distress = max(0, initial_distress - 30)
            break

    relief = initial_distress - final_distress
    console.print(f"\n[bold green][+] Physiological First-Aid Complete![/bold green]")
    console.print(f"    Distress: {initial_distress}% -> {final_distress}% (Relief: {format_delta_badge(relief)}%)\n")

    # Optional transition to CBT once calm
    if final_distress <= 65:
        transition = Prompt.ask(
            "[bold cyan]Now that your nervous system is calmer, do you want to analyze the triggering thoughts in a CBT Thought Record? (y/N)[/bold cyan]",
            default="n",
        ).strip().lower()
        if transition in ("y", "yes"):
            from .session import run_cbt_session
            run_cbt_session(db)
