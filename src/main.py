"""
AGRO LIFE-AI
Biochemical Decay & Shelf-Life Predictor

DMI St. Eugene University
BSc Computer Science - Mini Project

Author: Prosper Chungu Mwape
"""

import sys


def display_project_information():
    """Display basic project information."""

    print("=" * 60)
    print("                 AGRO LIFE-AI")
    print("=" * 60)
    print("Biochemical Decay & Shelf-Life Predictor")
    print("-" * 60)
    print("Agriculture + Data Analytics + Machine Learning")
    print("-" * 60)
    print("Project Type : BSc Computer Science Mini Project")
    print("Developer    : Prosper Chungu Mwape")
    print("Institution  : DMI St. Eugene University")
    print("=" * 60)


def check_python_environment():
    """Display the Python version being used."""

    print("\nPython Environment")
    print("-" * 60)
    print("Python Version:", sys.version.split()[0])
    print("Python Executable:")
    print(sys.executable)


def main():
    """Main entry point of AGRO LIFE-AI."""

    display_project_information()
    check_python_environment()

    print("\nSystem Status")
    print("-" * 60)
    print("AGRO LIFE-AI project initialized successfully.")
    print("Ready for data processing and machine-learning development.")
    print("=" * 60)


if __name__ == "__main__":
    main()