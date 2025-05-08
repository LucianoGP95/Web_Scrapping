import os, subprocess

# Get the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths to external resources
icon_path = os.path.join(script_dir, "resources", "icon.ico")
config_path = os.path.join(script_dir, "config", "config.json")
ffmpeg_path = os.path.join(script_dir, "libs", "ffmpeg.exe")

# Build the Nuitka arguments
nuitka_args = [
    "nuitka",
    "--standalone",
    "--enable-plugin=pyside6",
    "--output-dir=build",
    f"--windows-icon={icon_path}",
    f"--include-data-files={config_path}=config.json",
    f"--include-data-files={ffmpeg_path}=ffmpeg.exe",
    "app.py"
]

# Run Nuitka
subprocess.run(nuitka_args, check=True)

