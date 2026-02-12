import os

from ruamel.yaml import YAML

# ---------------- CONFIG ----------------
ROOT_PACKAGE = "manexp_web_lists"
PROJECT_ROOT = "."
DOCS_DIR = "docs/modules"
MKDOCS_FILE = "mkdocs.yml"
EXCLUSION_LIST = ["test.py"]
# ---------------------------------------


def generate_markdown_files() -> list[tuple]:
    """
    Generate documentation Markdown files from Python modules.

    :return: Navigation entries for mkdocs.yml
    :rtype: list[tuple]
    """
    # Create DOCS_DIR if it doesn't exist
    os.makedirs(DOCS_DIR, exist_ok=True)

    # list to store navigation entries
    nav_entries = []

    # Generate Markdown Files
    for dirpath, dirnames, filenames in os.walk(os.path.join(PROJECT_ROOT, ROOT_PACKAGE)):
        # Skip hidden folders and __pycache__
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "__pycache__"]

        # Relative path from PROJECT_ROOT
        rel_path = os.path.relpath(dirpath, PROJECT_ROOT)
        package_parts = rel_path.split(os.sep)
        module_prefix = ".".join(package_parts)

        # Collect all .py files
        py_files = [f for f in filenames if f.endswith(".py") and f not in EXCLUSION_LIST]
        if not py_files:
            continue  # skip folders with no .py files

        # Markdown file name
        md_filename = os.path.join(DOCS_DIR, f"{module_prefix.replace('.', '_')}.md")
        with open(md_filename, "w") as f:
            f.write(f"# {module_prefix}\n\n")

            for py_file in py_files:
                module_name = module_prefix if py_file == "__init__.py" else module_prefix + "." + py_file[:-3]

                f.write(f"## {module_name}\n\n")
                f.write(f"::: {module_name}\n")
                f.write("    rendering:\n")
                f.write("      show_root_heading: false\n\n")

        # Add to nav_entries
        nav_entries.append((module_prefix, os.path.relpath(md_filename, "docs").replace("\\", "/")))
    return nav_entries


def update_mkdocs_yaml(nav_entries: list[tuple]) -> None:
    """
    Modify mkdocs.yml to match generated documentation

    :param nav_entries: Navigation entries for mkdocs.yml
    :type nav_entries: list[tuple]
    """

    # Initialize YAML client
    client = YAML()
    client.preserve_quotes = True

    # Load mkdocs.yml
    mkdocs_data = {}
    with open(MKDOCS_FILE) as f:
        mkdocs_data = client.load(f)

    # Build Modules nav
    api_nav = [{name: path} for name, path in nav_entries]

    # Replace or add API Reference
    found = False
    if "nav" in mkdocs_data:
        for i, item in enumerate(mkdocs_data["nav"]):
            if isinstance(item, dict) and "Modules" in item:
                mkdocs_data["nav"][i]["Modules"] = api_nav
                found = True
                break
    if not found:
        mkdocs_data.setdefault("nav", []).append({"Modules": api_nav})

    # Write updated mkdocs.yml
    with open(MKDOCS_FILE, "w") as f:
        client.dump(mkdocs_data, f)


def main():
    """
    Generate documentation Markdown files from Python modules, ready to use by mkdocs.
    """
    try:
        nav_entries = generate_markdown_files()
        update_mkdocs_yaml(nav_entries)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
