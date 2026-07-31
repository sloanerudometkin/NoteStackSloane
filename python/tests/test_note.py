from python.src.notes.note import list_all_notes, Note, display_note, read_note_by_filename, create_note

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
