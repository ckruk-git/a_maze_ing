*This project has been created as part of the 42 curriculum*

# A-Maze-ing: Maze Generator & Visualizer

## Description

**A-Maze-ing** is a comprehensive maze generation and visualization system written in Python. It generates random, procedurally-created mazes using industry-standard algorithms, with support for reproducible generation via seeds, perfect maze mode, and interactive terminal visualization.

The project consists of two main components:
1. **Maze Generator** (`a_maze_ing.py`): Generates mazes from configuration files in hexadecimal format
2. **Terminal Visualizer** (`maze_visualizer.py`): Displays mazes interactively with user controls

### Key Features

✓ **Configurable Generation**: Full control via config files  
✓ **Deterministic Output**: Same seed always produces identical mazes  
✓ **Shortest Path Finding**: BFS algorithm for optimal solutions  
✓ **Hexadecimal Format**: Compact wall encoding (4 bits per cell)  
✓ **Perfect Maze Mode**: Single path between entry and exit  
✓ **Terminal Visualization**: ASCII rendering with colors and interactions  
✓ **Wall Validation**: Ensures mathematical maze coherence  
✓ **Full Connectivity**: No isolated cells (except optional "42" pattern)  
✓ **Error Handling**: Graceful validation and clear error messages  

## Instructions

### Installation

```bash
make install
```

### Running the Maze Generator

```bash
python3 a_maze_ing.py config.txt
```

### Running the Terminal Visualizer

```bash
python3 maze_visualizer.py
```

Or with custom files:
```bash
python3 maze_visualizer.py maze.txt config.txt
```

### Available Make Commands

```bash
make run           # Generate maze with default config
make visualize     # Run the terminal visualizer
make validate      # Validate maze output coherence
make lint          # Run code quality checks (flake8 + mypy)
make lint-strict   # Run strict mypy validation
make clean         # Remove cache files
make help          # Show all available commands
```

### Visualizer Controls

When running the visualizer, use these commands:

- **1**: Re-generate a new maze with random variations
- **2**: Toggle solution path visibility (cyan dots show the way)
- **3**: Cycle through wall colors (White, Bright White, Yellow, Green, Cyan, Blue)
- **4**: Quit the visualizer

**Visual Elements:**
- `E` (Magenta): Entry point (top-left)
- `X` (Red): Exit point (bottom-right)
- `·` (Cyan): Solution path (when toggled on)
- `█` (Colored): Walls
- ` ` (Space): Open corridors

## Configuration File Format

Create a `config.txt` file with these parameters:

```ini
# Maze dimensions (minimum 3x3)
WIDTH=20
HEIGHT=15

# Entry and exit coordinates (x,y format)
ENTRY=0,0
EXIT=19,14

# Output filename
OUTPUT_FILE=maze.txt

# Generate perfect maze? (True/False)
PERFECT=True

# Random seed for reproducibility (optional, random if omitted)
SEED=42

# Algorithm choice (optional, recursive_backtracking is default)
ALGORITHM=recursive_backtracking
```

**Mandatory Keys:** WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT  
**Optional Keys:** SEED, ALGORITHM

### Configuration Notes

- All coordinates are 0-indexed (0,0 is top-left)
- Maze dimensions must be at least 3x3 and at most 1000x1000
- Entry and exit must be different points within bounds
- PERFECT=True generates a maze with exactly one path between entry/exit
- SEED must be an integer; omit or randomize for random generation

## Output File Format

The generated `maze.txt` contains:

```
B9393955553D1555393B
AAAAAA9157C3853D46C2
C6C6AAEC5552C7C3D396
...
(HEIGHT lines of hex digits)

0,0
19,14
SSENNESSENNESSSWSWWWSSEESSSWSEENNENNENESENEENENWWWWSWNNNNEEEEESESSEEEENWNWWNEEEESENESESWSSWWSSWSEENENESSWSSSWSSSSENES
```

**Structure:**
- Lines 1-HEIGHT: Maze cells in hexadecimal (one digit per cell)
- Empty line separator
- Entry coordinates (x,y)
- Exit coordinates (x,y)
- Shortest path sequence (N/S/E/W directions)

### Wall Encoding

Each hex digit represents a cell's wall state (4 bits, one per cardinal direction):

| Bit | Direction | Value |
|-----|-----------|-------|
| 0   | North     | 1     |
| 1   | East      | 2     |
| 2   | South     | 4     |
| 3   | West      | 8     |

**Examples:**
- `0x0` = No walls (open cell)
- `0x5` (binary 0101) = North and South walls
- `0xF` (binary 1111) = All walls (fully closed)
- `0xA` (binary 1010) = East and West walls

## Maze Generation Algorithm

### Chosen Algorithm: Recursive Backtracking (Depth-First Search)

**Why This Algorithm?**

1. **Perfect Maze Generation**: Produces mazes with exactly one path when PERFECT flag is set
2. **Full Connectivity**: Guarantees all cells are reachable from the entry point
3. **Simplicity & Efficiency**: Linear time complexity O(width × height)
4. **Deterministic with Seeds**: Produces reproducible results with fixed random seeds
5. **Well-Tested**: Industry-standard for maze generation (used in video games, puzzle generation)

