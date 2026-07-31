from python.src.notes.note import list_all_notes, Note, display_note, read_note_by_filename, create_note, load_note, update_note, delete_note, search_notes_by_keyword, filter_notes_by_tag, get_all_tags, safe_file_operation

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

#4.2 filter by tag
def test_filter_finds_note_with_matching_tag():
    create_note("Tagged Note One", "content here", tags=["urgent"])
    results = filter_notes_by_tag("urgent")
    titles = [note.title for filename, note in results]
    assert "Tagged Note One" in titles

def test_filter_is_case_insensitive():
    create_note("Tagged Note Two", "content here", tags=["Urgent"])
    results = filter_notes_by_tag("urgent")
    titles = [note.title for filename, note in results]
    assert "Tagged Note Two" in titles

def test_filter_does_not_partial_match():
    create_note("Tagged Note Three", "content here", tags=["course"])
    results = filter_notes_by_tag("cours")
    titles = [note.title for filename, note in results]
    assert "Tagged Note Three" not in titles

def test_filter_returns_empty_list_for_no_match():
    results = filter_notes_by_tag("zzz_no_such_tag_zzz")
    assert results == []

#4.3 get all unique tags
def test_get_all_tags_returns_list():
    result = get_all_tags()
    assert isinstance(result, list)

def test_get_all_tags_includes_known_tag():
    create_note("Tag Collection Note", "content here", tags=["dinosaurs"])
    tags = get_all_tags()
    assert "dinosaurs" in tags

def test_get_all_tags_has_no_duplicates():
    create_note("Dup Tag Note One", "content", tags=["shared"])
    create_note("Dup Tag Note Two", "content", tags=["shared"])
    tags = get_all_tags()
    assert tags.count("shared") == 1

def test_get_all_tags_is_sorted():
    tags = get_all_tags()
    assert tags == sorted(tags)

#6.1 safe file operation
def test_safe_file_operation_returns_value_on_success():
    result = safe_file_operation(lambda: 42)
    assert result == 42

def test_safe_file_operation_catches_file_not_found(capsys):
    def raise_not_found():
        raise FileNotFoundError("no such file")

    result = safe_file_operation(raise_not_found)
    captured = capsys.readouterr()
    assert result is None
    assert "File not found" in captured.out

def test_safe_file_operation_catches_permission_error(capsys):
    def raise_permission():
        raise PermissionError("locked")

    result = safe_file_operation(raise_permission)
    captured = capsys.readouterr()
    assert result is None
    assert "Permission denied" in captured.out
    

