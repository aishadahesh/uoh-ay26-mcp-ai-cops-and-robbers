# Cloud / Ngrok Bonus Deployment

This guide is for the inter-group bonus in `ex06`: deploy one public MCP server for the cop agent
and one public MCP server for the thief agent, then exchange URLs with another group.

## What Gets Deployed

Deploy two separate web services from this same repository:

| Service | Start command | Public path |
| --- | --- | --- |
| Cop MCP | `python -m cops_robbers_ai.cop_server` | `/mcp` |
| Thief MCP | `python -m cops_robbers_ai.thief_server` | `/mcp` |

The services use FastMCP `streamable-http` transport in ngrok/cloud mode. Keep local development on
the default stdio transport unless you explicitly set `MCP_TRANSPORT`.

## Required Environment Variables

Set these on both cloud services:

```env
MCP_TRANSPORT=streamable-http
MCP_HOST=0.0.0.0
MCP_PUBLIC_URL=https://your-service-url.example.com
MCP_AUTH_TOKEN=use-a-long-random-secret
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
```

`MCP_PUBLIC_URL` must be different for the cop and thief service because each service gets its own
cloud URL.

`GEMINI_API_KEY` and `OPENAI_API_KEY` are optional for basic operation because the code can fall
back to deterministic agents, but API-backed agents are better for the assignment story.

## Ngrok Deployment

This is the fastest way to expose your local MCP servers for the bonus.

1. Install ngrok and authenticate it:

```powershell
ngrok config add-authtoken <your-ngrok-authtoken>
```

2. Copy the example tunnel config:

```powershell
Copy-Item ngrok.example.yml ngrok.yml
```

If you used `ngrok config add-authtoken`, you may remove the `agent.authtoken` line from
`ngrok.yml`. If you have paid/reserved ngrok domains, add `domain: your-domain.ngrok-free.app` under
each tunnel.

3. Start both ngrok tunnels in terminal 1:

```powershell
.\scripts\run_ngrok_bonus.ps1
```

Copy the two HTTPS forwarding URLs from the ngrok terminal. If you use reserved domains, use those
reserved URLs.

4. Start the local cop MCP server in terminal 2:

```powershell
$env:MCP_AUTH_TOKEN="use-a-long-random-secret"
$env:MCP_PUBLIC_URL="https://your-cop.ngrok-free.app"
.\scripts\run_cop_mcp_http.ps1
```

5. Start the local thief MCP server in terminal 3:

```powershell
$env:MCP_AUTH_TOKEN="use-a-long-random-secret"
$env:MCP_PUBLIC_URL="https://your-thief.ngrok-free.app"
.\scripts\run_thief_mcp_http.ps1
```

The public MCP URLs to exchange are:

```text
https://your-cop.ngrok-free.app/mcp
https://your-thief.ngrok-free.app/mcp
```

If ngrok assigned random URLs, use those URLs for `MCP_PUBLIC_URL` and append `/mcp` when exchanging
the MCP endpoint with the other group.

## Render Deployment

The repository includes `render.yaml`, which defines both services.

1. Push this repository to GitHub.
2. In Render, choose **New** -> **Blueprint**.
3. Connect the GitHub repository.
4. Render will create:
   - `shadowgrid-cop-mcp`
   - `shadowgrid-thief-mcp`
5. For each service, set:
   - `MCP_PUBLIC_URL` to that service's Render URL.
   - `MCP_AUTH_TOKEN` to the same long random token, or separate tokens if you prefer.
   - API keys if you are using cloud LLMs.
6. Redeploy both services after setting environment variables.

The MCP endpoint path is:

```text
https://your-render-service.onrender.com/mcp
```

## Local HTTP Smoke Test

You can run one service locally in HTTP mode:

```powershell
$env:MCP_TRANSPORT="streamable-http"
$env:MCP_HOST="127.0.0.1"
$env:MCP_PORT="8001"
$env:MCP_PUBLIC_URL="http://127.0.0.1:8001"
$env:MCP_AUTH_TOKEN="local-test-token"
python -m cops_robbers_ai.cop_server
```

Then test from an MCP client using:

```text
URL: http://127.0.0.1:8001/mcp
Authorization: Bearer local-test-token
```

## Inter-Group Bonus Match

Exchange these values with the other group:

```text
Your cop MCP URL: https://your-cop-service.example.com/mcp
Your thief MCP URL: https://your-thief-service.example.com/mcp
Your token: ...
```

They should give you:

```text
Their cop MCP URL: https://their-cop-service.example.com/mcp
Their thief MCP URL: https://their-thief-service.example.com/mcp
Their token: ...
```

Run six sub-games:

| Sub-games | Pairing |
| --- | --- |
| 1-3 | Your cop agent vs their thief agent |
| 4-6 | Their cop agent vs your thief agent |

Use one orchestrator as the source of truth for the board state, legal moves, barriers, scoring, and
the final JSON report. The MCP servers should only return agent decisions.

Before each decision, the orchestrator should call the remote agent's `update_state` tool, then
`receive_message`, then `choose_action`.

Create a working bonus config:

```powershell
Copy-Item bonus_config.example.json bonus_config.json
notepad bonus_config.json
```

Set the four public MCP URLs and the group tokens. Then run the six-game bonus series:

```powershell
python -m cops_robbers_ai.cli --bonus-config bonus_config.json --print-report
```

The runner writes:

```text
reports/bonus_game_report.json
```

If `bonus_config.json` contains `email.enabled=true`, the runner also sends the finished JSON report
as an attachment from both group Gmail accounts. Use separate OAuth token files for the two senders:

```json
"email": {
  "enabled": true,
  "to": "rmisegal+uoh26b@gmail.com",
  "subject": "Assignment 06 Bonus - Agreed MCP Cops and Robbers JSON Report",
  "credentials_path": "credentials.json",
  "senders": [
    {
      "group": "uoh-ay26",
      "address": "aishadahesh11@gmail.com",
      "token_path": "token_group_1_aisha.json"
    },
    {
      "group": "yanell11",
      "address": "yanalserhan3@gmail.com",
      "token_path": "token_group_2_yanal.json"
    }
  ]
}
```

`credentials.json` is the Google OAuth client file. Gmail sets the real sender according to the
approved token file, so authenticate `token_group_1_aisha.json` with
`aishadahesh11@gmail.com` and `token_group_2_yanal.json` with `yanalserhan3@gmail.com`.

## Report Fields

The bonus report includes the four public MCP URLs required by the PDF:

```json
{
  "report_type": "bonus_game",
  "mcp_url_group_1_cop": "https://your-cop-service.example.com/mcp",
  "mcp_url_group_1_thief": "https://your-thief-service.example.com/mcp",
  "mcp_url_group_2_cop": "https://their-cop-service.example.com/mcp",
  "mcp_url_group_2_thief": "https://their-thief-service.example.com/mcp",
  "mutual_agreement": true
}
```

Both groups must submit matching JSON results. If the reports disagree, the bonus series can be
rejected.
