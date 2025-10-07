# 🔧 Fix: Pydantic Core Import Error

## 🚨 Error Message

```
ImportError: cannot import name '_pydantic_core' from 'pydantic_core'
```

or

```
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
```

---

## ✅ Solution 1: Reinstall Pydantic (Recommended)

This is the most common fix:

```bash
# Navigate to project directory
cd /path/to/RAG_1

# Activate virtual environment
source venv/bin/activate

# Uninstall pydantic and pydantic-core
pip uninstall pydantic pydantic-core -y

# Reinstall pydantic (this will install the correct pydantic-core)
pip install pydantic==2.5.3

# Or install from requirements.txt
pip install -r requirements.txt --force-reinstall
```

---

## ✅ Solution 2: Clean Virtual Environment

If Solution 1 doesn't work, recreate the virtual environment:

```bash
# Navigate to project directory
cd /path/to/RAG_1

# Remove old virtual environment
rm -rf venv

# Create new virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

---

## ✅ Solution 3: Fix Specific Pydantic Versions

Install specific compatible versions:

```bash
# Activate virtual environment
source venv/bin/activate

# Uninstall both
pip uninstall pydantic pydantic-core -y

# Install specific versions that work together
pip install pydantic==2.5.3 pydantic-core==2.14.6
```

---

## ✅ Solution 4: Use Setup Script

Run the setup script which handles everything:

```bash
# Navigate to project directory
cd /path/to/RAG_1

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

---

## 🔍 Diagnostic Commands

### Check Python Version:
```bash
python3 --version
# Should be Python 3.9 or higher
```

### Check Pydantic Installation:
```bash
pip show pydantic
pip show pydantic-core
```

### Check if pydantic_core is importable:
```bash
python3 -c "import pydantic_core; print(pydantic_core.__version__)"
```

### List all installed packages:
```bash
pip list | grep pydantic
```

---

## 🎯 Complete Fix Workflow

Here's the complete step-by-step process:

```bash
# 1. Navigate to project
cd /path/to/RAG_1

# 2. Activate virtual environment
source venv/bin/activate

# 3. Check current installation
pip show pydantic pydantic-core

# 4. Uninstall both packages
pip uninstall pydantic pydantic-core -y

# 5. Clear pip cache
pip cache purge

# 6. Reinstall from requirements
pip install -r requirements.txt

# 7. Verify installation
python3 -c "import pydantic; print(pydantic.__version__)"
python3 -c "import pydantic_core; print(pydantic_core.__version__)"

# 8. Test the application
python3 -c "from app.models.schemas import SearchResponse; print('Success!')"

# 9. Start server
./run.sh
```

---

## 🐍 Python Version Issues

If you're using a different Python version on your other laptop:

### Check Python Version:
```bash
python3 --version
```

### If Python < 3.9:
```bash
# Install Python 3.9 or higher
# On macOS:
brew install python@3.9

# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.9 python3.9-venv

# Recreate venv with correct Python
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 💻 Platform-Specific Issues

### macOS (M1/M2 Apple Silicon):

```bash
# If on Apple Silicon, you might need:
arch -arm64 pip install pydantic pydantic-core

# Or use Rosetta:
arch -x86_64 pip install pydantic pydantic-core
```

### Linux:

```bash
# Install build dependencies
sudo apt-get update
sudo apt-get install -y python3-dev build-essential

# Then reinstall
pip install --no-cache-dir pydantic pydantic-core
```

### Windows:

```bash
# Use PowerShell or Command Prompt
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🔧 Advanced Troubleshooting

### Issue: Conflicting Versions

```bash
# Check for conflicts
pip check

# Fix conflicts
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

### Issue: Corrupted Installation

```bash
# Remove all pydantic-related packages
pip freeze | grep pydantic | xargs pip uninstall -y

# Clean install
pip install --no-cache-dir pydantic==2.5.3
```

### Issue: Permission Errors

```bash
# Don't use sudo! Use virtual environment instead
# If you accidentally used sudo, fix ownership:
sudo chown -R $USER:$USER venv/
```

---

## 📋 Quick Fix Script

Create a fix script:

```bash
cat > fix_pydantic.sh << 'EOF'
#!/bin/bash

echo "🔧 Fixing Pydantic Installation..."

# Activate virtual environment
source venv/bin/activate

# Uninstall
echo "📦 Uninstalling old packages..."
pip uninstall pydantic pydantic-core -y

# Clear cache
echo "🧹 Clearing pip cache..."
pip cache purge

# Reinstall
echo "📥 Reinstalling packages..."
pip install pydantic==2.5.3 pydantic-core==2.14.6

# Verify
echo "✅ Verifying installation..."
python3 -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
python3 -c "import pydantic_core; print(f'Pydantic Core: {pydantic_core.__version__}')"

echo "✅ Done! Try running ./run.sh now"
EOF

chmod +x fix_pydantic.sh
./fix_pydantic.sh
```

---

## 🎯 Most Common Solution

**90% of the time, this works:**

```bash
cd /path/to/RAG_1
source venv/bin/activate
pip uninstall pydantic pydantic-core -y
pip install pydantic==2.5.3
./run.sh
```

---

## ⚠️ Common Mistakes to Avoid

1. **Don't use `sudo pip install`** - Always use virtual environment
2. **Don't mix Python versions** - Use same Python version as requirements
3. **Don't skip cache clearing** - Old cached files can cause issues
4. **Don't install globally** - Always activate venv first

---

## 🧪 Test After Fix

```bash
# Test imports
python3 << EOF
from app.models.schemas import SearchResponse
from app.services.rag_pipeline import RAGPipeline
print("✅ All imports successful!")
EOF

# Start server
./run.sh
```

---

## 📞 Still Not Working?

If none of the above works, try this nuclear option:

```bash
# 1. Delete everything
rm -rf venv
rm -rf __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 2. Fresh start
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 3. Test
python3 -c "from app.models.schemas import SearchResponse; print('Success!')"

# 4. Run
./run.sh
```

---

## 📊 Expected Output After Fix

```bash
$ python3 -c "import pydantic; print(pydantic.__version__)"
2.5.3

$ python3 -c "import pydantic_core; print(pydantic_core.__version__)"
2.14.6

$ python3 -c "from app.models.schemas import SearchResponse; print('Success!')"
Success!
```

---

## 💡 Prevention for Future

Add this to your setup process:

```bash
# Always use these commands when setting up on a new machine:
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

**Try Solution 1 first - it fixes 90% of cases! 🚀**

