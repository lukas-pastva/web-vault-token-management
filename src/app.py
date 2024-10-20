from flask import Flask, render_template, request, redirect, url_for, flash
import hvac
import yaml
import os
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'asdf')

# Vault configuration
VAULT_ADDR = 
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
            expire_time_str = data.get('expire_time')
            if expire_time_str and expire_time_str != 'N/A':
                expire_time = parser.isoparse(expire_time_str)
                now = datetime.utcnow()
                delta = expire_time - now
                weeks = delta.days // 7
                expiration_display = f"{weeks} weeks"
            else:
                expiration_display = 'N/A'
            token_info_list.append({
                'name': name,
                'accessor': accessor,
                'expiration_time': expiration_display,
                'policies': policies
            })
        except hvac.exceptions.Forbidden:
            # Handle permission errors
            token_info_list.append({
                'name': name,
                'accessor': accessor,
                'expiration_time': 'Permission Denied',
                'policies': []
            })
        except hvac.exceptions.InvalidRequest:
            # Handle invalid accessors
            token_info_list.append({
                'name': name,
                'accessor': accessor,
                'expiration_time': 'Invalid Accessor',
                'policies': []
            })
        except Exception as e:
            # Handle other exceptions
            token_info_list.append({
                'name': name,
                'accessor': accessor,
                'expiration_time': f'Error: {str(e)}',
                'policies': []
            })
    return render_template('index.html', tokens=token_info_list)

@app.route('/renew', methods=['POST'])
def renew():
    accessor = request.form.get('accessor')
    try:
        # Renew token using accessor by 3 months
        increment = '43800h'  # Approximately 3 months
        client.auth.token.renew_accessor(accessor, increment=increment)
        flash('Token successfully renewed by 3 months.', 'success')
    except hvac.exceptions.InvalidRequest as e:
        flash(f'Failed to renew token: {str(e)}', 'danger')
    except hvac.exceptions.Forbidden as e:
        flash(f'Permission denied: {str(e)}', 'danger')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/invalidate', methods=['POST'])
def invalidate():
    accessor = request.form.get('accessor')
    try:
        # Invalidate token using accessor
        client.auth.token.revoke_accessor(accessor)
        flash('Token successfully invalidated.', 'success')
    except hvac.exceptions.InvalidRequest as e:
        flash(f'Failed to invalidate token: {str(e)}', 'danger')
    except hvac.exceptions.Forbidden as e:
        flash(f'Permission denied: {str(e)}', 'danger')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
