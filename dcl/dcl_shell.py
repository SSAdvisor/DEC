import sys
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

try:
    import readline
except ImportError:
    pass

from dcl.dcl_interpreter import DCLInterpreter

def run_shell(repo_root=None):
    interpreter = DCLInterpreter(repo_root=repo_root)
    
    print("DEC RSTS/E V10.1-L DCL (DIGITAL Command Language)")
    print("Print/Batch Services (PBS) Active. Type HELP for commands.\n")
    
    prompt = "$ "
    while not interpreter.exit_requested:
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\n%DCL-I-LOGOUT, control-C / session terminated")
            break
            
        code, out = interpreter.execute_line(line)
        if out:
            print(out)
        if interpreter.exit_requested:
            break

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    interpreter = DCLInterpreter(repo_root=repo_root)

    args = sys.argv[1:]
    if not args:
        run_shell(repo_root)
        return

    # Check if running a command or procedure directly
    first_arg = args[0]
    first_arg_lower = first_arg.lower()
    if first_arg.startswith('@'):
        proc_file = first_arg[1:]
        code, out = interpreter.execute_procedure(proc_file, args[1:])
        if out:
            print(out)
        sys.exit(code)
    elif first_arg_lower.endswith('.com') or first_arg_lower.endswith('.dcl'):
        code, out = interpreter.execute_procedure(first_arg, args[1:])
        if out:
            print(out)
        sys.exit(code)
    else:
        # One-shot command execution
        raw_cmd = " ".join(args)
        code, out = interpreter.execute_line(raw_cmd)
        if out:
            print(out)
        sys.exit(code)

if __name__ == "__main__":
    main()
