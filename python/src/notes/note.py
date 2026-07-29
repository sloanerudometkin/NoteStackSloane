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



