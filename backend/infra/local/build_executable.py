#!/usr/bin/env python3
"""
Build script for creating PersonalAI executable using PyInstaller
"""
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_artifacts():
    """Remove previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    artifacts = ['build', 'dist', '__pycache__']

    for artifact in artifacts:
        if Path(artifact).exists():
            shutil.rmtree(artifact, ignore_errors=True)
            print(f"   Removed {artifact}/")

    # Remove .pyc files
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()

    print("✅ Cleanup complete\n")


def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")

    try:
        import PyInstaller
        print(f"   ✅ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("   ❌ PyInstaller not found")
        print("   Installing PyInstaller...")
        subprocess.check_call(["uv", "pip", "install", "pyinstaller"])
        print("   ✅ PyInstaller installed")

    try:
        import cryptography
        print(f"   ✅ Cryptography found")
    except ImportError:
        print("   ❌ Cryptography not found")
        print("   Installing Cryptography...")
        subprocess.check_call(["uv", "pip", "install", "cryptography>=41.0.0"])
        print("   ✅ Cryptography installed")

    print("✅ All dependencies satisfied\n")


def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building pi_backend executable...")
    print("   This may take several minutes...\n")

    spec_file = "PersonalAI.spec"

    if not Path(spec_file).exists():
        print(f"   ❌ Error: {spec_file} not found")
        print("   Run this script from the project root directory")
        return False

    log_file = Path("build_output.log")
    print(f"   Build output is also saved to: {log_file.absolute()}\n")

    try:
        # Run PyInstaller with the spec file.
        # -y  → auto-confirm overwrite of existing dist/ (avoids interactive hang)
        # --clean → wipe PyInstaller cache before each build
        with open(log_file, "w") as lf:
            result = subprocess.run(
                [sys.executable, "-m", "PyInstaller", spec_file, "--clean", "-y"],
                check=True,
                stdout=lf,
                stderr=subprocess.STDOUT,
            )

        print("\n✅ Build complete!\n")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code {e.returncode}")
        print(f"   Check {log_file.absolute()} for details")
        # Print last 40 lines of the log so the error is visible immediately
        if log_file.exists():
            lines = log_file.read_text().splitlines()
            print("\n--- Last 40 lines of build log ---")
            print("\n".join(lines[-40:]))
            print("-----------------------------------")
        return False


def show_build_info():
    """Display information about the built executable"""
    print("=" * 70)
    print("📦 BUILD SUMMARY")
    print("=" * 70)

    # One-file executable location
    exe_file = Path("dist/pi_backend")

    if exe_file.exists():
        print(f"\n✅ Single-file executable created:")
        print(f"   Location: {exe_file.absolute()}")

        # Calculate size
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"   Size: {size_mb:.2f} MB")

        print(f"\n   ✨ This is a fully portable executable!")
        print(f"   You can copy it anywhere and run it directly.")

        print(f"\n   To run the executable:")
        print(f"   {exe_file.absolute()}")

        print(f"\n   Or from any location after copying:")
        print(f"   ./pi_backend")

        print(f"\n   To enable SSL/HTTPS:")
        print(f"   export ENABLE_SSL=true")
        print(f"   ./pi_backend")
    else:
        print("\n❌ Build artifacts not found in dist/")

    print("\n" + "=" * 70)
    print("\n💡 TIPS:")
    print("   - This is a ONE-FILE executable - fully portable!")
    print("   - Copy it anywhere and run it directly, no installation needed")
    print("   - All dependencies and data files are bundled inside")
    print("   - The executable extracts itself to a temp folder on each run")
    print("   - SSL certificates are auto-generated on first run (if enabled)")
    print("   - Set ENABLE_SSL=true environment variable to enable HTTPS")
    print("=" * 70 + "\n")


def main():
    """Main build process"""
    print("\n" + "=" * 70)
    print("PersonalAI - Executable Build Script")
    print("=" * 70 + "\n")

    # Step 1: Clean
    clean_build_artifacts()

    # Step 2: Check dependencies
    check_dependencies()

    # Step 3: Build
    success = build_executable()

    # Step 4: Show results
    if success:
        show_build_info()
    else:
        print("\n❌ Build failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

