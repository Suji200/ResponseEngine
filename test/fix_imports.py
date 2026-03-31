# /Users/sujith/Desktop/NLP/ChatEngine/test/fix_imports.py
import os
import re

project_root = '/Users/sujith/Desktop/NLP/ChatEngine'
nlp_folder = os.path.join(project_root, 'Nlp')

print("="*60)
print("🔍 SCANNING FOR RELATIVE IMPORTS")
print("="*60)

# Check all Python files in Nlp folder
for filename in os.listdir(nlp_folder):
    if filename.endswith('.py'):
        filepath = os.path.join(nlp_folder, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Look for relative imports (..)
        relative_imports = re.findall(r'from\s+\.\.', content)
        if relative_imports:
            print(f"\n📄 {filename} has relative imports:")
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if '..' in line:
                    print(f"   Line {i}: {line.strip()}")
                    
            # Show the fix
            print(f"\n   🔧 FIX: Change to:")
            fixed_line = line.replace('from ..', 'from ')
            print(f"      {fixed_line}")