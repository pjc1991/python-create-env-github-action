import base64
import json
import os
from base64 import b64encode

import requests
import ruamel.yaml as yaml
from dotenv import load_dotenv
from nacl import encoding, public

load_dotenv()


# get the list of environment variables from the .env file
# not the values, just the names
def get_env_vars():
    env_var_list = []
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("___"):
                continue
            if line.startswith("#"):
                continue
            if line.startswith("\n"):
                continue
            if "=" in line:
                env_var_list.append(line.split("=")[0])
    return env_var_list


# create string to be used on GitHub Actions workflow file
# ex) echo "VARIABLE_1=${{ secrets.VARIABLE_1 }}" >> .env
#     echo "VARIABLE_2=${{ secrets.VARIABLE_2 }}" >> .env
def create_env_string(env_var_list):
    echo_env_string = ""
    for variable in env_var_list:
        echo_env_string += f"echo \"{variable}=${{{{ secrets.{variable} }}}}\" >> .env\n"
    return echo_env_string


# format secrets to be used for GitHub API
# by base64 encoding the string
def format_secret(secret):
    return base64.b64encode(secret.encode("utf-8")).decode("utf-8")


# add environment variables to GitHub Secrets
# using GitHub API
def create_secret(repository_name, secret_name, secret_value, github_token):
    public_key = get_public_key(repository_name, github_token)
    encrypted_value = encrypt_secret(public_key['key'], secret_value)

    url = f"https://api.github.com/repos/{repository_name}/actions/secrets/{secret_name}"
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    data = {
        'encrypted_value': encrypted_value,
        'key_id': public_key['key_id'],
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    return response


def get_public_key(repository_name, github_token):
    url = f"https://api.github.com/repos/{repository_name}/actions/secrets/public-key"
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    response = requests.get(url, headers=headers)
    return response.json()


def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


if __name__ == "__main__":
    # get the list of environment variables from the .env file
    print("Step 1. Getting environment variables from .env file")
    env_vars = get_env_vars()

    # create string to be used on GitHub Actions workflow file
    print("Step 2. Creating string to be used on GitHub Actions workflow file")
    env_string = create_env_string(env_vars)

    # add environment variables to GitHub Secrets
    # using GitHub API
    repo = os.environ["___GITHUB_REPOSITORY___"]
    token = os.environ["___GITHUB_TOKEN___"]
    print("Step 3. Adding environment variables to GitHub Secrets via GitHub API")
    for var in env_vars:
        # Get the value of the environment variable from os.environ
        value = os.getenv(var)
        # print(f"{var}={value}")
        print(f"::Adding {var}=*** ")
        # format the secret to be used for GitHub API
        create_secret(repo, var, value, token)

    # print the string to the workflow file
    print("Step 4. Printing the string to the workflow file")
    workflow_file = os.getenv("___GITHUB_ACTION_WORKFLOW_PATH___")
    # if workflow file is not specified, print to .txt file
    if workflow_file is None:
        print("!! GITHUB_ACTION_WORKFLOW_PATH is not specified. Printing to echo_env.txt!! ")
        output_file = "echo_env.txt"
        exit()

    yaml = yaml.YAML()
    yaml.preserve_quotes = False

    # if workflow file is specified, print to the workflow file using yaml
    with open(workflow_file, "r") as f:
        text = f.read()
        workflow = yaml.load(text)

        if workflow is None or workflow == "":
            raise Exception("workflow file is empty")

        # jobs.build.steps
        # find name "CREATE_DOT_ENV_FILE"
        # add run: echo_env_string
        print("Step 5, Writing to workflow file by yaml")
        is_updated = False
        for step in workflow["jobs"]["build"]["steps"]:
            if step["name"] == "CREATE_DOT_ENV_FILE":
                step["run"] = env_string
                print("CREATE_DOT_ENV_FILE step updated")
                is_updated = True
                break

    if not is_updated:
        raise Exception("CREATE_DOT_ENV_FILE step not found")

    with open(workflow_file, "w") as f:
        yaml.dump(workflow, f)
        print("Workflow file updated")

    print("Everything is done!, please check the workflow file and everything is working fine")
