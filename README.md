# Python FastAPI Project for Story Teller

## Project Description
This is a Python project built using FastAPI, a modern, fast (high-performance) web framework for building APIs with Python 3.14+ based on standard Python type hints.

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── api/
│   |    ├── routes.py
│   |    └── __pycache__/
│   └── services
│   └── core
├── tests/
│   ├── test_main.py
│   └── __pycache__/
├── pyproject.toml
├── pytest.ini
└── .gitignore
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
run below command in
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/generate-story' \
  -F 'text=It is very interesting to watch the dragon boat racing.' \
  -F 'language=en' \
  -F 'voice_sample=@uploads/myvoice.wav' \
  --output outputs/final_test.wav
```

## Running Tests
To run the test suite, use:
```bash
poetry run pytest ./tests
```
