import os
from pathlib import Path

#0.2 Create configuration manager- ensure all notes are stored in one place, no matter where you run the app from
DEFAULT_NOTES_HOME = Path.home() / ".notes"

def get_notes_home_directory():
    notes_home_env = os.getenv("NOTES_HOME")

    if notes_home_env is not None:
        notes_home_path = Path(notes_home_env)
        return notes_home_path
    else:
        return DEFAULT_NOTES_HOME

def ensure_notes_directory_exists():
    notes_home = get_notes_home_directory() #call the function u just wrote to get the path
    if not notes_home.exists():
        notes_home.mkdir(parents=True, exist_ok=True)
    return notes_home

#0.3 create path utlities
def get_absolute_path_to_notes_home():
    notes_home = get_notes_home_directory()
    absolute_path = notes_home.resolve() #resolve converts the path to its absolute (fully resolved) form
    return absolute_path

def build_note_file_path(note_filename): #add a new file with note_filename to the end of the bath (after .notes)
    notes_home = get_absolute_path_to_notes_home()
    return notes_home / note_filename



    







