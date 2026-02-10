# IBM Quantum Credentials Setup Guide

This guide will help you set up your IBM Quantum credentials to run the ABENA quantum hardware tests.

## 📋 Quick Start

### Option 1: Use the Setup Helper Script (Recommended)

```bash
cd quantum-healthcare
python setup_ibm_credentials.py
```

This interactive script will:
- ✅ Check existing credentials
- ✅ Test your connection
- ✅ Help you save new credentials
- ✅ Verify everything works

### Option 2: Test Existing Credentials

```bash
python setup_ibm_credentials.py --test
```

### Option 3: Save Token Directly

```bash
python setup_ibm_credentials.py --token YOUR_API_TOKEN_HERE
```

## 🔑 Getting Your IBM Quantum API Token

### Step 1: Create/Login to IBM Quantum Account

1. Go to **https://quantum.ibm.com/**
2. Click **"Sign in"** or **"Get started"**
3. Use your IBM ID or create a new account (it's free!)

### Step 2: Generate API Token

1. After logging in, click your **profile icon** (top right corner)
2. Select **"My account"** or **"Account settings"**
3. Navigate to **"API token"** section
4. Click **"Generate token"** if you don't have one
5. **Copy the token immediately** (you'll only see it once!)

### Step 3: Save Your Token

You can save it using any of these methods:

#### Method A: Using the Setup Script (Easiest)
```bash
python setup_ibm_credentials.py --token YOUR_TOKEN_HERE
```

#### Method B: Using Python Directly
```python
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(
    channel='ibm_quantum_platform',
    token='YOUR_TOKEN_HERE'
)
```

#### Method C: Environment Variable
```bash
# Windows PowerShell
$env:QISKIT_IBM_TOKEN="YOUR_TOKEN_HERE"

# Windows CMD
set QISKIT_IBM_TOKEN=YOUR_TOKEN_HERE

# Linux/Mac
export QISKIT_IBM_TOKEN="YOUR_TOKEN_HERE"
```

#### Method D: Manual Config File
Create/edit: `C:\Users\YourUsername\.qiskit\qiskit-ibm.json`

```json
{
    "default-ibm-quantum-platform": {
        "channel": "ibm_quantum_platform",
        "token": "YOUR_TOKEN_HERE",
        "url": "https://cloud.ibm.com"
    }
}
```

## ✅ Verify Your Setup

Run the test script:

```bash
python setup_ibm_credentials.py --test
```

You should see:
- ✅ Connection successful
- ✅ List of available quantum backends
- ✅ Backend status information

## 🚀 Run the Hardware Test

Once credentials are configured:

```bash
python abena_quantum_hardware_test.py
```

This will:
1. Connect to IBM Quantum
2. Select a quantum backend (ibm_fez)
3. Create a healthcare optimization circuit
4. Submit job to real quantum hardware
5. Wait for results (5-20 minutes)
6. Display results and documentation

## 🐛 Troubleshooting

### Error: "Unable to retrieve instances. Please check that you are using a valid API token."

**Solutions:**
1. ✅ Verify your token is correct (no extra spaces)
2. ✅ Check if token has expired (generate a new one)
3. ✅ Ensure you're using `ibm_quantum_platform` channel
4. ✅ Check your internet connection

### Error: "channel can only be 'ibm_cloud', or 'ibm_quantum_platform'"

**Solution:**
- The script already uses the correct channel. If you see this, update your Qiskit:
  ```bash
  pip install --upgrade qiskit-ibm-runtime
  ```

### Error: UnicodeEncodeError (Windows)

**Solution:**
- Already fixed in the script! The script handles Windows console encoding automatically.

### Token Not Found

**Solution:**
1. Run the setup script: `python setup_ibm_credentials.py`
2. Or check if file exists: `%USERPROFILE%\.qiskit\qiskit-ibm.json`
3. Verify the token is saved correctly

## 📚 Additional Resources

- **IBM Quantum Documentation:** https://docs.quantum.ibm.com/
- **Qiskit Documentation:** https://qiskit.org/documentation/
- **IBM Quantum Platform:** https://quantum.ibm.com/
- **Qiskit Runtime Service:** https://docs.quantum.ibm.com/api/qiskit-ibm-runtime/qiskit_ibm_runtime.QiskitRuntimeService

## 🔒 Security Notes

- ⚠️ **Never commit your API token to git!**
- ⚠️ **Keep your token private and secure**
- ✅ The `.qiskit` folder is in your home directory (not in the project)
- ✅ Tokens are stored locally on your machine only

## 💡 Tips

1. **Free Tier:** IBM Quantum offers free access with limited credits
2. **Job Queue:** Some backends have long queues. The script uses `ibm_fez` which typically has shorter wait times
3. **Results:** Job results are stored on IBM Quantum and can be retrieved later using the Job ID
4. **Multiple Accounts:** You can save multiple accounts in the config file with different names

## 📞 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Run `python setup_ibm_credentials.py --test` to diagnose
3. Verify your token at https://quantum.ibm.com/
4. Check Qiskit version: `pip show qiskit-ibm-runtime`

