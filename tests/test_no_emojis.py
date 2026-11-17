from pathlib import Path
import unicodedata

def is_emoji(char: str) -> bool:
    code = ord(char)
    if (0x1F300 <= code <= 0x1FAFF) or (0x1F600 <= code <= 0x1F64F) or (0x2600 <= code <= 0x27BF):
        return True
    return False

def test_strictly_no_emojis():
    project_root = Path(__file__).resolve().parent.parent
    python_files = list(project_root.glob("src/leahe/**/*.py")) + [
        project_root / "main.py",
        project_root / "leahe",
        project_root / "mood",
    ]

    for py_file in python_files:
        if not py_file.exists():
            continue
        content = py_file.read_text(encoding="utf-8")
        for line_num, line in enumerate(content.splitlines(), 1):
            for ch in line:
                assert not is_emoji(ch), (
                    f"Found emoji '{ch}' (U+{ord(ch):04X}) in {py_file}:{line_num}: {line}"
                )
