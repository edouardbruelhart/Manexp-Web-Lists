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
    Modify mkdocs.yml to match the generated documentation structure.

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
        mkdocs_data: Optional[dict] = client.load(f)

    if mkdocs_data is None:
        print("mkdocs.yml not found")
        return

    doc_path = Path(ROOT_DIR) / DOC_DIR
    generated_path = doc_path / CODE_DIR

    # Keep existing navigation entries
    existing_nav = mkdocs_data.get("nav", [])

    nav = [entry for entry in existing_nav if isinstance(entry, dict) and any(key in NAV_TO_KEEP for key in entry)]

    # Build documentation tree
    tree: dict = {}

    for md_file in sorted(generated_path.rglob("*.md")):
        rel_path = md_file.relative_to(doc_path)

        node = tree

        # Build folder hierarchy
        for folder in rel_path.parts[:-1]:
            if folder == CODE_DIR:
                continue
            node = node.setdefault(folder, {})

        # Add file
        title = rel_path.stem.replace("_", " ").capitalize()
        node[title] = str(rel_path)

    # Convert tree into MkDocs nav format
    def build_nav(node: dict) -> list:
        nav_entries = []

        for key in sorted(node):
            value = node[key]

            if isinstance(value, dict):
                nav_entries.append({key.replace("_", " ").capitalize(): build_nav(value)})
            else:
                nav_entries.append({key: value})

        return nav_entries

    nav.extend(build_nav(tree))

    # Save mkdocs.yml
    mkdocs_data["nav"] = nav

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
