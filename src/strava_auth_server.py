"""One-time local OAuth helper for Strava.

Run this, open the page it prints, click "Connect with Strava", authorize,
and it captures the redirect, exchanges the code for tokens, and writes the
refresh token straight into .env.

Requires STRAVA_CLIENT_ID / STRAVA_CLIENT_SECRET already in .env, and the
Strava app's "Authorization Callback Domain" (strava.com/settings/api) set
to: localhost
"""
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from dotenv import load_dotenv

load_dotenv()

PORT = 8000
PUBLIC_CALLBACK_DOMAIN = os.environ.get("STRAVA_PUBLIC_CALLBACK_DOMAIN")
REDIRECT_URI = (
    f"https://{PUBLIC_CALLBACK_DOMAIN}/callback"
    if PUBLIC_CALLBACK_DOMAIN
    else f"http://localhost:{PORT}/callback"
)
SCOPE = "read,activity:read_all"
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")

AUTHORIZE_URL = "https://www.strava.com/oauth/authorize?" + urllib.parse.urlencode(
    {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "approval_prompt": "force",
        "scope": SCOPE,
    }
)

PAGE_STYLE = """
<html><body style="font-family: -apple-system, sans-serif; text-align:center; margin-top:15vh">
{body}
</body></html>
"""


def update_env_refresh_token(new_token: str) -> None:
    with open(ENV_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("STRAVA_REFRESH_TOKEN="):
                f.write(f"STRAVA_REFRESH_TOKEN={new_token}\n")
            else:
                f.write(line)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/":
            self._respond(200, PAGE_STYLE.format(body=f"""
                <h1>Run Coach</h1>
                <p>Connect your Strava account to pull in real activity data.</p>
                <a href="{AUTHORIZE_URL}"
                   style="background:#fc4c02;color:white;padding:12px 24px;
                   border-radius:6px;text-decoration:none;font-weight:bold">
                   Connect with Strava
                </a>
            """))
            return

        if parsed.path == "/callback":
            qs = urllib.parse.parse_qs(parsed.query)

            if "error" in qs:
                self._respond(400, PAGE_STYLE.format(
                    body=f"<h1>Authorization denied</h1><p>{qs['error'][0]}</p>"
                ))
                return

            code = qs.get("code", [None])[0]
            if not code:
                self._respond(400, PAGE_STYLE.format(body="<h1>Missing code</h1>"))
                return

            token_resp = requests.post(
                "https://www.strava.com/oauth/token",
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )
            token_resp.raise_for_status()
            data = token_resp.json()
            update_env_refresh_token(data["refresh_token"])

            self._respond(200, PAGE_STYLE.format(body=f"""
                <h1>Connected!</h1>
                <p>Scope granted: {data.get('scope', '')}</p>
                <p>Refresh token saved to .env — you can close this tab.</p>
            """))
            print(f"Success — refresh token saved to .env (scope={data.get('scope')}).")
            return

        self._respond(404, PAGE_STYLE.format(body="<h1>Not found</h1>"))

    def _respond(self, status: int, html: str) -> None:
        body = html.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        raise SystemExit("Set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET in .env first.")
    print(f"Open http://localhost:{PORT} in your browser to connect Strava.")
    HTTPServer(("localhost", PORT), Handler).serve_forever()
