"""
Allow running the CLI with: python -m app.cli

This file makes `python -m app` work, which delegates to cli.main().
"""

from app.cli import main

main()
