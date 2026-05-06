#!/usr/bin/env python3
"""
A-Maze-ing: Maze Generator
Generates random mazes with optional perfect maze generation.
"""

import sys
import random
from typing import Dict, Tuple
from mazegen import MazeGenerator

def parse_config(filename: str) -> Dict[str, str]:
    """Parse configuration file."""
    config = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE
                if '=' not in line:
                    raise ValueError(f"Invalid configuration line: {line}")
                
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                config[key] = value
        
        return config
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {filename}")
    except IOError as e:
        raise IOError(f"Error reading configuration file: {e}")


def validate_config(config: Dict[str, str]) -> Tuple[bool, str]:
    """Validate configuration parameters."""
    mandatory_keys = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT']
    
    for key in mandatory_keys:
        if key not in config:
            return False, f"Missing mandatory configuration key: {key}"
    
    try:
        width = int(config['WIDTH'])
        height = int(config['HEIGHT'])
        
        if width < 3 or height < 3:
            return False, "WIDTH and HEIGHT must be at least 3"
        
        if width > 1000 or height > 1000:
            return False, "WIDTH and HEIGHT must be at most 1000"
    
    except ValueError:
        return False, "WIDTH and HEIGHT must be integers"
    
    try:
        entry_parts = config['ENTRY'].split(',')
        if len(entry_parts) != 2:
            raise ValueError()
        entry = (int(entry_parts[0]), int(entry_parts[1]))
        
        exit_parts = config['EXIT'].split(',')
        if len(exit_parts) != 2:
            raise ValueError()
        exit_coord = (int(exit_parts[0]), int(exit_parts[1]))
    
    except ValueError:
        return False, "ENTRY and EXIT must be in format 'x,y' with integer coordinates"
    
    if entry == exit_coord:
        return False, "ENTRY and EXIT must be different"
    
    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        return False, "ENTRY coordinates out of bounds"
    
    if not (0 <= exit_coord[0] < width and 0 <= exit_coord[1] < height):
        return False, "EXIT coordinates out of bounds"
    
    if config['PERFECT'].lower() not in ['true', 'false']:
        return False, "PERFECT must be 'True' or 'False'"
    
    return True, ""


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    try:
        # Parse and validate configuration
        config = parse_config(config_file)
        is_valid, error_msg = validate_config(config)
        
        if not is_valid:
            print(f"Configuration error: {error_msg}", file=sys.stderr)
            sys.exit(1)
        
        # Extract configuration
        width = int(config['WIDTH'])
        height = int(config['HEIGHT'])
        entry_parts = config['ENTRY'].split(',')
        entry = (int(entry_parts[0]), int(entry_parts[1]))
        exit_parts = config['EXIT'].split(',')
        exit_coord = (int(exit_parts[0]), int(exit_parts[1]))
        output_file = config['OUTPUT_FILE']
        perfect = config['PERFECT'].lower() == 'true'
        seed = int(config.get('SEED', random.randint(0, 2**31 - 1)))
        
        # Generate maze
        print(f"Generating {width}x{height} maze with seed {seed}...", file=sys.stderr)
        maze = MazeGenerator(width, height, seed)
        maze.generate()
        
        # Validate maze and generate the output path
        is_valid, error_msg = maze.validate(entry, exit_coord, perfect=perfect)
        if not is_valid:
            print(f"Maze validation error: {error_msg}", file=sys.stderr)
            sys.exit(1)

        path = maze.solve(entry, exit_coord)
        output = maze.get_output(entry, exit_coord, path)
        
        # Write to file
        try:
            with open(output_file, 'w') as f:
                f.write(output)
            print(f"Maze written to {output_file}", file=sys.stderr)
        
        except IOError as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
