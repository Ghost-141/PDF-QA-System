import subprocess
import sys
import os

def run_in_new_terminal(command, cwd=None):
    if sys.platform == "win32":
        subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=cwd)
    else:
        print("Can't Find Terminal To Run the Process")
        
def run_app():

    project_root = os.path.dirname(os.path.abspath(__file__))
    api_command = [sys.executable, "-m", "uvicorn", "src.api:app", "--reload"]
    ui_command = [sys.executable, "-m", "streamlit", "run", "src/ui.py"]

    print("Starting FastAPI backend in a new terminal...")
    run_in_new_terminal(api_command, cwd=project_root)

    print("Starting Streamlit frontend in a new terminal...")
    run_in_new_terminal(ui_command, cwd=project_root)

if __name__ == "__main__":
    run_app()
