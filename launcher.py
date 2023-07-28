import subprocess

def start_streamlit_app():
    subprocess.Popen(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    start_streamlit_app()
