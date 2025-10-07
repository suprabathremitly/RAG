#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                   🔧 FIXING PYDANTIC INSTALLATION 🔧                         ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ ERROR: Virtual environment not found!"
    echo "   Creating new virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to activate virtual environment"
    exit 1
fi

echo "   ✅ Virtual environment activated"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
PYTHON_VERSION=$(python3 --version)
echo "   $PYTHON_VERSION"

# Check if Python >= 3.9
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "   ⚠️  WARNING: Python 3.9+ recommended (you have $PYTHON_VERSION)"
fi
echo ""

# Uninstall old packages
echo "📦 Uninstalling old pydantic packages..."
pip uninstall pydantic pydantic-core pydantic-settings -y > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   ✅ Old packages uninstalled"
else
    echo "   ℹ️  No old packages found"
fi
echo ""

# Clear pip cache
echo "🧹 Clearing pip cache..."
pip cache purge > /dev/null 2>&1
echo "   ✅ Cache cleared"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✅ Pip upgraded"
echo ""

# Install specific pydantic versions
echo "📥 Installing pydantic packages..."
pip install pydantic==2.5.3 pydantic-core==2.14.6 pydantic-settings==2.1.0

if [ $? -ne 0 ]; then
    echo "   ❌ ERROR: Failed to install pydantic"
    echo "   Trying alternative method..."
    pip install --no-cache-dir pydantic==2.5.3
    if [ $? -ne 0 ]; then
        echo "   ❌ ERROR: Still failed. Please check your internet connection."
        exit 1
    fi
fi

echo "   ✅ Pydantic installed"
echo ""

# Verify installation
echo "✅ Verifying installation..."

# Check pydantic
PYDANTIC_VERSION=$(python3 -c "import pydantic; print(pydantic.__version__)" 2>&1)
if [ $? -eq 0 ]; then
    echo "   ✅ Pydantic: $PYDANTIC_VERSION"
else
    echo "   ❌ ERROR: Cannot import pydantic"
    echo "   $PYDANTIC_VERSION"
    exit 1
fi

# Check pydantic_core
PYDANTIC_CORE_VERSION=$(python3 -c "import pydantic_core; print(pydantic_core.__version__)" 2>&1)
if [ $? -eq 0 ]; then
    echo "   ✅ Pydantic Core: $PYDANTIC_CORE_VERSION"
else
    echo "   ❌ ERROR: Cannot import pydantic_core"
    echo "   $PYDANTIC_CORE_VERSION"
    exit 1
fi

echo ""

# Test application imports
echo "🧪 Testing application imports..."

TEST_RESULT=$(python3 -c "from app.models.schemas import SearchResponse; print('OK')" 2>&1)
if [ "$TEST_RESULT" = "OK" ]; then
    echo "   ✅ Application imports successful!"
else
    echo "   ⚠️  WARNING: Application imports failed"
    echo "   Error: $TEST_RESULT"
    echo ""
    echo "   This might be due to other missing dependencies."
    echo "   Installing all requirements..."
    pip install -r requirements.txt
    
    # Test again
    TEST_RESULT=$(python3 -c "from app.models.schemas import SearchResponse; print('OK')" 2>&1)
    if [ "$TEST_RESULT" = "OK" ]; then
        echo "   ✅ Application imports successful after installing all requirements!"
    else
        echo "   ❌ ERROR: Still failing. Error details:"
        echo "   $TEST_RESULT"
        exit 1
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                        ✅ FIX COMPLETE! ✅                                   ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Installed Versions:"
echo "   • Pydantic: $PYDANTIC_VERSION"
echo "   • Pydantic Core: $PYDANTIC_CORE_VERSION"
echo ""
echo "🚀 You can now start the server:"
echo "   ./run.sh"
echo ""
echo "   Or use the restart script:"
echo "   ./restart.sh"
echo ""

