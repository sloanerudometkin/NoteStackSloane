import sys
from python.src.notes import note
from python.src.config import settings

#5.1 and 5.2 command parser/dispatcher and display help
def display_help():
    """Display help information."""
    help_text = """
Notes Application - Personal Note Manager

Usage:
  notes create [--tags tag1,tag2]     Create a new note
  notes list [--tag tagname]          List all notes or filter by tag
  notes read <filename>               Display a specific note
  notes update <filename>             Update a note
  notes delete <filename>             Delete a note
  notes search <keyword>              Search notes by keyword
  notes tags                          List all tags
  notes menu                          Launch interactive menu mode
  notes --help                        Show this help message

Environment Variables:
  NOTES_HOME    Directory where notes are stored (default: ~/.notes)
    """
    print(help_text.strip())

#5.3 handle create commands
def extract_tags_from_args(args):
    """Look for a --tags flag in args and return its value as a list of valid tags."""
    if "--tags" in args:
        flag_index = args.index("--tags")
        if flag_index + 1 < len(args):
            tags_string = args[flag_index + 1]
            raw_tags = [t.strip() for t in tags_string.split(",")]

            valid_tags = []
            for tag in raw_tags:
                if is_valid_tag(tag):
                    valid_tags.append(tag)
                else:
                    print(f"Warning: skipping invalid tag '{tag}'")

            return valid_tags
    return []

def read_multiline_input():
    """Read lines from the user until they hit Ctrl+D (EOF)."""
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)

def handle_create_command(args):
    """Prompt the user for a title and content, then create the note."""
    tags = extract_tags_from_args(args)

    title = get_validated_input("Enter note title: ", is_valid_title).strip()

    print("Enter note content (press Ctrl+D when done):")
    content = read_multiline_input()

    if not tags:
        tags_input = input("Tags, comma-separated (press Enter to skip): ").strip()
        if tags_input:
            raw_tags = [t.strip() for t in tags_input.split(",")]
            tags = [t for t in raw_tags if is_valid_tag(t)]

    author = input("Author (press Enter to skip): ").strip() or None
    status = input("Status (press Enter to skip): ").strip() or None
    priority_input = input("Priority 1-5 (press Enter to skip): ").strip()
    priority = int(priority_input) if priority_input else None

    filename = note.create_note(title, content, tags, author=author, status=status, priority=priority)
    print(f"Note created: {filename}")
    
#5.4
def extract_tag_filter_from_args(args):
    """Look for a --tag flag in args and return its value, or None if absent."""
    if "--tag" in args:
        flag_index = args.index("--tag")
        if flag_index + 1 < len(args):
            return args[flag_index + 1]
    return None


def display_notes_list(note_files):
    """Print a summary line for each note file."""
    if len(note_files) == 0:
        print("No notes found.")
        return

    print("Your Notes:")
    print("=" * 40)

    for note_file in note_files:
        loaded_note = note.load_note(note_file.name)
        print(f"\n{note_file.name}")
        print(f"  Title: {loaded_note.title}")
        if loaded_note.tags:
            print(f"  Tags: {', '.join(loaded_note.tags)}")


def handle_list_command(args):
    """List all notes, or notes filtered by a --tag flag."""
    tag_filter = extract_tag_filter_from_args(args)

    if tag_filter is not None:
        results = note.filter_notes_by_tag(tag_filter)
        print(f"Notes tagged with '{tag_filter}':")
        for filename, loaded_note in results:
            print(f"  {filename}: {loaded_note.title}")
    else:
        note_files = note.list_all_notes()
        display_notes_list(note_files)

#5.5 last batch of handlers
def handle_read_command(args):
    """Display a specific note by filename."""
    if len(args) < 1:
        print("Error: Please specify a filename")
        print("Usage: notes read <filename>")
        return

    filename = args[0]
    note.read_note_by_filename(filename)


def handle_update_command(args):
    """Update a note's content by filename."""
    if len(args) < 1:
        print("Error: Please specify a filename")
        print("Usage: notes update <filename>")
        return

    filename = args[0]
    print("Enter new content (press Ctrl+D when done, or leave blank to keep unchanged):")
    new_content = read_multiline_input()

    if new_content.strip() == "":
        new_content = None

    note.update_note(filename, new_content=new_content)


