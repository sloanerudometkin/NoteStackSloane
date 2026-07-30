import datetime

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
    

    



