from flask import Flask, render_template, request, redirect, url_for, flash
import hvac
import yaml
import os
from datetime import datetime, timezone
from dateutil import parser
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')  # Use environment variable for security

# Vault configuration
VAULT_ADDR = os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200')
VAULT_TOKENS_FILE = os.getenv('VAULT_TOKENS_FILE', '/vault/secrets/tokens.yaml')
VAULT_TOKEN = os.getenv('VAULT_TOKEN')

# Renewal increment configuration
TOKEN_RENEW_INCREMENT = os.getenv('TOKEN_RENEW_INCREMENT', '2160h')  # Default to 2160 hours (~3 months)

client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

@app.route('/')
def index():
    # Load tokens from YAML file
    try:
        with open(VAULT_TOKENS_FILE, 'r') as f:
            config = yaml.safe_load(f)
            tokens = config.get('tokens', [])
    except FileNotFoundError:
        flash('Vault tokens file not found.', 'danger')
        tokens = []
    except yaml.YAMLError as e:
        flash(f'Error parsing YAML file: {str(e)}', 'danger')
        tokens = []

    token_info_list = []
    for token in tokens:
        accessor = token.get('accessor')
        name = token.get('name', 'No name')
        if not accessor:
            token_info_list.append({
                'name': name,
                'accessor': 'N/A',
                'expiration_time_display': 'N/A',
                'actual_expiration_time': 'N/A',
                'policies': [],
                'is_expiring_soon': False
            })
            continue

        try:
            # Lookup token information using accessor
            lookup_response = client.auth.token.lookup_accessor(accessor)
            data = lookup_response['data']
            policies = data.get('policies', [])
            expire_time_str = data.get('expire_time')

            if expire_time_str and expire_time_str != 'N/A':
                expire_time = parser.isoparse(expire_time_str)
                now = datetime.now(timezone.utc)
                delta = expire_time - now

                # Calculate weeks remaining
                weeks = delta.days // 7
                # Format actual expiration time
                actual_expiration = expire_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                expiration_display = f"{weeks} weeks"

                # Determine if expiring soon (within 30 days)
                is_expiring_soon = delta.days < 30 and delta.total_seconds() > 0

                # Handle past expiration
                if delta.total_seconds() < 0:
                    expiration_display = "Expired"
                    actual_expiration = expire_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                    is_expiring_soon = False  # Already expired

            else:
                expiration_display = 'N/A'
                actual_expiration = 'N/A'
                is_expiring_soon = False

            token_info_list.append({
                'name': name,
                'accessor': accessor,
                'expiration_time_display': expiration_display,
                'actual_expiration_time': actual_expiration,
                'policies': policies,
                'is_expiring_soon': is_expiring_soon
            })
        except hvac.exceptions.Forbidden:
            # Handle permission errors
            token_info_list.append({
                'name': name,
                'accessor': accessor,
                'expiration_time_display': 'Permission Denied',
                'actual_expiration_time': 'Permission Denied',
                'policies': [],
                'is_expiring_soon': False
            })
        except hvac.exceptions.InvalidRequest:
            # Handle invalid accessors
            token_info_list.append({
                'name': name,
                'accessor': accessor,
                'expiration_time_display': 'Invalid Accessor',
                'actual_expiration_time': 'Invalid Accessor',
                'policies': [],
                'is_expiring_soon': False
            })
        except Exception as e:
            # Handle other exceptions
            token_info_list.append({
                'name': name,
                'accessor': accessor,
                'expiration_time_display': f'Error: {str(e)}',
                'actual_expiration_time': f'Error: {str(e)}',
                'policies': [],
                'is_expiring_soon': False
            })
    return render_template('index.html', tokens=token_info_list)

@app.route('/renew', methods=['POST'])
def renew():
    accessor = request.form.get('accessor')
    if not accessor:
        flash('No accessor provided for renewal.', 'danger')
        return redirect(url_for('index'))

    try:
        # Renew token using accessor by the configured increment
        client.auth.token.renew_accessor(accessor, increment=TOKEN_RENEW_INCREMENT)
        flash('Token successfully renewed.', 'success')
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
    if not accessor:
        flash('No accessor provided for invalidation.', 'danger')
        return redirect(url_for('index'))

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
