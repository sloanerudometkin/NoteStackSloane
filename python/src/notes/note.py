import datetime
from python.src.config.settings import build_note_file_path
from python.src.config.settings import get_absolute_path_to_notes_home

#6.1 handle file system errors
def safe_file_operation(operation_function):
    """Run operation_function and catch common file system errors."""
    try:
        return operation_function()
    except FileNotFoundError:
        print("Error: File not found")
        return None
    except PermissionError:
        print("Error: Permission denied. Check file permissions.")
        return None
    except IOError as e:
        print(f"Error: Failed to access file - {e}")
        return None

#1.1 define note data structure
class Note:
    """represents a single note with content and metadata"""
    def __init__(self, title, content):
        self.title = title
        self.content = content 
        self.created_timestamp = datetime.datetime.now()
        self.modified_timestamp = datetime.datetime.now()
        self.tags = []
        self.author = None
        self.status = None
        self.priority = None

#1.2 note validation
def is_valid_note(note):
    """Check whether a Note has the minimum required data."""
    if note.title.strip() == "":
        return False
    if note.content is None:
        return False
    return True

def validate_title(title):
    """raise an error if the title is invalid"""
    if title.strip() == "":
        raise ValueError("Title cannot be empty")
    if len(title) > 200:
        raise ValueError("Title too long (max 200 characters)")
    return True

#2.1 generate unique note file name
    #1st helper function
def sanitize_title(title):
    """Sanitize the title: keep alphanumeric characters, replace spaces with dashes."""
    safe_title = ""
    for letter in title:
        if letter.isalnum():
            letter = letter.lower()
            safe_title = safe_title + letter
        elif letter == " ":
            letter = "-"
            safe_title = safe_title + letter
    return safe_title

# 2nd helper function: get timestamp for unique title
def get_timestamp_string():
    now = datetime.datetime.now()
    timestamp_string = now.strftime("%Y%m%d-%H%M%S")
    return timestamp_string

def generate_note_filename(title):
    safe_title = sanitize_title(title)
    timestamp = get_timestamp_string()
    filename = safe_title + "-" + timestamp + ".md"
    return filename

#2.2 format YAML header
#helper function to create timestamp for frontlining
def format_iso8601(timestamp):
    return timestamp.isoformat()

#now actually format the note headers
def format_note_for_file(note):
    output = "---\n"
    output = output + "title: " + note.title + "\n"
    output = output + "created: " + format_iso8601(note.created_timestamp) + "\n"
    output = output + "modified: " + format_iso8601(note.modified_timestamp) + "\n"

    if note.status is not None:
        output = output + "status: " + note.status + "\n"
    if note.priority is not None:
        output = output + "priority: " + str(note.priority) + "\n"
    if note.author is not None:
        output = output + "author: " + note.author + "\n"
    if note.tags != []:
        output = output + "tags: " + "[" + ", ".join(note.tags) + "]" + "\n"

    output = output + "---\n\n"
    output = output + note.content

    return output

#2.3 save note: use helper functions from note and config/settings
def save_note(note):
    if not is_valid_note(note):
        raise ValueError("Invalid note")
    else:
        filename = generate_note_filename(note.title)
        full_path = build_note_file_path(filename)
        file_content = format_note_for_file(note)
    with open (full_path, "w") as f:
        f.write(file_content)
    return filename

#2.4 YAML parse header
def parse_yaml_header(file_content):
    if not file_content.startswith("---"): #make sure header opens with "---"
        raise ValueError("Invalid note format: missing YAML header")

    lines = file_content.split("\n") #split into lines and find where header closes

    yaml_end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            yaml_end_index = i
            break
    if yaml_end_index == -1:
        raise ValueError("Invalid note format: YAML header not closed")

    yaml_lines = lines[1:yaml_end_index] #pull out and parse yaml lines into metadata

    metadata = {}
    for line in yaml_lines:
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            metadata[key] = value

    content_lines = lines[yaml_end_index +1:] #everything after the closing "---" is the content
    content = "\n".join(content_lines)
    content = content.strip()

    return metadata, content

#2.5 load note: opposite of save_note
def load_note(filename):
    full_path = build_note_file_path(filename) #build path using filename

    if not full_path.exists(): #confirm file is actually there
        raise ValueError("Note file not found: " + filename)

    with open(full_path, "r") as f: #open and read the file content
        file_content = f.read()

    metadata, content = parse_yaml_header(file_content) #uses above function but unpacks two variable instead of packing them in

    note = Note(metadata["title"], content) #built metadata dictionary in 2.4 parse_yaml_header
    note.created_timestamp = datetime.datetime.fromisoformat(metadata["created"]) #does opposite of isoformat:turns string back into datetime object
    note.modified_timestamp = datetime.datetime.fromisoformat(metadata["modified"])

    if "author" in metadata: #checks whether optional key exists
        note.author = metadata["author"]
    if "status" in metadata:
        note.status = metadata["status"]
    if "priority" in metadata:
        note.priority = int(metadata["priority"])
    if "tags" in metadata:
        tags_string = metadata["tags"]
        tags_string = tags_string.strip("[]")
        note.tags = [tag.strip() for tag in tags_string.split(",")]

    return note

