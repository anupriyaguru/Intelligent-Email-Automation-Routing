# CAP Guidelines

Technical constraints and patterns for building CAP BTP Extensions. Follow these throughout specification execution.

## Tech Stack

- CAP (Cloud Application Programming Model) — Node.js runtime
- Frontend: React with SAP UI5 Web Components
- Local execution only (no BTP deployment in this stage)

## Project Structure

- CAP project lives in `assets/<asset-name>/`
- The `cap-development` skill handles project init, modeling, testing, and frontend scaffolding

## Key Constraints

- You MUST follow the `cap-development` skill for ALL CAP development
- Only use public APIs; mock any private systems with minimal mock data
- No Git operations, no authentication, no documentation/READMEs
- No `.env` files (environment variables supplied at runtime)

## asset.yaml

Create `assets/<asset-name>/asset.yaml` with:

```yaml
apiVersion: asset.sap/v1
kind: Asset
type: cap-app
metadata:
  name: {{application-name}}
components:
  - name: srv
    buildPath: .
    outputPath: gen/srv
    provides:
      endpoints:
        - path: /odata/v4
          port: 4004
          protocol: http
    port: 4004
    requires:
      - name: hdi-container
  - name: hdi-deployer
    type: hdi-deployer
    buildPath: .
    outputPath: gen/db
    requires:
      - hdi-container
    custom:
      lifecycle: init
```

## Testing

- CRITICAL: never skip testing after adding custom handler logic
- Only test custom logic — never test generic CRUD
- Run `cds compile srv/` to validate models; run `cds watch` to confirm service starts

## Validation

- All source code must compile, all imports must resolve
- Fix validation failures immediately before proceeding
- Implement all backend functionality also in the UI
