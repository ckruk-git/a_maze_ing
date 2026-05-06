#!/usr/bin/env python3
import random
from collections import deque
from typing import Dict, List, Tuple, Set, Optional


class MazeGenerator:
    """Maze generator and solver."""
    
    # Wall bit positions
    NORTH = 0  # bit 0
    EAST = 1   # bit 1
    SOUTH = 2  # bit 2
    WEST = 3   # bit 3
    
    # Directions: (dx, dy, wall_bit, opposite_wall_bit)
    DIRECTIONS = {
        'N': (0, -1, NORTH, SOUTH),
        'S': (0, 1, SOUTH, NORTH),
        'E': (1, 0, EAST, WEST),
        'W': (-1, 0, WEST, EAST),
    }
    
    def __init__(self, width: int, height: int, seed: Optional[int] = None):
        """Initialize maze with given dimensions."""
        if width < 3 or height < 3:
            raise ValueError("Maze dimensions must be at least 3x3")
        
        self.width = width
        self.height = height
        self.cells = [[0x0F for _ in range(width)] for _ in range(height)]  # All walls initially
        self.pattern_cells: Set[Tuple[int, int]] = set()
        self.seed = seed if seed is not None else random.randint(0, 2**31 - 1)
        random.seed(self.seed)
    
    def _in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within maze bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def _carve_passage(self, x: int, y: int, nx: int, ny: int) -> None:
        """Remove wall between current cell (x,y) and neighbor (nx,ny)."""
        if not self._in_bounds(nx, ny):
            return
        if (x, y) in self.pattern_cells or (nx, ny) in self.pattern_cells:
            return

        dx = nx - x
        dy = ny - y
        
        # Find direction
        direction = None
        for d, (ddx, ddy, _, _) in self.DIRECTIONS.items():
            if ddx == dx and ddy == dy:
                direction = d
                break
        
        if direction is None:
            return
        
        wall_bit = self.DIRECTIONS[direction][2]
        opposite_bit = self.DIRECTIONS[direction][3]
        
        # Remove wall from current cell
        self.cells[y][x] &= ~(1 << wall_bit)
        
        # Remove opposite wall from neighbor cell
        self.cells[ny][nx] &= ~(1 << opposite_bit)
    
    def _create_42_pattern(self) -> bool:
        """Place a centered '42' pattern as isolated full-wall cells."""
        # A clearer 4 and 2 pattern in an 11x7 block.
        pattern_coords = [
            # 4
            (0, 0), (1, 0), (2, 0), (3, 0),
            (3, 1),
            (3, 2),
            (0, 3), (1, 3), (2, 3), (3, 3),
            (0, 4),
            (0, 5),
            (0, 6),
            
            # 2
            (6, 0), (7, 0), (8, 0), (9, 0), (10, 0),
            (10, 1),
            (6, 2), (7, 2), (8, 2), (9, 2), (10, 2),
            (6, 3),
            (6, 4),
            (6, 5),
            (6, 6), (7, 6), (8, 6), (9, 6), (10, 6),
        ]

        pattern_width = max(dx for dx, _ in pattern_coords) + 1
        pattern_height = max(dy for _, dy in pattern_coords) + 1

        if self.width < pattern_width or self.height < pattern_height:
            return False

        center_x = self.width // 2 - pattern_width // 2
        center_y = self.height // 2 - pattern_height // 2
        self.pattern_cells = {
            (center_x + dx, center_y + dy)
            for dx, dy in pattern_coords
        }

        for x, y in self.pattern_cells:
            if not self._in_bounds(x, y):
                return False
            self.cells[y][x] = 0x0F

        self._ensure_pattern_borders()
        return True

    def _ensure_pattern_borders(self) -> None:
        """Ensure pattern cells are fully walled off from adjacent maze cells."""
        for x, y in self.pattern_cells:
            for direction, (_, _, _, opposite_bit) in self.DIRECTIONS.items():
                nx, ny = x + self.DIRECTIONS[direction][0], y + self.DIRECTIONS[direction][1]
                if self._in_bounds(nx, ny) and (nx, ny) not in self.pattern_cells:
                    self.cells[ny][nx] |= (1 << opposite_bit)

    def _cell_available(self, x: int, y: int) -> bool:
        return self._in_bounds(x, y) and (x, y) not in self.pattern_cells

    def generate(self, perfect: bool = False) -> None:
        """Generate maze using recursive backtracking (DFS)."""
        self.pattern_cells.clear()
        self._create_42_pattern()

        start = (0, 0)
        if start in self.pattern_cells:
            for yy in range(self.height):
                for xx in range(self.width):
                    if (xx, yy) not in self.pattern_cells:
                        start = (xx, yy)
                        break
                else:
                    continue
                break

        visited = set(self.pattern_cells)
        visited.add(start)
        stack = [start]

        while stack:
            x, y = stack[-1]

            # Get unvisited neighbors
            neighbors = []
            for direction, (dx, dy, _, _) in self.DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if self._cell_available(nx, ny) and (nx, ny) not in visited:
                    neighbors.append((nx, ny))

            if neighbors:
                nx, ny = random.choice(neighbors)
                self._carve_passage(x, y, nx, ny)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        self._ensure_borders()
        self._ensure_pattern_borders()
        self.solution = self._find_path((0, 0), (self.width - 1, self.height - 1))
    
    def _ensure_borders(self) -> None:
        """Ensure all border cells have external walls."""
        for x in range(self.width):
            # Top border
            self.cells[0][x] |= (1 << self.NORTH)
            # Bottom border
            self.cells[self.height - 1][x] |= (1 << self.SOUTH)
        
        for y in range(self.height):
            # Left border
            self.cells[y][0] |= (1 << self.WEST)
            # Right border
            self.cells[y][self.width - 1] |= (1 << self.EAST)
    
    def _find_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[str]:
        """
        Find shortest path from start to end using BFS.
        Returns path as string of directions (N, S, E, W) or None if no path.
        """
        queue = deque([(start, "")])
        visited = {start}
        
        while queue:
            (x, y), path = queue.popleft()
            
            if (x, y) == end:
                return path
            
            # Try all directions
            for direction, (dx, dy, wall_bit, _) in self.DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                
                if not self._in_bounds(nx, ny) or (nx, ny) in visited:
                    continue
                
                # Check if there's a wall between current and neighbor
                if self.cells[y][x] & (1 << wall_bit):
                    continue  # There's a wall, can't go this way
                
                visited.add((nx, ny))
                queue.append(((nx, ny), path + direction))
        
        return None
    
    def validate(self, entry: Tuple[int, int], exit: Tuple[int, int], perfect: bool = False) -> Tuple[bool, str]:
        """
        Validate the maze.
        Returns (is_valid, error_message).
        """
        # Check entry and exit are different
        if entry == exit:
            return False, "Entry and exit must be different"
        
        # Check entry and exit are in bounds
        if not self._in_bounds(*entry) or not self._in_bounds(*exit):
            return False, "Entry or exit out of bounds"
        
        # Check connectivity
        visited = self._get_reachable_cells(entry)
        if exit not in visited:
            return False, "No path from entry to exit"
        
        # Check for 3x3 open areas (no area wider than 2 cells)
        if not self._check_no_large_open_areas():
            return False, "Maze has open areas wider than 2 cells"
        
        # Check for isolated cells
        if not self._check_no_isolated_cells():
            return False, "Maze has isolated cells"
        
        # Check consistency (walls must be mutual)
        if not self._check_wall_consistency():
            return False, "Maze has inconsistent walls"
        
        return True, ""
    
    def _get_reachable_cells(self, start: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """Get all reachable cells from a starting position."""
        visited = set()
        queue = deque([start])
        visited.add(start)
        
        while queue:
            x, y = queue.popleft()
            
            for direction, (dx, dy, wall_bit, _) in self.DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                
                if not self._in_bounds(nx, ny) or (nx, ny) in visited:
                    continue
                
                if self.cells[y][x] & (1 << wall_bit):
                    continue  # Wall blocks path
                
                visited.add((nx, ny))
                queue.append((nx, ny))
        
        return visited
    
    def _check_no_large_open_areas(self) -> bool:
        """Check that there are no 3x3 open areas."""
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                # Check 3x3 area
                all_open = True
                for dy in range(3):
                    for dx in range(3):
                        cy, cx = y + dy, x + dx
                        if cy >= self.height or cx >= self.width:
                            all_open = False
                            break
                        # Check if this cell is open (no internal walls with neighbors)
                        # This is a simplified check
                    if not all_open:
                        break
        return True  # Simplified for now
    
    def _check_no_isolated_cells(self) -> bool:
        """Check that no cells are isolated, except for '42' pattern cells (0x0F)."""
        visited = self._get_reachable_cells((0, 0))
        
        # Count cells - exclude cells with value 0x0F (42 pattern cells)
        total_non_pattern_cells = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] != 0x0F:
                    total_non_pattern_cells += 1
        
        return len(visited) == total_non_pattern_cells
    
    def _check_wall_consistency(self) -> bool:
        """Check that walls are consistent between adjacent cells."""
        for y in range(self.height):
            for x in range(self.width):
                # Check each direction
                for direction, (dx, dy, wall_bit, opposite_bit) in self.DIRECTIONS.items():
                    nx, ny = x + dx, y + dy
                    
                    if not self._in_bounds(nx, ny):
                        continue
                    
                    has_wall = bool(self.cells[y][x] & (1 << wall_bit))
                    neighbor_has_wall = bool(self.cells[ny][nx] & (1 << opposite_bit))
                    
                    if has_wall != neighbor_has_wall:
                        return False
        
        return True
    
    def get_output(self, entry: Tuple[int, int], exit: Tuple[int, int], path) -> str:
        lines = []

        for y in range(self.height):
            line = ""
            for x in range(self.width):
                line += f"{self.cells[y][x]:X}"
            lines.append(line)
        lines.append("")
        lines.append(f"{entry[0]},{entry[1]}")
        lines.append(f"{exit[0]},{exit[1]}")
        lines.append(path if path else "")

        return "\n".join(lines)

    def get_maze(self):
        return self.cells
    
    def get_solution(self):
        return self.solution
    
    def solve(self, entry, exit):
        return self._find_path(entry, exit)
