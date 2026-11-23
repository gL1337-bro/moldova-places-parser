"""
Build script for Moldova Places Parser desktop app.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd: list, cwd: Path, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print(f"In: {cwd}")

    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def build_ui():
    """Build the React UI."""
    ui_dir = Path(__file__).parent / "ui"
    dist_dir = ui_dir / "dist"

    # Clean previous build
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    # Install dependencies
    if not run_command(["npm", "install"], ui_dir, "Installing UI dependencies"):
        return False

    # Build
    if not run_command(["npm", "run", "build"], ui_dir, "Building UI"):
        return False

    return True


def build_python():
    """Build Python executable with PyInstaller."""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"

    # Create spec file content
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['{src_dir.as_posix()}'],
    binaries=[],
    datas=[
        ('{src_dir.as_posix()}/parser', 'parser'),
        ('{project_root.as_posix()}/config', 'config'),
        ('{project_root.as_posix()}/data', 'data'),
    ],
    hiddenimports=[
        'parser',
        'parser.overpass_client',
        'parser.config_loader',
        'parser.models',
        'parser.extractor',
        'parser.classifier',
        'parser.scorer',
        'parser.exporter',
        'api',
        'flask',
        'flask_cors',
        'pandas',
        'openpyxl',
        'yaml',
        'requests',
        'tenacity',
        'tqdm',
        'geopy',
        'loguru',
        'webview',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MoldovaPlacesParser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{project_root.as_posix()}/assets/icon.ico' if os.path.exists('{project_root.as_posix()}/assets/icon.ico') else None,
)
'''

    spec_path = project_root / "MoldovaPlacesParser.spec"
    with open(spec_path, "w") as f:
        f.write(spec_content)

    # Run PyInstaller
    if not run_command(
        [sys.executable, "-m", "PyInstaller", "--clean", "MoldovaPlacesParser.spec"],
        project_root,
        "Building Python executable with PyInstaller"
    ):
        return False

    return True


def main():
    """Main build function."""
    project_root = Path(__file__).parent.parent

    print("🚀 Building Moldova Places Parser Desktop App")
    print(f"Project root: {project_root}")

    # Build UI first
    if not build_ui():
        print("❌ UI build failed")
        sys.exit(1)

    print("\n✅ UI built successfully")

    # Build Python executable
    if not build_python():
        print("❌ Python build failed")
        sys.exit(1)

    print("\n✅ Build completed successfully!")
    print(f"Executable: {project_root / 'dist' / 'MoldovaPlacesParser.exe'}")


if __name__ == "__main__":
    main()