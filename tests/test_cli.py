from click.testing import CliRunner
from pathlib import Path
from leahe.cli import main

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Leahe" in result.output

def test_cli_distortions():
    runner = CliRunner()
    result = runner.invoke(main, ["distortions"])
    assert result.exit_code == 0
    assert "All-or-Nothing Thinking" in result.output
    assert "Catastrophizing" in result.output

def test_cli_methods():
    runner = CliRunner()
    result = runner.invoke(main, ["methods"])
    assert result.exit_code == 0
    assert "The Double-Standard Technique" in result.output
    assert "Cost-Benefit Analysis" in result.output
    assert "The Downward / Vertical Arrow Technique" in result.output

def test_cli_seed_and_stats(tmp_path: Path):
    db_file = tmp_path / "cli_test.db"
    runner = CliRunner()

    # Seed
    seed_res = runner.invoke(main, ["--db", str(db_file), "seed-demo", "--count", "5"])
    assert seed_res.exit_code == 0
    assert "Inserted 5 realistic CBT demo records" in seed_res.output

    # Stats
    stats_res = runner.invoke(main, ["--db", str(db_file), "stats"])
    assert stats_res.exit_code == 0
    assert "COMPREHENSIVE CBT MOOD ANALYTICS" in stats_res.output
    assert "CBT Therapeutic Efficacy" in stats_res.output
    assert "David Burns Restructuring Methods" in stats_res.output

    # Verify / Audit
    verify_res = runner.invoke(main, ["--db", str(db_file), "verify"])
    assert verify_res.exit_code == 0
    assert "Pattern Verification" in verify_res.output

    # History
    hist_res = runner.invoke(main, ["--db", str(db_file), "history"])
    assert hist_res.exit_code == 0
    assert "Mood & CBT History Log" in hist_res.output

    # Show entry #1
    show_res = runner.invoke(main, ["--db", str(db_file), "show", "1"])
    assert show_res.exit_code == 0
    assert "ENTRY #1" in show_res.output
    assert "Automatic Thought" in show_res.output

    # Export markdown
    export_file = tmp_path / "out.md"
    exp_res = runner.invoke(main, ["--db", str(db_file), "export", "-f", "markdown", "-o", str(export_file)])
    assert exp_res.exit_code == 0
    assert export_file.exists()
    assert "CBT Mood & Thought Records Export" in export_file.read_text(encoding="utf-8")

    # Export yaml
    export_yaml_file = tmp_path / "out.yaml"
    exp_yaml_res = runner.invoke(main, ["--db", str(db_file), "export", "-f", "yaml", "-o", str(export_yaml_file)])
    assert exp_yaml_res.exit_code == 0
    assert export_yaml_file.exists()
    assert "initial_mood" in export_yaml_file.read_text(encoding="utf-8")
