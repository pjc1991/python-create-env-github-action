# Python Create .env For GitHub Actions

## What is this?
This is a simple python script that creates a .env file for GitHub Actions.
All of your secrets from .env in your local machine will be copied to GitHub Actions.
and your workflow will be edited to use the secrets from GitHub Actions by creating .env file at the GitHub Actions Runner.

## Why did you make this?

I was tired of copying and pasting my .env file to GitHub Actions, and updating my workflow with tons of echo commands.

## What does this script solve?

1. You don't have to copy and paste your .env file to GitHub Actions.
2. You don't have to update your workflow file with echo commands.
3. .env file will be created at GitHub Actions Runner, so you don't have to worry about your .env file being exposed to the public.
4. Whenever you modify your .env file, you can run this script again to update your GitHub Secrets and your workflow file.

## How does it work?

1. This script will read your .env file and upload every secret to GitHub Actions, except for secrets that start with ___.
2. This script will read your workflow file and fine the step named "CREATE_DOT_ENV_FILE". (If you don't have this step, please add it.)
3. CREATE_DOT_ENV_FILE's run command will be replaced with a command that creates .env file with secrets from GitHub Actions.
4. Because GitHub Hosted Runner have your .env file, every deployment step will be able to use your secrets.
5. Whenever you modify your .env file, you can run this script again to update your GitHub Secrets and your workflow file.

## How to use?

### 1. Clone this repository

```shell
git clone https://github.com/pjc1991/python-create-env-github-action.git
```

### 2. copy create_dotenv.py, requirements.txt to your project

```shell
cp python-create-env-github-action/create_dotenv.py {your-project-path}
cp python-create-env-github-action/requirements.txt {your-project-path} 
# if your project is using python already, you shouldn't copy requirements.txt
# just install required libraries to your project's virtual environment on your own
# or you could make second virtual environment for this script only. (Really?)
# Actually, if your project is using python, copying and pasting create_dotenv.py to your project will be enough.
```

### 3. Install python3.9 and create virtual environment (if you don't have one already)

```shell
sudo apt install python3.9
# if you don't have python3.9 already

python3.9 -m venv venv
source venv/bin/activate && python3.9 -m pip install -r requirements.txt
# only if you copied requirements.txt for virtual environment
```

### 4. Create .env file

```shell
touch .env
# if you don't have .env file already
```

```yaml
# .env
SECRET_KEY1=secret_key1
SECRET_KEY2=secret_key2
# the following secrets is required for this script to work
___GITHUB_REPOSITORY___=your_id_or_organization/your_repository
___GITHUB_TOKEN___=your_github_token_with_repo_scope_and_so_on
___GITHUB_ACTION_WORKFLOW_PATH___=.github/workflows/deploy.yml # example
# create_dotenv.py will not upload secrets that start with ___
```

### 5. Run main.py

```shell
python3.9 create_dotenv.py
```
