# Python FastAPI Project for Story Teller

## Project Description
This is a Python project built using FastAPI, a modern, fast (high-performance) web framework for building APIs with Python 3.14+ based on standard Python type hints.

## Project Structure
```
backend/
├── README.md
├── app
│   ├── __init__.py
│   ├── main.py
│   └── tts_engine.py
├── outputs
│   └── final_test.wav
├── poetry.lock
├── pyproject.toml
└── uploads
    ├── harvard.wav
    └── myvoice.wav
```

## Requirements
- Python 3.14+
- Poetry (for dependency management)

## Installation
1. Clone the repository:
   ```bash
   git clone git@github.com:xiaotaozi1127/story-teller-backend.git backend
   cd backend
   ```

 2. Install Poetry:
   Follow the instructions at [Poetry's official documentation](https://python-poetry.org/docs/#installation) to install Poetry.

3. Configure Poetry to create the virtual environment inside the project:
   ```bash
   poetry config virtualenvs.in-project true
   ```

4. Install dependencies:
   ```bash
   poetry install
   ```  
5. Set Python Interpreter in VSCode
if you encounter 'Import fastapi could not be resolved' issue, it seems that your Editor Is Not Using Poetry’s Virtualenv
   ```bash
   poetry env info --path
   ```  
Copy the path.
Set Python Interpreter
Cmd + Shift + P (Mac) 
Python: Select Interpreter
Paste or select the Poetry venv path
Restart VS Code.
✅ The FastAPI import error should disappear.


## Run the backend
To start the FastAPI application, run:
```bash
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
poetry run uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## Verify the speech generation
run below command to generate some English sound
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/stories/test-speech' \
  -F 'text=It is very interesting to watch the dragon boat racing.' \
  -F 'language=en' \
  -F 'voice_sample=@uploads/myvoice.wav' \
  --output outputs/final_test.wav
```

run below command to generate some Chinese sound
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/stories/test-speech' \
  -F 'text=我很喜欢这里的生活，人们都很友好，风景也很漂亮.' \
  -F 'language=zh' \
  -F 'voice_sample=@uploads/myvoice.wav' \
  --output outputs/chinese_test.wav
```

You should hear audio:
```bash
afplay outputs/chinese_test.wav   # macOS
```bash

## Verify the long story generation
run below command to generate audios by long text
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/stories/long-story' \
  -F 'text= on the wall, Who is the fairest one of all?”  And the mirror would reply:  “You, O Queen, are the fairest of all.”  This pleased her, for she knew the mirror spoke the truth.' \
  -F 'language=en' \
  -F 'chunk_size=300' \
  -F 'voice_sample=@uploads/myvoice.wav'
```

run below command to check the chunk status for a story
```bash
curl -v http://localhost:8000/stories/<id>/chunks/0 --output chunk0.wav
```

You should hear audio:
```bash
afplay chunk0.wav   # macOS
```

## Running Tests
To run the test suite, use:
```bash
poetry run pytest ./tests