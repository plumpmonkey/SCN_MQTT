#!/usr/bin/env bash
set -euo pipefail

# --- pretty helpers ---
note() { echo "🔎 $*"; }
ok()   { echo "✅ $*"; }
warn() { echo "⚠️  $*"; }
fail() { echo "❌ $*"; }

# Require sudo for apt; pip will run as the invoking user (not root)
if [[ "${EUID}" -ne 0 ]]; then
  fail "Please run this script with sudo (only apt needs it)."
  exit 1
fi
if [[ -z "${SUDO_USER:-}" || "${SUDO_USER}" == "root" ]]; then
  fail "SUDO_USER is not set. Run via 'sudo ./install.sh' as a real user."
  exit 1
fi

# Regex to hide only the noisy pip warnings from older Ubuntu packages
PIP_WARN_FILTER='^WARNING: Error parsing dependencies of (distro-info|python-debian): Invalid version: .*$'

# Run user-level pip with filtered stderr so students do not see those warnings
upip() {
  # All other warnings and errors will still be shown
  sudo -u "$SUDO_USER" env PIP_DISABLE_PIP_VERSION_CHECK=1 \
    python3 -m pip "$@" \
    2> >(grep -v -E "${PIP_WARN_FILTER}" >&2)
}

note "Updating package lists..."
apt update -y -qq
ok "Packages updated."

note "Installing required system packages..."
apt install -y -qq python3-tk mosquitto-clients python3-pip
ok "System packages installed."

note "⬆️  Upgrading pip (user-level)…"
upip install --user --upgrade -q pip
ok "Pip upgraded (user)."

note "🐍 Installing Python packages at user level…"
upip install --user --force-reinstall -q Pillow
ok "Pillow reinstalled (user)."

upip install --user -q paho-mqtt
ok "paho-mqtt installed (user)."

note "🔒 Installing PyArmor…"
upip install --user -q pyarmor
ok "PyArmor installed (user)."

note "🔧 Configuring PATH for user binaries..."
# Check if ~/.local/bin is already in PATH via .bashrc
USER_HOME=$(sudo -u "$SUDO_USER" bash -c 'echo $HOME')
BASHRC_FILE="$USER_HOME/.bashrc"

if ! sudo -u "$SUDO_USER" grep -q '\.local/bin' "$BASHRC_FILE" 2>/dev/null; then
    # Add ~/.local/bin to PATH in .bashrc
    sudo -u "$SUDO_USER" bash -c "echo '' >> '$BASHRC_FILE'"
    sudo -u "$SUDO_USER" bash -c "echo '# Added by MQTT Lab setup script' >> '$BASHRC_FILE'"
    sudo -u "$SUDO_USER" bash -c "echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> '$BASHRC_FILE'"
    ok "Added ~/.local/bin to PATH in .bashrc"
    # Also set PATH for the current session if we're in an interactive shell
    note "Setting PATH for current session..."
    export PATH="$USER_HOME/.local/bin:$PATH"
    ok "~/.local/bin added to current session PATH"
else
    ok "~/.local/bin already configured in PATH"
fi

# Optional: concise version summary for students
PY_SUMMARY=$(sudo -u "$SUDO_USER" python3 - <<'PY'
import pkgutil, importlib, sys
def ver(mod, attr="__version__"):
    try:
        m = importlib.import_module(mod)
        return getattr(m, attr, "unknown")
    except Exception:
        return "not importable"
print("=== System Python ===")
print("Python:", sys.version.split()[0])
try:
    import pip; print("pip:", pip.__version__)
except Exception:
    print("pip: unknown")
try:
    import PIL; print("Pillow:", getattr(PIL, "__version__", "unknown"))
except Exception:
    print("Pillow: not importable")
try:
    import paho.mqtt; print("paho-mqtt:", getattr(paho.mqtt, "__version__", "unknown"))
except Exception:
    print("paho-mqtt: not importable")
try:
    import pyarmor; print("pyarmor: installed")
except Exception:
    print("pyarmor: not importable")
PY
)
echo "$PY_SUMMARY"

note "📝 PyArmor Usage Notes:"
echo "   PyArmor is installed for system Python"
echo "   ~/.local/bin has been added to your PATH (current session and .bashrc)"
echo "   "
echo "   You can now use PyArmor directly:"
echo "   pyarmor gen your_script.py"
echo "   "
echo "   Python usage:"
echo "   python3 --version       # Will show system Python"
echo "   python3 your_script.py  # Will use system Python"
echo "   "
echo "   Alternative methods:"
echo "   ~/.local/bin/pyarmor gen your_script.py"
echo "   "
echo "   To verify setup:"
echo "   pyarmor --help"
echo "   which pyarmor"

echo "🎉 Installation completed successfully."
