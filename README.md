# web-vault-token-management
This web application allows you to view and manage HashiCorp Vault tokens defined in a YAML configuration file. It provides a user-friendly interface to display token details, renew tokens, and invalidate (revoke) tokens as needed.

## Configuration
#### Example `tokens.yaml`

```yaml
# tokens.yaml

tokens:
  - name: "Token for Application A"
    accessor: "s.HASHED_ACCESSOR_VALUE_1"

  - name: "Token for Application B"
    accessor: "s.HASHED_ACCESSOR_VALUE_2"

  - name: "Token for Application C"
    accessor: "s.HASHED_ACCESSOR_VALUE_3"

  # Add more tokens as needed following the same structure.
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

#### Example of Helm-chartie values
```yaml
deployments:
  web-vault-token-management:
    image: lukaspastva/web-vault-token-management:latest
    resourcesSimple: 50
    podSecurityContextRestricted: true
    ports:
      - name: http
        port: 8080
        domains:
          - "vault-tokens.tronic.sk"
        paths:
          - "/"
    env:
      - name: VAULT_ADDR
        value: "http://vault-internal.sys-vault.svc.cluster.local:8200"
      - name: VAULT_TOKENS_FILE
        value: "/vault/secrets/tokens.yaml"
      - name: VAULT_TOKEN
        valueFrom:
          secretKeyRef:
            name: web-vault-token-management
            key: VAULT_TOKEN
    serviceAccountAnnotations:
      vault.hashicorp.com/alias-metadata-env: web-vault-token-management/web-vault-token-management
    annotations:
      vault.hashicorp.com/agent-inject: "true"
      vault.hashicorp.com/role: "template-web-vault-token-management"
      vault.hashicorp.com/agent-inject-file-accessors: "config.yaml"
      vault.hashicorp.com/agent-inject-template-accessors: |-
        {{ with secret "kv/k8s/exporter-vault-tokens/exporter-vault-tokens/secret" }}{{ .Data.data.data }}{{ end }}
```