# XFAIR

MIT 1.125 term project. Project scope and workflow will be added here.

## Local setup

This workspace uses Python 3.15.0. The installed packages are
`openai==3.53.0` and `PyYAML==6.0.3`.

To recreate the environment from the project folder, run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install openai==3.53.0 PyYAML==6.0.3
```

The model check reads `OPENAI_API_KEY` from your environment. If you need to
set it up later, create a private file with `touch .env && chmod 600 .env`.
Open it in a local editor and add `export OPENAI_API_KEY='YOUR_KEY_HERE'`,
replacing the placeholder with your key. Save the file and run `source .env`
in the same terminal before running the check. Git ignores `.env`. Keep
the key out of chat, screenshots, terminal commands, and commits.

Run the model check from the project folder:

```sh
.venv/bin/python -m components.check_model
```
