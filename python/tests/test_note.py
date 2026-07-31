from python.src.notes.note import list_all_notes, Note, display_note, read_note_by_filename, create_note, load_note, update_note, delete_note, search_notes_by_keyword

#3.2 list all notes
def test_list_all_notes_returns_a_list():
    result = list_all_notes()
    assert isinstance(result, list)

#3.3 display and read specific note
def test_display_note_runs_without_error():
    note = Note("Test Title", "Test content")
    note.tags = ["tag1", "tag2"]
    note.author = "Sloane"
    display_note(note)

def test_display_note_with_no_optional_fields():
    note = Note("Title Only", "Content only, no tags or author")
    display_note(note)

def test_read_note_by_filename_runs_without_error():
    filename = create_note("Pytest Note", "Some content for testing.", tags=["pytest"])
    read_note_by_filename(filename)

#3.4 update note
def test_update_note_changes_content():
    filename = create_note("Update Test", "original content", tags=["draft"])
    update_note(filename, new_content="updated content")
    loaded = load_note(filename)
    assert loaded.content == "updated content"

def test_update_note_changes_tags():
    filename = create_note("Update Tags Test", "some content", tags=["draft"])
    update_note(filename, new_tags=["final"])
    loaded = load_note(filename)
    assert loaded.tags == ["final"]

def test_update_note_leaves_content_when_not_given():
    filename = create_note("Update Partial Test", "keep me", tags=["draft"])
    update_note(filename, new_tags=["final"])  # no new_content passed
    loaded = load_note(filename)
    assert loaded.content == "keep me"

#3.5 delete note
def test_delete_note_removes_file_when_confirmed(monkeypatch):
    filename = create_note("Delete Me", "temporary content")
    monkeypatch.setattr("builtins.input", lambda prompt: "yes")
    result = delete_note(filename)
    assert result is True

def test_delete_note_keeps_file_when_declined(monkeypatch):
    filename = create_note("Keep Me", "important content")
    monkeypatch.setattr("builtins.input", lambda prompt: "no")
    result = delete_note(filename)
    assert result is False

def test_delete_note_raises_error_for_missing_file():
    import pytest
    with pytest.raises(ValueError):
        delete_note("this-file-does-not-exist.md")

#4.1 search by keyword
def test_search_finds_note_by_title_keyword():
    create_note("Python Tutorial", "Learn about loops and functions")
    results = search_notes_by_keyword("Python")
    titles = [note.title for filename, note in results]
    assert "Python Tutorial" in titles

def test_search_finds_note_by_content_keyword():
    create_note("Random Title", "This mentions xylophone somewhere inside")
    results = search_notes_by_keyword("xylophone")
    titles = [note.title for filename, note in results]
    assert "Random Title" in titles

def test_search_is_case_insensitive():
    create_note("Case Test Note", "irrelevant content")
    results = search_notes_by_keyword("case test")
    titles = [note.title for filename, note in results]
    assert "Case Test Note" in titles

def test_search_returns_empty_list_for_no_match():
    results = search_notes_by_keyword("zzz_this_should_never_match_zzz")
    assert results == []