#6.3 safely load a note, handling corrupted files
def load_note_safely(filename):
    full_path = build_note_file_path(filename)

    if not full_path.exists():
        print(f"Error: Note file not found: {filename}")
        return None

    try:
        return load_note(filename)
    except (ValueError, KeyError) as e:
        print(f"Warning: File '{filename}' has corrupted YAML header")
        response = input("Would you like to view the raw content? (yes/no): ")

        if response.strip().lower() == "yes":
            with open(full_path, "r") as f:
                raw_content = f.read()
            print(raw_content)

        return None
    except Exception as e:
        print(f"Error loading note: {e}")
        return None

#CRUD OPERATIONS

#3.1 Create Note
def create_note(title, content, tags=None):
    note = Note(title, content)
    if tags is not None:
        note.tags = tags
    filename = save_note(note)
    print(f"Note created successfully: {filename}")
    return filename

#3.2 list all notes
def list_all_notes():
    notes_dir = get_absolute_path_to_notes_home() #created in utilities/settings, hands back path pointing to .notes
    note_files = list(notes_dir.glob("*.md")) #walks the directory and matches any filename that ends in .md
    note_files.sort(key=lambda f: f.stat().st_mtime, reverse=True) #run the sort function on each item, sort by timestamp
    return note_files

#3.3 read specific note
def display_note(note):
    print("=" * 50)
    print(note.title)
    print("=" * 50)
    print("")

    print("Created: " + format_iso8601(note.created_timestamp))
    print("Modified: " + format_iso8601(note.modified_timestamp))

    if note.tags:
        print("Tags: " + "[" + ", ".join(note.tags) + "]")

    if note.author is not None:
        print("Author: " + note.author)

    print("")
    print("-" * 50)
    print(note.content)
    print("-" * 50)

def read_note_by_filename(filename):
    note = load_note(filename)
    display_note(note)

#3.4 update note
def update_note(filename, new_content=None, new_tags=None):
    note = load_note(filename) #opens the file, parses the YAML header, and hands back a full Note object

    if new_content is not None:
        note.content = new_content
    if new_tags is not None:
        note.tags = new_tags

    note.modified_timestamp = datetime.datetime.now()

    full_path = build_note_file_path(filename) #turns a bare filename like "my-note.md" into the full path inside ~/.notes.
    file_content = format_note_for_file(note)

    with open(full_path, "w") as f: #overwrrite the file with updated stuff
        f.write(file_content)

    print(f"Note updated successfully: {filename}")
    return filename

#3.5 delete note
def delete_note(filename):
    full_path = build_note_file_path(filename)

    if not full_path.exists():
        raise ValueError("Note not found: " + filename)

    confirmation = input(f"Are you sure you want to delete '{filename}'? (yes/no): ")

    if confirmation.strip().lower() == "yes":
        full_path.unlink() #removes link from the directory
        print(f"Note deleted successfully: {filename}")
        return True
    else:
        print("Deletion cancelled.")
        return False

#4.1 search by keyword
def search_notes_by_keyword(keyword):
    all_note_files = list_all_notes()
    matching_notes = []

    for note_file in all_note_files:
        note = load_note(note_file.name)

        if keyword.lower() in note.title.lower():
            matching_notes.append((note_file.name, note))
        elif keyword.lower() in note.content.lower():
            matching_notes.append((note_file.name, note))

    return matching_notes

#4.2 filter by tag
def filter_notes_by_tag(tag):
    all_note_files = list_all_notes() #grab every note (.md)
    matching_notes = [] #prep an empty list to collect matches

    for note_file in all_note_files: #walk every file and load it into a note object
        note = load_note(note_file.name)
        note_tags_lower = [t.lower() for t in note.tags]

        if tag.lower() in note_tags_lower:
            matching_notes.append((note_file.name, note))

    return matching_notes

#4.3 get all unique tags
def get_all_tags():
    all_note_files = list_all_notes()
    all_tags = set() #creates an empty set

    for note_file in all_note_files:
        note = load_note(note_file.name)
        for tag in note.tags:
            all_tags.add(tag.lower()) #add is the same thing as append, but for sets

    return sorted(all_tags) #sorted takes a new list alphabetically sorted

          
    
    