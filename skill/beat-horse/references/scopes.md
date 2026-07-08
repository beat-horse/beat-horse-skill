# API key scopes

Every MCP key needs:

- `mcp:access`

Common workflows:

| Workflow | Scopes |
|---|---|
| Read account/credits | `mcp:access`, `account:read`, `credits:read` |
| Generate from text | `mcp:access`, `generation:create`, `generation:read`, `models:read`, `credits:read` |
| Upload source/reference audio and generate | `mcp:access`, `assets:read`, `assets:write`, `generation:create`, `generation:read`, `models:read`, `credits:read` |
| Read usage | `mcp:access`, `usage:read` |
| Read billing purchases/packages | `mcp:access`, `billing:read`, `credits:read` |

Default dashboard-created keys normally include the generation, asset, model, credit, and MCP scopes needed for normal agent use.

If the API returns `insufficient_scope`, create or update the key with the missing scope shown in the error message.
