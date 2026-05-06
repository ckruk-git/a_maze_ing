#!/usr/bin/env python3
"""Maze visualizer using solid block rendering for connected walls."""

import argparse
import os
import sys
from typing import List, Optional, Tuple

WALL_CHAR = "█"
SPACE_CHAR = " "
ENTRY_CHAR = "E"
EXIT_CHAR = "X"
PATH_CHAR = "█"
HIGHLIGHT_CHAR = "█"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def parse_maze_file(path: str) -> Tuple[List[List[int]], Optional[Tuple[int, int]], Optional[Tuple[int, int]], Optional[str]]:
    """Parse maze file and return grid plus optional entry/exit coordinates and solution path."""
    with open(path, "r", encoding="utf-8") as handle:
        lines = [line.rstrip("\n") for line in handle]

    grid_lines = []
    entry = None
    exit = None
    solution_path = None
    reached_blank = False

    for line in lines:
        stripped = line.strip()
        if stripped == "":
            reached_blank = True
            continue

        if not reached_blank:
            grid_lines.append(stripped)
            continue

        if entry is None:
            entry = parse_coordinate_line(stripped)
            continue

        if exit is None:
            exit = parse_coordinate_line(stripped)
            continue

        if solution_path is None:
            solution_path = stripped
        else:
            solution_path += stripped

    if not grid_lines:
        raise ValueError("Maze file does not contain any maze grid lines.")

    width = len(grid_lines[0])
    for row in grid_lines:
        if len(row) != width:
            raise ValueError("Maze rows must all be the same width.")

    grid: List[List[int]] = []
    for row in grid_lines:
        try:
            grid.append([int(c, 16) for c in row])
        except ValueError as exc:
            raise ValueError(f"Invalid hex digit in maze file: {row}") from exc

    return grid, entry, exit, solution_path


def parse_coordinate_line(line: str) -> Tuple[int, int]:
    parts = [part.strip() for part in line.split(",") if part.strip()]
    if len(parts) != 2:
        raise ValueError(f"Invalid coordinate line: {line}")
    return int(parts[0]), int(parts[1])


def render_maze(
    grid: List[List[int]],
    entry: Optional[Tuple[int, int]] = None,
    exit: Optional[Tuple[int, int]] = None,
    solution_path: Optional[str] = None,
) -> str:
    height = len(grid)
    width = len(grid[0])

    canvas_rows = 2 * height + 1
    canvas_cols = 2 * width + 1
    canvas = [[SPACE_CHAR for _ in range(canvas_cols)] for _ in range(canvas_rows)]

    def fill_wall(r: int, c: int) -> None:
        if 0 <= r < canvas_rows and 0 <= c < canvas_cols:
            canvas[r][c] = WALL_CHAR

    def fill_path(r: int, c: int) -> None:
        if 0 <= r < canvas_rows and 0 <= c < canvas_cols:
            canvas[r][c] = f"{RED}{PATH_CHAR}{RESET}"

    # Draw walls and cell centers
    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            center_r = 2 * y + 1
            center_c = 2 * x + 1
            canvas[center_r][center_c] = SPACE_CHAR

            if cell & 1:
                fill_wall(center_r - 1, center_c)
            if cell & 2:
                fill_wall(center_r, center_c + 1)
            if cell & 4:
                fill_wall(center_r + 1, center_c)
            if cell & 8:
                fill_wall(center_r, center_c - 1)

    # Fill corner intersections when any adjacent wall segment is present
    for r in range(0, canvas_rows, 2):
        for c in range(0, canvas_cols, 2):
            if has_adjacent_wall(canvas, r, c):
                fill_wall(r, c)

    # Highlight any 42-pattern cells (full-wall cells) first.
    if entry is not None:
        pattern_cells = {
            (x, y)
            for y, row in enumerate(grid)
            for x, value in enumerate(row)
            if value == 0x0F
        }
        for x, y in pattern_cells:
            r = 2 * y + 1
            c = 2 * x + 1
            if 0 <= r < canvas_rows and 0 <= c < canvas_cols:
                canvas[r][c] = f"{YELLOW}{HIGHLIGHT_CHAR}{RESET}"

    # Render solution path if provided
    if solution_path and entry is not None:
        r = 2 * entry[1] + 1
        c = 2 * entry[0] + 1
        fill_path(r, c)

        for direction in solution_path:
            if direction == "N":
                r -= 1
            elif direction == "S":
                r += 1
            elif direction == "E":
                c += 1
            elif direction == "W":
                c -= 1
            else:
                continue

            fill_path(r, c)

            if direction == "N":
                fill_path(r - 1, c)
            elif direction == "S":
                fill_path(r + 1, c)
            elif direction == "E":
                fill_path(r, c + 1)
            elif direction == "W":
                fill_path(r, c - 1)

            if direction == "N":
                r -= 1
            elif direction == "S":
                r += 1
            elif direction == "E":
                c += 1
            elif direction == "W":
                c -= 1

            fill_path(r, c)

    # Place entry and exit markers if available and within bounds
    if entry is not None and 0 <= entry[0] < width and 0 <= entry[1] < height:
        canvas[2 * entry[1] + 1][2 * entry[0] + 1] = ENTRY_CHAR
    if exit is not None and 0 <= exit[0] < width and 0 <= exit[1] < height:
        canvas[2 * exit[1] + 1][2 * exit[0] + 1] = EXIT_CHAR

    return "\n".join("".join(row) for row in canvas)


def has_adjacent_wall(canvas: List[List[str]], r: int, c: int) -> bool:
    neighbors = [
        (r - 1, c),
        (r + 1, c),
        (r, c - 1),
        (r, c + 1),
    ]
    return any(0 <= nr < len(canvas) and 0 <= nc < len(canvas[0]) and canvas[nr][nc] == WALL_CHAR for nr, nc in neighbors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a maze file using solid blocks.")
    parser.add_argument("path", nargs="?", default="maze.txt", help="Path to the maze file to visualize")
    args = parser.parse_args()

    if not os.path.isfile(args.path):
        print(f"Maze file not found: {args.path}")
        return 1

    try:
        grid, entry, exit, solution_path = parse_maze_file(args.path)
    except Exception as exc:
        print(f"Error reading maze file: {exc}")
        return 1

    print(render_maze(grid, entry=entry, exit=exit, solution_path=solution_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
