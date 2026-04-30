# Assessment PIN test users

Use these with `verify_customer_pin` for demos and pytest scenarios that hit the live MCP server (optional integration tests).

| Email | PIN |
|-------|-----|
| donaldgarcia@example.net | 7912 |
| michellejames@example.com | 1520 |
| laurahenderson@example.org | 1488 |
| spenceamanda@example.org | 2535 |
| glee@example.net | 4582 |
| williamsthomas@example.net | 4811 |
| justin78@example.net | 9279 |
| jason31@example.com | 1434 |
| samuel81@example.com | 4257 |
| williamleon@example.net | 9928 |

After a successful verification, the agent records the **customer UUID** from the tool output and only then allows `list_orders`, `get_order`, `create_order`, and `get_customer` (with matching id where applicable).
