💬 Go to the home directory
cd
💬 Create a directory for all your code projects
mkdir code
💬 Enter into that code directory
cd code
💬 Create a directory for this project
mkdir awesome-project
💬 Enter into that project directory
cd awesome-project


To create a virtual environment, you can use the venv module that comes with Python.
python -m venv .venv

Activate the Virtual Environment
source .venv/bin/activate

Install required packages by running
pip install -r requirement.txt

start the server by running
fastapi dev main.py

To see the API docs and create entries
http://127.0.0.1:8000/docs#/

To see SQlite database
Go to SQLite Online. -> https://sqliteonline.com/
Upload your test.db file.
Run queries directly in the browser.
