from flask import Flask, render_template, request, redirect, url_for
import hvac
import yaml
import os

app = Flask(__name__)

# Vault configuration
VAULT_ADDR = os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200')
VAULT_TOKENS_FILE = os.getenv('VAULT_TOKENS_FILE', '/vault/secrets/tokens.yaml')
VAULT_TOKEN = os.getenv('VAULT_TOKEN')

client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

@app.route('/')
def index():
    # Load tokens from YAML file
    with open(VAULT_TOKENS_FILE, 'r') as f:
        config = yaml.safe_load(f)
        tokens = config.get('tokens', [])

    token_info_list = []
    for token in tokens:
        accessor = token['accessor']
        name = token.get('name', 'No name')
        try:
            # Lookup token information using accessor
            lookup_response = client.auth.token.lookup_accessor(accessor)
            data = lookup_response['data']
            policies = data.get('policies', [])
            expiration_time = data.get('expire_time', 'N/A')
            token_info_list.append({
                'name': name,
                'accessor': accessor,
                'expiration_time': expiration_time,
                'policies': policies
            })
        except hvac.exceptions.InvalidRequest:
            # Handle invalid accessors
            token_info_list.append({
                'name': name,
                'accessor': accessor,
                'expiration_time': 'Invalid Accessor',
                'policies': []
            })
    return render_template('index.html', tokens=token_info_list)

@app.route('/renew', methods=['POST'])
def renew():
    accessor = request.form.get('accessor')
    try:
        # Renew token using accessor
        client.auth.token.renew_accessor(accessor)
    except hvac.exceptions.InvalidRequest as e:
        pass  # Handle exception if needed
    return redirect(url_for('index'))

@app.route('/invalidate', methods=['POST'])
def invalidate():
    accessor = request.form.get('accessor')
    try:
        # Invalidate token using accessor
        client.auth.token.revoke_accessor(accessor)
    except hvac.exceptions.InvalidRequest as e:
        pass  # Handle exception if needed
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
