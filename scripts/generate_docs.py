import os
import shutil
from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML

# ---------------- CONFIG ----------------
ROOT_DIR = "."
CODE_DIR = "manexp_web_lists"
DOC_DIR = "docs"
MKDOCS_FILE = "mkdocs.yml"
EXCLUSION_LIST = ["test.py"]
NAV_TO_KEEP = ["Home", "Getting Started"]
# ---------------------------------------


def generate_markdown_files() -> None:
    """
    Generate documentation Markdown files from code.

        Args:
            None

        Returns:
            None
    """

    # Remove doc dir to start fresh everytime
    generated_doc_dir = Path(ROOT_DIR) / DOC_DIR / CODE_DIR
    if generated_doc_dir.exists():
        shutil.rmtree(generated_doc_dir, ignore_errors=True)

    # Construct package path
    code_path = Path(ROOT_DIR) / CODE_DIR

    # Generate Markdown Files
    for dirpath, dirnames, filenames in os.walk(code_path):
        # Skip hidden folders and __pycache__
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "__pycache__"]

        # Skip __init__.py files, non python files and exclusion list
        filenames[:] = [f for f in filenames if f.endswith(".py") and f != "__init__.py" and f not in EXCLUSION_LIST]

        # Create folder if it doesn't exist
        doc_path = Path(ROOT_DIR) / DOC_DIR / dirpath
        doc_path.mkdir(parents=True, exist_ok=True)

        # Get module prefix
        package_path = Path(dirpath)
        package_parts = package_path.parts
        module_prefix = ".".join(package_parts)

        # Create files
        for filename in filenames:
            # Create filename
            file_name = filename.replace(".py", ".md")

            # Create file path
            file_path = Path(doc_path) / file_name

            # Create module name
            module = filename.removesuffix(".py")

            # Format title
            title = module.capitalize().replace("_", " ")

            # Format module path
            module_path = module_prefix + "." + module

            file_path.write_text(f"# {title}\n\n::: {module_path}\n    rendering:\n      show_root_heading: false\n\n")


def update_mkdocs_yaml() -> None:
    """
    Modify mkdocs.yml to match generated documentation

    Args:
            None

        Returns:
            None
    """

    # Initialize YAML client
    client = YAML()
    client.preserve_quotes = True

    # Load mkdocs.yml
    with open(MKDOCS_FILE) as f:
        mkdocs_data: Optional[dict] = client.load(f) or None

    if mkdocs_data is None:
        print("mkdocs.yml not found")
        exit()

    # Get path to documentation
    doc_path = Path(ROOT_DIR) / DOC_DIR

    # Initialize nav
    nav = []

    # Get existing nav
    existing_nav = [entry for entry in mkdocs_data.get("nav", []) if isinstance(entry, dict)]
    for entry in existing_nav:
        print(entry)
    nav_to_keep = [entry for entry in existing_nav if str(entry) in NAV_TO_KEEP]
    nav.extend(nav_to_keep)

    # Traverse generated Markdown files
    generated_path = Path(ROOT_DIR) / DOC_DIR / CODE_DIR
    for dirpath, _, filenames in os.walk(generated_path):
        dir_path = Path(dirpath)
        rel_dir = dir_path.relative_to(doc_path)

        # Stop if no file in dir
        if not filenames:
            continue

        # Build nested structure
        entries = []
        for file in sorted(filenames):
            if file.endswith(".md"):
                title = file.removesuffix(".md").replace("_", " ").capitalize()
                path = Path(rel_dir) / file
                str_path = str(path)
                entries.append({title: str_path})

        # Create nested entry only if not empty
        if entries:
            # For top-level folders
            if rel_dir.parts and rel_dir.parts[-1] != "manexp_web_lists":
                nav.append({rel_dir.parts[-1].capitalize(): entries})
            else:
                nav.extend(entries)

    # Update mkdocs_data
    mkdocs_data["nav"] = nav

    # Write updated mkdocs.yml
    with open(MKDOCS_FILE, "w") as f:
        client.dump(mkdocs_data, f)


def main():
    """
    Generate documentation Markdown files from Python modules, ready to use by mkdocs.
    """
    try:
        generate_markdown_files()
        update_mkdocs_yaml()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
