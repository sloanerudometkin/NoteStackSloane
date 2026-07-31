import os
import sys
import subprocess


def test_running_as_a_script_shows_help_only_once(tmp_path):
    """
    Running `python -m python.src.main --help` should print the help
    text exactly one time. If it prints twice, something (usually a
    stray top-level call) is running the command logic more than once.
    """
    env = os.environ.copy()
    env["NOTES_HOME"] = str(tmp_path)  # keep this test out of the real ~/.notes

    result = subprocess.run(
        [sys.executable, "-m", "python.src.main", "--help"],
        capture_output=True,
        text=True,
        env=env,
    )

    # "Usage:" only appears once in display_help()'s text.
    # If it shows up twice in the output, main() ran the command twice.
    assert result.stdout.count("Usage:") == 1