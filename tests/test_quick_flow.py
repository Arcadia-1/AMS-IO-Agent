"""
Quick Flow Test Module
Used to verify the complete process of Python code generating Skill scripts

Usage:
python test_quick_flow.py [options]

Options:
    -h, --help          Show help information
    -a, --all          Run all found files
    -i, --interactive  Interactive selection of files to run
    -n NUMBER          Run file with specified number
    -l, --list         Only list found files, do not execute
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.il_runner_tool import clear_all_figures_in_window  # New import

def get_all_code_files(output_dir, pattern=None):
    """Recursively get all code files, sorted by timestamp
    
    Args:
        output_dir: Output directory path
        pattern: Optional file matching pattern, defaults to all relevant files
        
    Returns:
        List containing (file path, modification time) tuples, sorted by timestamp
    """
    if pattern is None:
        patterns = ["*.py"]
    else:
        patterns = [pattern]
    
    all_files = []
    import glob
    for pattern in patterns:
        # Recursively find all subdirectories
        full_pattern = str(output_dir / "**" / pattern)
        code_files = glob.glob(full_pattern, recursive=True)
        for file in code_files:
            mtime = os.path.getmtime(file)
            all_files.append((file, mtime))
    # Sort by modification time
    all_files.sort(key=lambda x: x[1])
    return all_files

def test_get_all_code_files():
    """Test get_all_code_files function"""
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    
    files = get_all_code_files(output_dir)
    assert isinstance(files, list), "get_all_code_files should return a list"
    # Files should be sorted by modification time
    if len(files) > 1:
        assert files[0][1] <= files[-1][1], "Files should be sorted by modification time"

def get_latest_code_file(output_dir, pattern=None):
    """Get the latest generated code file"""
    all_files = get_all_code_files(output_dir, pattern)
    return all_files[-1][0] if all_files else None

def extract_skill_files(output_text, output_dir=None):
    """Extract generated skill script names from Python code output, return unique path relative to output"""
    skill_files = []
    lines = output_text.split('\n')
    
    patterns = [
        r'Skill script generated[:：]\s*([^\s]+\.il)',
        r'Generated skill file[:：]\s*([^\s]+\.il)', 
        r'Created skill script[:：]\s*([^\s]+\.il)',
        r'Skill file created[:：]\s*([^\s]+\.il)',
        r'Generated skill file[:：]\s*([^\s]+\.il)',
        r'Created skill script[:：]\s*([^\s]+\.il)',
        r'Saved as[:：]\s*([^\s]+\.il)',
        r'Output file[:：]\s*([^\s]+\.il)',
        r'File saved[:：]\s*([^\s]+\.il)',
        r'([a-zA-Z_][a-zA-Z0-9_/]*\.il)',
    ]
    
    seen = set()
    for line in lines:
        line = line.strip()
        for pattern in patterns:
            import re
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                match_path = Path(match)
                # Pseudo absolute path correction
                if not match_path.is_absolute() and str(match_path).startswith("home/"):
                    match_path = Path("/" + str(match_path))
                if output_dir is not None:
                    try:
                        match_path = match_path.resolve()
                        output_dir_resolved = output_dir.resolve()
                        if str(match_path).startswith(str(output_dir_resolved)):
                            match_path = match_path.relative_to(output_dir_resolved)
                        else:
                            # Skip files not under output_dir
                            continue
                    except Exception:
                        continue
                if str(match_path) not in seen:
                    seen.add(str(match_path))
                    skill_files.append(str(match_path))
    return skill_files

def test_extract_skill_files():
    """Test extract_skill_files function"""
    test_output = "Skill script generated: output/test.il\nGenerated skill file: output/test2.il"
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "output"
    
    skill_files = extract_skill_files(test_output, output_dir)
    assert isinstance(skill_files, list), "extract_skill_files should return a list"
    assert len(skill_files) > 0, "Should extract at least one skill file from test output"

def execute_python_code(code_file, project_root):
    """Execute Python code file"""
    import subprocess
    
    try:
        # Add project root directory to Python path
        env = os.environ.copy()
        python_path = env.get('PYTHONPATH', '')
        env['PYTHONPATH'] = f"{project_root}:{python_path}"
        
        # Execute Python file
        result = subprocess.run(
            [sys.executable, code_file],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60,
            env=env
        )
        
        if result.returncode != 0:
            error_msg = f"Exit code: {result.returncode}\n"
            if result.stdout:
                error_msg += f"Standard output:\n{result.stdout}\n"
            if result.stderr:
                error_msg += f"Error output:\n{result.stderr}"
            return False, error_msg
            
        return True, result.stdout
        
    except subprocess.TimeoutExpired:
        return False, "Execution timed out (60 seconds)"
    except Exception as e:
        return False, f"Execution exception: {str(e)}"

def execute_skill_file(skill_file, project_root):
    """Execute a single skill file"""
    try:
        # Import skillbridge
        from skillbridge import Workspace
        
        # Open workspace and execute skill script
        ws = Workspace.open()
        try:
            ws['load'](str(skill_file))
            cv = ws['geGetEditCellView']()
            ws['dbSave'](cv)
            return True
        except Exception as e:
            import traceback
            print(f"Failed to execute skill file: {e}")
            traceback.print_exc()
            return False
        finally:
            ws.close()
            
    except ImportError:
        # If skillbridge is not available, at least check if the file exists and is readable
        return Path(skill_file).is_file()
    except Exception as e:
        import traceback
        print(f"An error occurred while executing skill file: {e}")
        traceback.print_exc()
        return False

def list_files(files):
    """List files, showing the directory they are in"""
    print("\nAvailable code files:")
    for i, (file, mtime) in enumerate(files, 1):
        time_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        file_path = Path(file)
        parent_dir = file_path.parent.name
        # If parent directory is output, display as output, otherwise display as timestamp directory name
        dir_display = parent_dir if parent_dir != "output" else "output"
        print(f"{i}. {file_path.name} [Directory: {dir_display}] [Modified: {time_str}]")
    print()

def interactive_select(files):
    """Interactive file selection"""
    list_files(files)
    while True:
        try:
            choice = input("Please select a file to run by number (q to exit): ")
            if choice.lower() == 'q':
                return None
            idx = int(choice)
            if 1 <= idx <= len(files):
                return files[idx-1][0]
            print(f"Please enter a number between 1 and {len(files)}")
        except ValueError:
            print("Please enter a valid number")

# Modify run_single_file to call extract_skill_files and avoid executing the same physical file repeatedly

def run_single_file(code_file, project_root):
    """Run the complete process for a single file, avoiding repeated execution of the same Skill file"""
    if not code_file:
        print("❌ No code file found")
        return False
    print(f"Running code file: {code_file}")
    
    # Execute Python code
    success, output = execute_python_code(code_file, project_root)
    if not success:
        print(f"❌ Python code execution failed:\n{output}")
        return False
    print("✅ Python code execution successful")
    
    # Parse generated skill files (pass output_dir for standardization)
    output_dir = project_root / "output"
    skill_files = extract_skill_files(output, output_dir=output_dir)
    if not skill_files:
        print("❌ No generated skill files found")
        return False
    print(f"Found skill files: {', '.join(skill_files)}")
    
    # Validate and execute skill files
    executed_files = set()
    success_count = 0
    from pathlib import Path
    for skill_file in skill_files:
        # Clear window before each execution
        clear_result = clear_all_figures_in_window()
        print(f"Window clearing result: {clear_result}")
        skill_path = Path(skill_file)
        if not skill_path.is_absolute():
            skill_path = output_dir / skill_path
        if not skill_path.exists():
            skill_path = output_dir / Path(skill_file).name
        real_path = skill_path.resolve()
        print(f"Preparing to execute skill file: {skill_path} (exists: {skill_path.exists()})")  # Debug info
        if not skill_path.exists() or real_path in executed_files:
            continue
        if execute_skill_file(skill_path, project_root):
            success_count += 1
            executed_files.add(real_path)
            print(f"✅ Successfully executed: {skill_file}")
        else:
            print(f"❌ Execution failed: {skill_file}")
    
    if success_count == 0:
        print("❌ All skill scripts failed to execute")
        return False
    
    print(f"\n✅ Execution complete! Successfully executed {success_count}/{len(executed_files)} skill files")
    return True

def main():
    """Main function, handles command line arguments and executes corresponding operations"""
    parser = argparse.ArgumentParser(description="Quick Flow Test Tool")
    parser.add_argument('-a', '--all', action='store_true', help='Run all found files')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive selection of files to run')
    parser.add_argument('-n', type=int, help='Run file with specified number')
    parser.add_argument('-l', '--list', action='store_true', help='Only list found files, do not execute')
    parser.add_argument('-t', '--latest', action='store_true', help='Only run the latest Python code file')
    
    args = parser.parse_args()
    
    # Set paths
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Get all code files
    all_files = get_all_code_files(output_dir)
    if not all_files:
        print("❌ No code files found")
        return
    
    # Only list files
    if args.list:
        list_files(all_files)
        return
    
    # Interactive selection
    if args.interactive:
        selected_file = interactive_select(all_files)
        if selected_file:
            run_single_file(selected_file, project_root)
        return
    
    # Run file with specified number
    if args.n is not None:
        if 1 <= args.n <= len(all_files):
            run_single_file(all_files[args.n-1][0], project_root)
        else:
            print(f"❌ Invalid file number, please specify a number between 1 and {len(all_files)}")
        return
    
    # Run all files
    if args.all:
        print(f"Preparing to run all {len(all_files)} files...")
        for i, (file, _) in enumerate(all_files, 1):
            print(f"\nRunning file {i}/{len(all_files)}:")
            run_single_file(file, project_root)
        return
    
    # Run the latest file (new -t/--latest parameter)
    if args.latest:
        latest_file = all_files[-1][0] if all_files else None
        if latest_file:
            print("Running the latest file:")
            run_single_file(latest_file, project_root)
        else:
            print("❌ No latest code file found")
        return
    
    # Default: Run the latest file
    latest_file = all_files[-1][0] if all_files else None
    if latest_file:
        print("Running the latest file:")
        run_single_file(latest_file, project_root)

if __name__ == '__main__':
    main()