# 🧪 TestDevoApp

A minimal fullstack Next.js application designed to test CI/CD pipelines with intentional failures for **Devo log collection and analysis**.

## 🎯 Purpose

This app is specifically designed to:
- ✅ **Pass CI** with normal inputs
- ⚠️ **Generate warnings** with specific inputs  
- ❌ **Fail CI** with certain commands to trigger Devo log collection
- 📊 **Provide real logs** for testing Graph-RAG pipelines

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

### Testing Commands

The app responds differently based on input:

| Command | App Behavior | CI Behavior |
|---------|-------------|-------------|
| `hello` | ✅ Success response | CI passes |
| `warn` | ⚠️ Warning logged | CI shows warnings |
| `fail` | ❌ Error thrown | CI fails |

## 🏗️ Architecture

```
src/
├── app/
│   ├── page.js                 # Main UI (input form)
│   └── api/command/route.js    # API endpoint
tests/
└── command.test.js             # Test scenarios
.github/workflows/
└── ci.yml                      # CI/CD pipeline
db.txt                          # File-based storage
```

## 🧪 Testing Scenarios

### Run Tests Locally
```bash
# Normal tests (should pass)
npm test

# Tests with warnings
npm test

# Tests with intentional failures
TRIGGER_FAIL=true npm test
```

### Trigger CI Failures

Include `[trigger-fail]` in your commit message:
```bash
git commit -m "test: [trigger-fail] trigger intentional failure"
git push
```

## 📊 Devo Integration

### Collect Failed CI Logs

Use the existing Devo collector to fetch GitHub Actions logs:

```python
# Example using your ci_cd_collector.py
from collectors.ci_cd_collector import router

# Fetch logs from failed CI run
logs = fetch_github_actions_logs(
    repo="your-username/devo",
    run_id=12345,  # From failed CI run
    token="your-github-token"
)
```

### Log Analysis

The app generates structured logs that include:
- 📅 Timestamps
- 🏷️ Command types (normal/warn/fail)
- 📝 Error messages
- 🔄 CI run metadata

## 🎮 Usage Examples

### 1. Normal Operation
```
Input: "hello"
Response: ✅ Success: Command processed successfully
CI: Passes ✅
```

### 2. Warning Scenario  
```
Input: "warn"
Response: ✅ Success: Command processed with warning
CI: Shows warnings ⚠️
```

### 3. Failure Scenario
```
Input: "fail"
Response: ❌ Error: Intentional failure triggered
CI: Fails ❌ (ready for Devo collection)
```

## 🔧 Configuration

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `TRIGGER_FAIL` | Force test failures | `true` |
| `INTENTIONAL_FAIL` | Control specific test behavior | `true` |

### File Storage

Commands are logged to `db.txt`:
```
[2025-06-21T10:30:00.000Z] Command: hello
[2025-06-21T10:30:00.000Z] SUCCESS: Command processed successfully
[2025-06-21T10:31:00.000Z] Command: fail
[2025-06-21T10:31:00.000Z] ERROR: Intentional failure triggered
```

## 🤖 CI/CD Pipeline

The GitHub Actions workflow includes:

- 🧪 **Multiple test scenarios** (normal, warning, failure)
- 🏗️ **Build verification**
- 🔍 **Code linting**
- 📊 **Artifact collection**
- ❌ **Intentional failure triggers**

### Matrix Strategy

The CI runs three parallel jobs:
- `normal`: All tests pass
- `warning`: Tests pass with warnings
- `failure`: Tests intentionally fail

## 📈 Success Criteria

- ✅ Normal inputs result in CI success
- ⚠️ Warning inputs generate observable warnings
- ❌ Failure inputs cause CI failures with collectible logs
- 📊 Logs are structured for Graph-RAG analysis
- 🔄 Devo collector can successfully fetch failure logs

## 🔗 Integration with Main Devo Project

This TestDevoApp works with your existing Devo collectors:

```python
# collectors/ci_cd_collector.py can fetch these logs
# Use the GitHub run ID from failed CI runs
```

## 📝 Development Notes

- Built with **Next.js 15** and **React 19**
- Uses **Tailwind CSS** for styling
- **Jest** for testing
- **File-based storage** for simplicity
- **GitHub Actions** for CI/CD

## 🎯 Next Steps

1. 🚀 **Deploy** to see CI/CD in action
2. 🧪 **Trigger failures** using commit messages
3. 📊 **Collect logs** using Devo
4. 🤖 **Analyze** with Graph-RAG pipeline

---

**Ready to test your Devo log collection pipeline!** 🚀
