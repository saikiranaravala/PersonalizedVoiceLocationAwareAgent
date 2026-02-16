# Windows Installation Guide

## Prerequisites

1. **Python 3.11.9**
   - Download from: https://www.python.org/downloads/release/python-3119/
   - During installation, check "Add Python to PATH"
   - Verify installation:
     ```bash
     python --version
     ```

2. **Microphone** (for voice mode)
   - Ensure microphone is connected and set as default device
   - Check: Settings > Privacy > Microphone > Allow apps to access

3. **Internet Connection**
   - Required for speech recognition and API calls

## Installation Steps

### 1. Extract the Project

Extract the zip file to a location like:
```
C:\Users\YourName\personalized-agentic-assistant\
```

### 2. Open Command Prompt

- Press `Win + R`
- Type `cmd` and press Enter
- Navigate to the project folder:
  ```bash
  cd C:\Users\YourName\personalized-agentic-assistant
  ```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

```bash
venv\Scripts\activate
```

You should see `(venv)` at the start of your command line.

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with `pyaudio`, you may need to install it separately:

```bash
pip install pipwin
pipwin install pyaudio
```

Alternatively, download the wheel file from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Then install it:
```bash
pip install PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl
```

### 6. Configure API Keys

1. Copy the example environment file:
   ```bash
   copy config\.env.example config\.env
   ```

2. Edit `config\.env` with Notepad or any text editor:
   ```bash
   notepad config\.env
   ```

3. Add your API keys:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   LANGSMITH_API_KEY=your-langsmith-key-here
   ```

4. Save and close the file

### 7. Test the Installation

Run the test suite to ensure everything is set up correctly:

```bash
pytest tests/ -v
```

### 8. Launch the Application

**Option A: Using the batch file (easiest)**
```bash
start.bat
```

**Option B: Using Python directly**
```bash
python src\main.py
```

**Option C: Text-only mode (no voice)**
```bash
python src\main.py --no-voice
```

## Troubleshooting

### Microphone Not Working

1. Check Windows microphone permissions:
   - Settings > Privacy > Microphone
   - Enable "Allow apps to access your microphone"

2. Set default microphone:
   - Right-click speaker icon in taskbar
   - Select "Sounds"
   - Go to "Recording" tab
   - Set your microphone as default

3. Test microphone:
   - Run the app
   - Type `test` to test microphone

### ImportError for pyaudio

If you get an error about `pyaudio`:

```bash
pip uninstall pyaudio
pipwin install pyaudio
```

Or use the pre-compiled wheel as described in step 5.

### OpenAI API Key Error

Make sure your `.env` file is in the `config` folder and contains:
```
OPENAI_API_KEY=sk-...
```

Do NOT commit this file to version control!

### Module Not Found Errors

Make sure the virtual environment is activated:
```bash
venv\Scripts\activate
```

Then reinstall dependencies:
```bash
pip install -r requirements.txt
```

### Speech Recognition Not Working

- Ensure you have an active internet connection
- Google Speech Recognition API is used (requires internet)
- Try speaking more clearly or adjusting microphone volume

## Updating the Application

To update dependencies:

```bash
venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

## Uninstallation

1. Deactivate virtual environment:
   ```bash
   deactivate
   ```

2. Delete the project folder

## Getting API Keys

### OpenAI API Key (Required)
1. Go to: https://platform.openai.com/api-keys
2. Create an account or log in
3. Click "Create new secret key"
4. Copy the key and paste it in `config\.env`

### LangSmith API Key (Optional)
1. Go to: https://smith.langchain.com
2. Create an account
3. Go to Settings > API Keys
4. Create a new API key
5. Copy the key and paste it in `config\.env`

### Zomato API Key (Optional)
1. Go to: https://developers.zomato.com/api
2. Sign up for an API key
3. Copy the key and paste it in `config\.env`

Note: Without Zomato API key, the app will use mock restaurant data for demonstration purposes.

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=src --cov-report=html
```

View coverage report:
```bash
start htmlcov\index.html
```

## Need Help?

- Check the main README.md for usage examples
- Review logs in the `logs` folder
- Check console output for error messages
