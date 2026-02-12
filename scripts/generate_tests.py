from pathlib import Path

PACKAGE_NAME = "manexp_web_lists"
TESTS_DIR = Path("tests")


def generate_tests():
    package_path = Path(PACKAGE_NAME)

    for py_file in package_path.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        relative_path = py_file.relative_to(package_path)
        test_file = TESTS_DIR / relative_path.parent / f"test_{py_file.name}"

        test_file.parent.mkdir(parents=True, exist_ok=True)

        if not test_file.exists():
            test_file.write_text(
                f"""\"\"\"Tests for {relative_path}\"\"\"

def test_placeholder():
    assert True
"""
            )
            print(f"Created {test_file}")


if __name__ == "__main__":
    generate_tests()
