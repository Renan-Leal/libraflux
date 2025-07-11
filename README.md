# Start Service

## Step 1 - Create environment

- install requirements:

```bash
pip install -r requirements.txt
```

- Create a `.env` file in the project root.  
  Copy all variables from `.env.example` and change the values as needed for your environment.

## Step 2 - start service local

1. Run service with main method

```bash
python main.py
```

2. Run service using uvicorn

```bash
uvicorn "app:app" --host "0.0.0.0" --port "8000" --reload
```

## Step 3 - Send requests

Go to the fastapi docs and use your api endpoints - http://127.0.0.1/docs


## Project Structure and Contribution Guidelines

## Code linting and formatting

To ensure code quality and consistency, run the following script from the project root:

```bash
./lint.sh
```

This script will:
- Format your code using **Black**
- Run **pylint** to check for code issues

Make sure to run this script before committing your changes.

## Commit message convention

Use the following commit message prefixes to standardize your commits:

- **fix:** message describing a bug fix  
  _Example:_ `fix: correct book category parsing`

- **refactor:** message describing a code refactor  
  _Example:_ `refactor: improve scraping service structure`

- **config:** message describing configuration changes  
  _Example:_ `config: update .env example and logging config`

- **doc:** message describing documentation changes  
  _Example:_ `doc: update README with usage instructions`

- **feat:** message describing a new feature or implementation  
  _Example:_ `feat: add endpoint for book search`

