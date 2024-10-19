# web-vault-token-management
This web application allows you to view and manage HashiCorp Vault tokens defined in a YAML configuration file. It provides a user-friendly interface to display token details, renew tokens, and invalidate (revoke) tokens as needed.

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
