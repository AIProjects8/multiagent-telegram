#!/usr/bin/env python3
"""
Translation management script for multiagent-telegram project.
This script helps manage gettext translations for all agents.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command {cmd}: {e}")
        return False

def update_translations(agent_name):
    """Update translations for a specific agent"""
    agent_path = Path(f"Agents/{agent_name}")
    if not agent_path.exists():
        print(f"Agent {agent_name} not found")
        return False
    
    locale_path = agent_path / "locale"
    if not locale_path.exists():
        print(f"Locale directory not found for {agent_name}")
        return False
    
    # Update PO files from source
    for lang_dir in locale_path.iterdir():
        if lang_dir.is_dir() and lang_dir.name != "en":
            lc_messages = lang_dir / "LC_MESSAGES"
            if lc_messages.exists():
                po_file = lc_messages / "messages.po"
                mo_file = lc_messages / "messages.mo"
                
                if po_file.exists():
                    print(f"Compiling {po_file} to {mo_file}")
                    # Use absolute paths for the command
                    po_abs = po_file.absolute()
                    mo_abs = mo_file.absolute()
                    if run_command(f"msgfmt {po_abs} -o {mo_abs}", cwd=lc_messages):
                        print(f"✓ Compiled {lang_dir.name} for {agent_name}")
                    else:
                        print(f"✗ Failed to compile {lang_dir.name} for {agent_name}")
    
    return True

def update_all_translations():
    """Update translations for all agents"""
    agents = ["WeatherAgent", "TimeAgent", "DefaultAgent", "ConfigurationAgent", "YoutubeAgent"]
    
    print("Updating translations for all agents...")
    for agent in agents:
        print(f"\nProcessing {agent}...")
        update_translations(agent)
    
    print("\nTranslation update complete!")

def extract_messages(agent_name):
    """Extract messages from Python files for a specific agent"""
    agent_path = Path(f"Agents/{agent_name}")
    if not agent_path.exists():
        print(f"Agent {agent_name} not found")
        return False
    
    locale_path = agent_path / "locale"
    if not locale_path.exists():
        print(f"Locale directory not found for {agent_name}")
        return False
    
    # Find Python files in the agent directory
    python_files = list(agent_path.rglob("*.py"))
    if not python_files:
        print(f"No Python files found in {agent_name}")
        return False
    
    # Create POT file
    pot_file = locale_path / "messages.pot"
    files_arg = " ".join(str(f) for f in python_files)
    
    cmd = f"xgettext --from-code=UTF-8 --keyword=_ --keyword=gettext --output={pot_file} {files_arg}"
    
    print(f"Extracting messages for {agent_name}...")
    if run_command(cmd, cwd=agent_path):
        print(f"✓ Created {pot_file}")
        
        # Update existing PO files
        for lang_dir in locale_path.iterdir():
            if lang_dir.is_dir() and lang_dir.name != "en":
                lc_messages = lang_dir / "LC_MESSAGES"
                if lc_messages.exists():
                    po_file = lc_messages / "messages.po"
                    if po_file.exists():
                        cmd = f"msgmerge --update {po_file} {pot_file}"
                        if run_command(cmd, cwd=lc_messages):
                            print(f"✓ Updated {po_file}")
                        else:
                            print(f"✗ Failed to update {po_file}")
    else:
        print(f"✗ Failed to create POT file for {agent_name}")
        return False
    
    return True

def extract_all_messages():
    """Extract messages for all agents"""
    agents = ["WeatherAgent", "TimeAgent", "DefaultAgent", "ConfigurationAgent", "YoutubeAgent"]
    
    print("Extracting messages for all agents...")
    for agent in agents:
        print(f"\nProcessing {agent}...")
        extract_messages(agent)
    
    print("\nMessage extraction complete!")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python manage_translations.py <command> [agent_name]")
        print("\nCommands:")
        print("  update [agent_name]  - Update translations (compile PO to MO)")
        print("  extract [agent_name] - Extract messages from source files")
        print("  update-all           - Update all agents' translations")
        print("  extract-all          - Extract messages from all agents")
        print("\nExamples:")
        print("  python manage_translations.py update WeatherAgent")
        print("  python manage_translations.py extract-all")
        return
    
    command = sys.argv[1]
    
    if command == "update":
        if len(sys.argv) < 3:
            print("Please specify agent name for update command")
            return
        agent_name = sys.argv[2]
        update_translations(agent_name)
    
    elif command == "extract":
        if len(sys.argv) < 3:
            print("Please specify agent name for extract command")
            return
        agent_name = sys.argv[2]
        extract_messages(agent_name)
    
    elif command == "update-all":
        update_all_translations()
    
    elif command == "extract-all":
        extract_all_messages()
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'python manage_translations.py' for help")

if __name__ == "__main__":
    main()
