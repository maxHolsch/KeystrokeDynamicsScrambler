#!/bin/bash
# create_app.sh

# Set variables
APP_NAME="KeystrokeScrambler"
APP_DIR="$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
PYTHON_SCRIPTS_DIR="$RESOURCES_DIR/scripts"

# Create directory structure
mkdir -p "$MACOS_DIR" "$PYTHON_SCRIPTS_DIR"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>keystroke_launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.yourname.keystrokescrambler</string>
    <key>CFBundleName</key>
    <string>KeystrokeScrambler</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSAppleEventsUsageDescription</key>
    <string>This app needs to monitor keystrokes to scramble typing patterns.</string>
    <key>NSInputMonitoringUsageDescription</key>
    <string>This app needs to monitor keyboard input to function.</string>
</dict>
</plist>
EOL

# Create launcher script
cat > "$MACOS_DIR/keystroke_launcher" << EOL
#!/bin/bash
DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="\$(which python3)"
"\$PYTHON_PATH" "\$DIR/../Resources/scripts/gui_scrambler.py"
EOL

# Make launcher executable
chmod +x "$MACOS_DIR/keystroke_launcher"

# Copy Python files
cp gui_scrambler.py keystroke_core.py typing_patterns.py "$PYTHON_SCRIPTS_DIR/"

echo "App bundle created at $APP_DIR"
