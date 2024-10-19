# web-vault-token-management
A web page for reneweing and revoking Hashicorp Vault tokens

# Vault Token Management Web Application

This web application allows you to view and manage HashiCorp Vault tokens defined in a YAML configuration file. It provides a user-friendly interface to display token details, renew tokens, and invalidate (revoke) tokens as needed.

## Table of Contents

- [Features](#features)
- [Configuration](#configuration)
  - [1. `tokens.yaml`](#1-tokensyaml)
  - [2. `policy.hcl`](#2-policyhcl)
- [Environment Variables](#environment-variables)
- [Notes](#notes)

## Features

- **View Tokens:** Display a list of Vault tokens with descriptions, accessors, expiration dates, and bound policies.
- **Renew Tokens:** Renew tokens to extend their expiration.
- **Invalidate Tokens:** Revoke tokens to immediately invalidate them.
- **Responsive Design:** Optimized for both desktop and mobile devices using Bootstrap.

## Configuration

### 1. `tokens.yaml`

The `tokens.yaml` file defines the Vault tokens that the application will manage. Each token entry includes a description and its corresponding accessor.

#### Example `tokens.yaml`

```yaml
- description: "Token for Application A"
  accessor: "s.HASHED_ACCESSOR_VALUE_1"

- description: "Token for Application B"
  accessor: "s.HASHED_ACCESSOR_VALUE_2"

# Vault Token Management Web Application

This web application allows you to view and manage HashiCorp Vault tokens defined in a YAML configuration file. It provides a user-friendly interface to display token details, renew tokens, and invalidate (revoke) tokens as needed.

## Features

- **View Tokens:** Display a list of Vault tokens with descriptions, accessors, expiration dates, and bound policies.
- **Renew Tokens:** Renew tokens to extend their expiration.
- **Invalidate Tokens:** Revoke tokens to immediately invalidate them.
- **Responsive Design:** Optimized for both desktop and mobile devices using Bootstrap.

## Configuration
#### Example `tokens.yaml`

```yaml
- description: "Token for Application A"
  accessor: "s.HASHED_ACCESSOR_VALUE_1"

- description: "Token for Application B"
  accessor: "s.HASHED_ACCESSOR_VALUE_2"
```

#### Example policy.hcl
```yaml
# policy.hcl

path "auth/token/lookup-accessor" {
  capabilities = ["update"]
}

path "auth/token/renew-accessor" {
  capabilities = ["update"]
}

path "auth/token/revoke-accessor" {
  capabilities = ["update"]
}
```
