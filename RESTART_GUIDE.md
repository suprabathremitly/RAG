# 🔄 How to Restart the Project

## 🚨 Problem: "Address Already in Use" Error

If you see an error like:
```
Error: [Errno 48] Address already in use
```

This means port 8000 is already being used by another process.

---

## ✅ Solution 1: Kill the Existing Process (Recommended)

### **Option A: Kill by Port Number**

```bash
# Find the process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or in one command
lsof -ti:8000 | xargs kill -9
```

### **Option B: Kill by Process Name**

```bash
# Find all uvicorn processes
ps aux | grep uvicorn

# Kill all uvicorn processes
pkill -f "uvicorn app.main:app"

# Or force kill
pkill -9 -f "uvicorn"
```

### **Option C: Kill by PID (Process ID)**

```bash
# Find the process
ps aux | grep uvicorn

# You'll see output like:
# suprabathc  45242  0.0  0.5  ... python -m uvicorn app.main:app

# Kill using the PID (second column)
kill -9 45242
```

---

## ✅ Solution 2: Use a Different Port

If you don't want to kill the existing process:

```bash
# Run on port 8001 instead
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Then access at: http://localhost:8001
```

---

## 🔄 Complete Restart Workflow

### **Step 1: Stop Any Running Servers**

```bash
# Kill all uvicorn processes
pkill -9 -f "uvicorn"

# Verify nothing is running on port 8000
lsof -ti:8000
# (Should return nothing)
```

### **Step 2: Start Fresh**

```bash
# Navigate to project directory
cd /Users/suprabathc/Documents/augment-projects/RAG_1

# Activate virtual environment
source venv/bin/activate

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Step 3: Verify It's Running**

```bash
# Check if server is responding
curl http://localhost:8000/api/health

# Should return: {"status":"healthy"}
```

---

## 🛠️ Quick Restart Script

Create a restart script for convenience:

```bash
# Create restart.sh
cat > restart.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping existing server..."
pkill -9 -f "uvicorn" 2>/dev/null

echo "⏳ Waiting 2 seconds..."
sleep 2

echo "🚀 Starting server..."
cd /Users/suprabathc/Documents/augment-projects/RAG_1
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF

# Make it executable
chmod +x restart.sh

# Run it
./restart.sh
```

---

## 🔍 Troubleshooting Commands

### **Check if Port 8000 is in Use:**

```bash
lsof -i:8000
```

**Output if in use:**
```
COMMAND   PID        USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
Python  45242 suprabathc    3u  IPv4 0x...      0t0  TCP *:8000 (LISTEN)
```

**Output if free:**
```
(nothing)
```

### **Check All Python Processes:**

```bash
ps aux | grep python
```

### **Check All Uvicorn Processes:**

```bash
ps aux | grep uvicorn
```

### **Kill All Python Processes (Nuclear Option):**

```bash
# ⚠️ WARNING: This kills ALL Python processes!
pkill -9 python
```

---

## 📋 Common Scenarios

### **Scenario 1: Server Running in Background**

```bash
# Kill it
pkill -9 -f "uvicorn"

# Restart
./run.sh
```

### **Scenario 2: Multiple Terminals Running Server**

```bash
# Kill all instances
pkill -9 -f "uvicorn"

# Start in one terminal only
./run.sh
```

### **Scenario 3: Port Stuck After Crash**

```bash
# Force kill anything on port 8000
lsof -ti:8000 | xargs kill -9

# Wait a moment
sleep 2

# Restart
./run.sh
```

### **Scenario 4: Permission Denied**

```bash
# Use sudo (if needed)
sudo lsof -ti:8000 | xargs sudo kill -9

# Or change to a higher port (no sudo needed)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

---

## 🎯 Best Practices

### **1. Always Stop Before Starting**

```bash
# Good practice
pkill -9 -f "uvicorn" && ./run.sh
```

### **2. Use One Terminal for Server**

Keep the server running in one dedicated terminal window. Don't start multiple instances.

### **3. Check Before Starting**

```bash
# Check if port is free
if lsof -ti:8000 > /dev/null; then
    echo "⚠️  Port 8000 is in use. Killing process..."
    kill -9 $(lsof -ti:8000)
    sleep 1
fi

# Start server
./run.sh
```

### **4. Use Screen or Tmux for Background Running**

```bash
# Start in screen session
screen -S rag_server
./run.sh

# Detach: Ctrl+A, then D
# Reattach: screen -r rag_server
```

---

## 🚀 Quick Reference Commands

| Task | Command |
|------|---------|
| **Kill server** | `pkill -9 -f "uvicorn"` |
| **Kill by port** | `lsof -ti:8000 \| xargs kill -9` |
| **Check port** | `lsof -i:8000` |
| **Start server** | `./run.sh` |
| **Start manually** | `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |
| **Different port** | `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001` |
| **Check health** | `curl http://localhost:8000/api/health` |

---

## 🔧 Update run.sh to Auto-Kill

You can update your `run.sh` to automatically kill existing processes:

```bash
#!/bin/bash

# Kill any existing uvicorn processes
echo "🛑 Stopping any existing servers..."
pkill -9 -f "uvicorn" 2>/dev/null

# Wait a moment
sleep 1

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Start the server
echo "🚀 Starting server on http://localhost:8000..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ⚠️ Important Notes

1. **`kill -9` is forceful** - It immediately terminates the process without cleanup
2. **`pkill -f` matches pattern** - Be careful not to kill unrelated processes
3. **Port 8000 is default** - You can use any port above 1024 without sudo
4. **Auto-reload is enabled** - Code changes will automatically restart the server

---

## 🎬 For Video Recording

Before recording your video:

```bash
# 1. Clean restart
pkill -9 -f "uvicorn"
sleep 2

# 2. Start fresh
./run.sh

# 3. Wait for startup (about 5 seconds)
sleep 5

# 4. Verify it's working
curl http://localhost:8000/api/health

# 5. Open browser
open http://localhost:8000

# 6. Start recording!
```

---

## 📞 Still Having Issues?

If you're still having problems:

1. **Reboot your machine** - This will clear all ports
2. **Check firewall** - Make sure port 8000 isn't blocked
3. **Try a different port** - Use 8001, 8080, or 3000
4. **Check logs** - Look for error messages in the terminal

---

**You're all set! 🚀**

