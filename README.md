# FastAPI-Boilerplate

## Installing dependencies
### Using Docker Compose
if you don't have a docker, you can install it.
This installation guide is tailored to the Ubuntu environment.
```sh
# Remove existing environment to avoid collision
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```sh
docker compose up --build
```


### Using uv
if you don't have a uv, you can install int.
```sh
# Install uv with our standalone installers:
curl -LsSf https://astral.sh/uv/install.sh | sh # On macOS and Linux.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" # On Windows.

# Or, from PyPI:
pip install uv # With pip.
pipx install uv # Or pipx.

uv sync
```

### Using venv
if you don't have a venv, you can install it.
```sh
sudo apt install python3.10-venv -y     # You can also another python version
python3 -m venv .env
source .env/bin/activate                # if you use Linux
pip install -r requirements.txt
```

### Using Conda
if you don't have a miniconda(or anaconda), you can install it on this url.
https://docs.anaconda.com/free/miniconda/index.html

```sh
conda create -n venv python=3.12
conda activate venv
pip install -r requirements.txt
```

After that, follow the steps below:

## usage
```sh
uv run main.py
```

or

```sh
uvicorn main:app
```

or

```sh
python main.py
```

## Structure

```sh
FastAPI-Boilerplate
├─README.md # Project introduction, etc.
├─uv.lock # Storing dependency information
├─pre-commit-config.yaml # Define git commit hook
├─alembic.ini # Database migration configuration
├─Dockerfile # Dockerfile
├─docker-compose.yml # Docker Compose File
├─main.py # Backend execution entry point
├─logs # Logs are saved at runtime (automatically generated)
├─.github # GitHub Settings
│  ├─ISSUE_TEMPLATE # Issue, PR Template
│  └─workflows # Github Action
├─src
│  ├─application
│  │  └─api
│  │      └─v1 # If you develop a new version, copy the directory and change the folder name.
│  │         ├─common # Used for common schema (or DTO) settings, etc.
│  │         └─service # Develop APIs here (separated by tags)
│  │            ├─auth # Login and other authentication related (using "FastAPI User")
│  │            └─sample # Implement the folder in this format as a sample structure
│  │                ├─sample_route.py # Define routing
│  │                ├─sample_schema.py # Define the schema (DTO) of the request and response
│  │                └─sample_service.py # Service layer Write the detailed implementation here
│  ├─core
│  │  ├─config # Managing variables related to settings, etc.
│  │  └─security # Define auth, jwt handlers, etc. required for security (use when necessary)
│  ├─crud # Database control CRUD implementation, etc.
│  ├─decorator # Implementation of decorators that are used throughout the implementation
│  ├─infrastructure # Control over the ancillary infrastructure required for operation, excluding the backend server.
│  │  ├─celery
│  │  │  └─tasks
│  │  ├─database
│  │  │  ├─models.py # Defining database table structure, etc.
│  │  │  └─migration # Database migration, version management, etc.
│  │  │     └─versions
│  │  └─redis
│  ├─middleware # Defining new middleware required for operation
│  └─utils
│     └─starlette_admin # Admin Panel
│         └─view # Admin Panel Components
└─test
```
For some files, the file name and variable name must be unified.

For example, to add a new route, there must be `src/application/api/{version}/service/{dir_name}/{something}_route.py` and an APIRouter called router in that folder.

# Dependency
This project implements some of its features through the following dependencies:

- Certification
    - [FastAPI Users](https://fastapi-users.github.io/fastapi-users/latest/)
- Admin Panel
    - [Starlette Admin](https://jowilf.github.io/starlette-admin/)

# How to Migrate Databases
This project uses Alembic as the database migration tool.
If you have a separate development database and a separate service database, you can migrate the database in the following order:

1. Configure models.py from the development database server.
This can be easily done using tools such as sqlacodegen.
This operation will cause differences between the server of sqlalchemy.url defined in alembic.ini and models.py.

3. To update the definition of migration (src/infrastructure/database/migration), you can use a command such as `alembic revision --autogenerate -m "{commit msg}"` to newly define the version according to the changed models.py.

4. This can be applied to the deployment database through `alembic upgrade head`.

5. If it is incorrect, you can restore it using a command such as `alembic downgrade -{num}`.

# How to Contribution
Git hook scripts are useful for identifying simple issues before submission to code review. We run our hooks on every commit to automatically point out issues in code such as missing semicolons, trailing whitespace, and debug statements. By pointing these issues out before code review, this allows a code reviewer to focus on the architecture of a change while not wasting time with trivial style nitpicks.

## Installation pre-commit
Before you can run hooks, you need to have the pre-commit package manager installed.

Using pip:

```sh
pip install pre-commit

pre-commit --version
# pre-commit x.y.z

pre-commit install
# pre-commit installed at .git/hooks/pre-commit
```
