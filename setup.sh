# [CockroachDB] download CA cert for server certificate verification
# NOTE: Only compatible with Linux or Mac
curl --create-dirs -o $HOME/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/1734f6a0-3ba8-49ef-8642-d823b77d7abd/cert'

# Set up virtual environment, activate, and install requirements
python3 -m venv diversavenv
source diversavenv/bin/activate
pip install -r requirements.txt