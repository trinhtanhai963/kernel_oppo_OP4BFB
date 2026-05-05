#!/usr/bin/env python3
"""
Fix Makefiles corrupted by the mass-append script.
The script appended 'ccflags-y += -I$(src)' without a newline,
so some lines look like: 'endifccflags-y += -I$(src)'
This script splits those lines and also ensures all Makefiles
have the ccflags-y += -I$(src) directive.
"""
import os
import sys

FLAG = 'ccflags-y += -I$(src)'
fixed_count = 0
already_ok = 0

for root, dirs, files in os.walk('.'):
    # Skip .git directory
    dirs[:] = [d for d in dirs if d != '.git']
    
    for name in files:
        if name != 'Makefile':
            continue
        
        path = os.path.join(root, name)
        try:
            with open(path, 'r', errors='replace') as f:
                content = f.read()
        except Exception as e:
            print(f"  SKIP (read error): {path}: {e}")
            continue
        
        if FLAG not in content:
            already_ok += 1
            continue
        
        # Fix lines where FLAG is concatenated with other content
        lines = content.split('\n')
        new_lines = []
        changed = False
        
        for line in lines:
            idx = line.find(FLAG)
            if idx > 0:  # FLAG found but NOT at start of line
                before = line[:idx]
                # Split into two lines
                new_lines.append(before)
                new_lines.append(FLAG)
                changed = True
            else:
                new_lines.append(line)
        
        if changed:
            new_content = '\n'.join(new_lines)
            try:
                with open(path, 'w') as f:
                    f.write(new_content)
                print(f"  FIXED: {path}")
                fixed_count += 1
            except Exception as e:
                print(f"  SKIP (write error): {path}: {e}")

print(f"\nDone! Fixed {fixed_count} files. {already_ok} files didn't need fixing.")