def handle_delete_command(args):
    """Delete a note by filename, with confirmation."""
    if len(args) < 1:
        print("Error: Please specify a filename")
        print("Usage: notes delete <filename>")
        return

    filename = args[0]
    note.delete_note(filename)


def display_search_results(results, keyword):
    """Print search results in a readable list."""
    if len(results) == 0:
        print(f"No notes found containing '{keyword}'")
        return

    print(f"Found {len(results)} note(s) containing '{keyword}':")
    for filename, found_note in results:
        print(f"  {filename}: {found_note.title}")


def handle_search_command(args):
    """Search notes by keyword."""
    if len(args) < 1:
        print("Error: Please specify a search keyword")
        print("Usage: notes search <keyword>")
        return

    keyword = args[0]
    results = note.search_notes_by_keyword(keyword)
    display_search_results(results, keyword)


def handle_tags_command(args):
    """List all unique tags across every note."""
    all_tags = note.get_all_tags()

    if len(all_tags) == 0:
        print("No tags found.")
    else:
        print("All tags:")
        for tag in all_tags:
            print(f"  - {tag}")

#interactive menu mode
def display_menu():
    """Print the numbered list of actions the user can choose from."""
    print("\n=== Notes Manager ===")
    print("1. Create a note")
    print("2. List notes")
    print("3. Read a note")
    print("4. Update a note")
    print("5. Delete a note")
    print("6. Search notes")
    print("7. List all tags")
    print("8. Quit")


def run_interactive_menu():
    """Loop showing a menu of actions until the user chooses to quit."""
    while True:
        display_menu()
        choice = input("Choose an option (1-8): ").strip()

        if choice == "1":
            handle_create_command([])
        elif choice == "2":
            tag = input("Filter by tag (press Enter to skip): ").strip()
            if tag:
                handle_list_command(["--tag", tag])
            else:
                handle_list_command([])
        elif choice == "3":
            filename = input("Enter filename: ").strip()
            handle_read_command([filename])
        elif choice == "4":
            filename = input("Enter filename: ").strip()
            handle_update_command([filename])
        elif choice == "5":
            filename = input("Enter filename: ").strip()
            handle_delete_command([filename])
        elif choice == "6":
            keyword = input("Search for: ").strip()
            handle_search_command([keyword])
        elif choice == "7":
            handle_tags_command([])
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number 1-8.")

#made in 5.1
def parse_command_line_arguments(args):
    """Look at the command-line arguments and run the matching command."""
    if len(args) == 0 or args[0] == "--help":
        display_help()
        return

    command = args[0]
    remaining_args = args[1:]

    if command == "create":
        handle_create_command(remaining_args)
    elif command == "list":
        handle_list_command(remaining_args)
    elif command == "read":
        handle_read_command(remaining_args)
    elif command == "update":
        handle_update_command(remaining_args)
    elif command == "delete":
        handle_delete_command(remaining_args)
    elif command == "search":
        handle_search_command(remaining_args)
    elif command == "tags":
        handle_tags_command(remaining_args)
    elif command == "menu":
        run_interactive_menu()
    else:
        print(f"Unknown command: {command}")
        print("Use --help for usage information")

#5.6 create main entry point
def main():
    """Main entry point for the notes CLI application."""
    settings.ensure_notes_directory_exists()

    args = sys.argv[1:]

    try:
        parse_command_line_arguments(args)
    except Exception as e:
        print(f"Error: {e}")
        print("Use --help for usage information")
        sys.exit(1)

#6.2
def is_valid_title(title):
    """A title is valid if it's non-empty and not absurdly long."""
    return title.strip() != "" and len(title) <= 200


def is_valid_tag(tag):
    """A tag is valid if it has no whitespace and isn't empty."""
    has_whitespace = " " in tag or "\t" in tag
    return not has_whitespace and len(tag) > 0


def get_validated_input(prompt, validator_function):
    """Keep asking the user for input until it passes validator_function."""
    while True:
        user_input = input(prompt)
        if validator_function(user_input):
            return user_input
        else:
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    main()