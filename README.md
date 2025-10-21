## Creating an agenticAI project wtih poetry

> poetry new <project>

Poetry create a basic python project structure with src and tests folders, README.md and pyproject.toml for poetry project setting

<project>/
├── pyproject.toml
├── README.md
├── <project>/
│   └── __init__.py
└── tests/
    └── __init__.py

## Add mainly dependencies 

You can add any package you need using poetry add

--- for fastpi <backend> and uvicorn <server>

> poetry add requests python-dotenv fastapi uvicorn

## Create a .env file

This is for include the environment setting for using an specifc llm
 
Include this into the .env according the model you want o use
# ==== Model settings ====
MODEL_PROVIDER="ollama"   
# or "openai"

# ==== Ollama ====
OLLAMA_API_URL="http://localhost:11434/api"
OLLAMA_MODEL="llama2"

# ==== OpenAI ====
OPENAI_API_KEY="sk-your-openai-key"
OPENAI_MODEL="gpt-4o-mini"

##  for using jupyter notebooks files for testing

# install it
> poetry add --dev jupyter

# run it
> poetry run jupyter lab

#  for using ollama instead of openai, crew ai use openai by defect

> poetry add litellm
>