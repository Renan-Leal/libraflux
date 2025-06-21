# PyNest service

This is a template for a PyNest service.

## Start Service

## Step 1 - Create environment

- install requirements:

```bash
pip install -r requirements.txt
```

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

## Commit message convention

Use the following commit message prefixes to standardize your commits:

- **fix:** message describing a bug fix  
  _Example:_ `fix: correct book category parsing`

- **refactor:** message describing a code refactor  
  _Example:_ `refactor: improve scraping service structure`

- **conf:** message describing configuration changes  
  _Example:_ `conf: update .env example and logging config`

- **doc:** message describing documentation changes  
  _Example:_ `doc: update README with usage instructions`

- **feat:** message describing a new feature or implementation  
  _Example:_ `feat: add endpoint for book search`
