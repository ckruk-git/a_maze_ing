.PHONY: install run debug clean lint lint-strict help

help:
	@echo "Available targets:"
	@echo "  install         - Install project dependencies"
	@echo "  run             - Run the maze generator"
	@echo "  visualize       - Run the maze visualizer"
	@echo "  debug           - Run in debug mode"
	@echo "  validate        - Validate the generated maze"
	@echo "  lint            - Run flake8 and mypy checks"
	@echo "  lint-strict     - Run strict mypy checks"
	@echo "  clean           - Remove cache files"

install:
	pip install --upgrade pip
	pip install flake8 mypy

run:
	python3 a_maze_ing.py config.txt

visualize:
	python3 maze_visualizer.py

debug:
	python3 -m pdb a_maze_ing.py config.txt

validate:
	python3 output_validator.py maze.txt

lint:
	flake8 . && mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . && mypy . --strict

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