### How It Works

1. Start at entry point (0,0)
2. Mark current cell as visited
3. While unvisited neighbors exist:
   - Choose a random unvisited neighbor
   - Carve passage between cells (remove wall)
   - Move to neighbor and repeat
4. When stuck, backtrack until finding unvisited cells
5. Continue until all cells are visited

This creates a spanning tree of the maze, ensuring single connectivity.

### Alternative Algorithms (Bonus)

Other maze generation algorithms that could be implemented:
- **Prim's Algorithm**: Similar result, different approach
- **Kruskal's Algorithm**: Union-find based generation
- **Wilson's Algorithm**: Loop-erasing random walk

## Code Reusability

### Reusable Module: `Maze` Class

The core maze generation logic is encapsulated in the `Maze` class within `a_maze_ing.py`, making it importable and reusable in other projects.

#### Import and Usage Example

```python
from a_maze_ing import Maze

# Create a 30x30 maze with seed 12345
maze = Maze(width=30, height=30, seed=12345)
maze.generate(perfect=True)

# Access maze data
cells = maze.cells  # 2D array of cell wall encodings

# Find path between two points
path = maze._find_path((0, 0), (29, 29))
print(f"Path: {path}")  # Output: "SSEESSEWWWSEE..." etc

# Access specific cell
cell_value = maze.cells[10][15]  # Get cell at (15, 10)
print(f"Cell walls: {hex(cell_value)}")
```

#### Key Methods

- `generate(perfect=False)`: Generate maze using recursive backtracking
- `_find_path(start, end)`: Find shortest path using BFS (returns N/S/E/W string)
- `validate(entry, exit)`: Validate maze integrity
- `get_output(entry, exit)`: Generate output in required format

#### Maze Structure

- `cells`: 2D list `[[int, ...], ...]` where each int is wall encoding
- `width`, `height`: Dimensions
- `seed`: Reproducibility seed

### Validation Tool: `output_validator.py`

Standalone script to verify maze coherence:
```bash
python3 output_validator.py maze.txt
```

Checks that neighboring cells have consistent walls (no gaps or overlaps).

## Resources

### References

- **Maze Generation Algorithms**: https://en.wikipedia.org/wiki/Maze_generation_algorithm
- **Depth-First Search**: https://en.wikipedia.org/wiki/Depth-first_search
- **Breadth-First Search**: https://en.wikipedia.org/wiki/Breadth-first_search
- **Python Type Hints**: https://docs.python.org/3/library/typing.html
- **ANSI Color Codes**: https://en.wikipedia.org/wiki/ANSI_escape_code

### AI Usage

**AI was used for:**
- **Code Structure & Organization**: Assistance with class design and module architecture
- **Documentation**: Writing clear docstrings and README sections
- **Testing Strategies**: Suggestions for edge case validation
- **Terminal Rendering**: Guidance on ANSI color codes and terminal manipulation
- **Error Handling**: Best practices for graceful error management

**AI was NOT used for:**
- Core algorithm implementation (Recursive Backtracking, BFS)
- Wall encoding logic
- Maze validation rules
- Main business logic

**AI Disclosure**: The project structure and some helper functions were aided by AI suggestions, but all core algorithms were implemented from first principles understanding.

## Project Structure

```
hub/
├── a_maze_ing.py           # Main maze generator
├── maze_visualizer.py      # Terminal visualizer
├── output_validator.py     # Maze validation utility
├── config.txt              # Default configuration
├── maze.txt                # Generated maze output
├── Makefile                # Build automation
├── README.md               # This file
└── .gitignore              # Git exclusions
```

## Technical Choices

1. **Python 3.10+**: Modern Python with type hints
2. **Recursive Backtracking**: For reliable perfect maze generation
3. **BFS for Pathfinding**: Guaranteed shortest path
4. **Hexadecimal Format**: Compact 4-bit per cell storage
5. **Terminal ANSI Colors**: Cross-platform visualization without external deps

## Testing & Validation

Test the generator:
```bash
make validate     # Verify wall coherence
```

Test the visualizer:
```bash
make visualize    # Interactive testing
```

Run code quality checks:
```bash
make lint         # Standard checks
make lint-strict  # Strict validation
```

## Team & Project Management

**Solo Project**: Developed by single team member

**Roles:**
- Algorithm Design & Implementation
- Testing & Validation
- Documentation
- UI/UX (Terminal Visualization)

**Evolution:**
- Started with basic generator (mandatory part)
- Added terminal visualizer (bonus feature)
- Implemented interactive controls
- Enhanced validation and error handling
- Optimized maze rendering

**What Worked Well:**
- Clear separation of concerns (generator vs. visualizer)
- Comprehensive validation prevents invalid mazes
- Deterministic seeding enables reproducible testing
- ANSI color codes provide good visual feedback

**What Could Be Improved:**
- MiniLibX graphical interface (bonus feature not implemented)
- Performance optimization for very large mazes (>500x500)
- Additional maze generation algorithms
- Animation during maze generation
- Configuration file GUI tool

**Tools Used:**
- Python 3.10
- Standard library only (no external dependencies for core functionality)
- VS Code for development
- Git for version control
- Make for task automation
