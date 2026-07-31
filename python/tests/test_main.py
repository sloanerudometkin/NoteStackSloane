from python.src.main import (
    display_help, parse_command_line_arguments,
    extract_tags_from_args, handle_create_command,
    extract_tag_filter_from_args, handle_list_command, display_notes_list,
    handle_read_command, handle_update_command, handle_delete_command,
    handle_search_command, display_search_results, handle_tags_command, main,
)
from python.src.notes.note import create_note, load_note

#5.1 command parser/dispatcher
def test_help_flag_runs_without_error(capsys):
    parse_command_line_arguments(["--help"])
    captured = capsys.readouterr()
    assert "Usage" in captured.out

def test_empty_args_shows_help(capsys):
    parse_command_line_arguments([])
    captured = capsys.readouterr()
    assert "Usage" in captured.out

def test_unknown_command_shows_error(capsys):
    parse_command_line_arguments(["not-a-real-command"])
    captured = capsys.readouterr()
    assert "Unknown command" in captured.out

def test_known_command_does_not_show_unknown_error(capsys):
    parse_command_line_arguments(["list"])
    captured = capsys.readouterr()
    assert "Unknown command" not in captured.out

#5.2 display help command
def test_display_help_mentions_all_commands(capsys):
    display_help()
    captured = capsys.readouterr()
    assert "create" in captured.out
    assert "list" in captured.out
    assert "read" in captured.out
    assert "update" in captured.out
    assert "delete" in captured.out
    assert "search" in captured.out
    assert "tags" in captured.out

def test_display_help_mentions_notes_home_env_var(capsys):
    display_help()
    captured = capsys.readouterr()
    assert "NOTES_HOME" in captured.out

def test_help_flag_still_shows_all_commands(capsys):
    parse_command_line_arguments(["--help"])
    captured = capsys.readouterr()
    assert "NOTES_HOME" in captured.out

#5.3 create command
def test_extract_tags_from_args_parses_comma_list():
    result = extract_tags_from_args(["--tags", "urgent,school"])
    assert result == ["urgent", "school"]

def test_extract_tags_from_args_returns_empty_list_when_missing():
    result = extract_tags_from_args([])
    assert result == []

def test_handle_create_command_creates_note(monkeypatch, capsys):
    responses = iter(["My CLI Note", "First line", "Second line"])

    def fake_input(prompt=""):
        try:
            return next(responses)
        except StopIteration:
            raise EOFError()

    monkeypatch.setattr("builtins.input", fake_input)
    handle_create_command([])

    captured = capsys.readouterr()
    assert "Note created" in captured.out

def test_handle_create_command_rejects_empty_title_then_accepts(monkeypatch, capsys):
    responses = iter(["", "Valid Title After Retry", "some content"])
    def fake_input(prompt=""):
        try:
            return next(responses)
        except StopIteration:
            raise EOFError()
    monkeypatch.setattr("builtins.input", fake_input)

    handle_create_command([])

    captured = capsys.readouterr()
    assert "Invalid input" in captured.out
    assert "Note created" in captured.out

#5.4 list command
def test_extract_tag_filter_from_args_returns_value():
    result = extract_tag_filter_from_args(["--tag", "urgent"])
    assert result == "urgent"

def test_extract_tag_filter_from_args_returns_none_when_missing():
    result = extract_tag_filter_from_args([])
    assert result is None

def test_display_notes_list_handles_empty_list(capsys):
    display_notes_list([])
    captured = capsys.readouterr()
    assert "No notes found" in captured.out

def test_handle_list_command_shows_all_notes(capsys):
    create_note("List Handler Note", "some content", tags=["misc"])
    handle_list_command([])
    captured = capsys.readouterr()
    assert "List Handler Note" in captured.out

def test_handle_list_command_filters_by_tag(capsys):
    create_note("Filtered Note", "some content", tags=["special-tag-xyz"])
    handle_list_command(["--tag", "special-tag-xyz"])
    captured = capsys.readouterr()
    assert "Filtered Note" in captured.out

def test_handle_list_command_tag_filter_excludes_others(capsys):
    create_note("Excluded Note", "content", tags=["not-this-one"])
    handle_list_command(["--tag", "special-tag-xyz"])
    captured = capsys.readouterr()
    assert "Excluded Note" not in captured.out

#5.5 last batch of handlers
def test_handle_read_command_requires_filename(capsys):
    handle_read_command([])
    captured = capsys.readouterr()
    assert "Please specify a filename" in captured.out

def test_handle_read_command_shows_note_content(capsys):
    filename = create_note("Read Handler Note", "unique read content xyz")
    handle_read_command([filename])
    captured = capsys.readouterr()
    assert "unique read content xyz" in captured.out

def test_handle_update_command_requires_filename(capsys):
    handle_update_command([])
    captured = capsys.readouterr()
    assert "Please specify a filename" in captured.out

def test_handle_update_command_updates_content(monkeypatch):
    filename = create_note("Update Handler Note", "old content")
    responses = iter(["brand new content"])
    def fake_input(prompt=""):
        try:
            return next(responses)
        except StopIteration:
            raise EOFError()
    monkeypatch.setattr("builtins.input", fake_input)

    handle_update_command([filename])
    loaded = load_note(filename)
    assert loaded.content == "brand new content"

def test_handle_delete_command_requires_filename(capsys):
    handle_delete_command([])
    captured = capsys.readouterr()
    assert "Please specify a filename" in captured.out

def test_handle_delete_command_deletes_with_confirmation(monkeypatch):
    filename = create_note("Delete Handler Note", "temp content")
    monkeypatch.setattr("builtins.input", lambda prompt="": "yes")
    handle_delete_command([filename])
    # loading it again should now fail since it's gone
    import pytest
    with pytest.raises(ValueError):
        load_note(filename)

def test_handle_search_command_requires_keyword(capsys):
    handle_search_command([])
    captured = capsys.readouterr()
    assert "Please specify a search keyword" in captured.out

def test_display_search_results_handles_no_matches(capsys):
    display_search_results([], "nonexistent")
    captured = capsys.readouterr()
    assert "No notes found" in captured.out

def test_handle_tags_command_lists_tags(capsys):
    create_note("Tags Handler Note", "content", tags=["handler-tag-xyz"])
    handle_tags_command([])
    captured = capsys.readouterr()
    assert "handler-tag-xyz" in captured.out

 #5.6 main entry point
def test_main_handles_unknown_command_gracefully(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py", "not-a-real-command"])
    main()
    captured = capsys.readouterr()
    assert "Unknown command" in captured.out

def test_main_catches_errors_from_missing_notes(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py", "read", "totally-fake-file.md"])
    try:
        main()
    except SystemExit as e:
        assert e.code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.out

def test_main_ensures_notes_directory_exists(monkeypatch):
    from python.src.config.settings import get_notes_home_directory
    monkeypatch.setattr("sys.argv", ["main.py", "--help"])
    main()
    assert get_notes_home_directory().exists()
