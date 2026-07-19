"""One-time local OAuth helper for Fitbit via the Google Health API.

Run this, open the page it prints, click "Connect with Fitbit", sign in with
the Google account your Fitbit is linked to, authorize, and it captures the
redirect, exchanges the code for tokens, and writes the refresh token into .env.

Prerequisites (see README "Connecting Fitbit (Google Health API)"):
  - A Google Cloud project with the Google Health API enabled.
  - An OAuth 2.0 Client (type: Web application) whose Authorized redirect URIs
    include exactly:  http://localhost:8000/callback
  - GOOGLE_HEALTH_CLIENT_ID / GOOGLE_HEALTH_CLIENT_SECRET set in .env.
  - The OAuth consent screen configured with the googlehealth.* scopes, and —
    while the app is unverified/"Testing" — your own Google account added as a
    Test user. Note: refresh tokens for apps in "Testing" status expire after
    ~7 days, so you'll re-run this weekly until the app is verified/Production.
"""
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from dotenv import load_dotenv

load_dotenv()

PORT = 8000
PUBLIC_CALLBACK_DOMAIN = os.environ.get("GOOGLE_HEALTH_PUBLIC_CALLBACK_DOMAIN")
REDIRECT_URI = (
    f"https://{PUBLIC_CALLBACK_DOMAIN}/callback"
    if PUBLIC_CALLBACK_DOMAIN
    else f"http://localhost:{PORT}/callback"
)
# Scopes are space-separated. activity_and_fitness covers runs/steps/VO2;
# sleep covers sleep sessions/stages; health_metrics covers resting HR, HRV,
# SpO2, weight, etc. All must also be added on the Cloud Console consent screen.
SCOPE = " ".join([
    "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly",
    "https://www.googleapis.com/auth/googlehealth.sleep.readonly",
    "https://www.googleapis.com/auth/googlehealth.health_metrics_and_measurements.readonly",
])
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")

CLIENT_ID = os.getenv("GOOGLE_HEALTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_HEALTH_CLIENT_SECRET")

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(
    {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "access_type": "offline",  # required for Google to return a refresh token
        "prompt": "consent",       # force the refresh token even on re-auth
    }
)

PAGE_STYLE = """
<html><body style="font-family: -apple-system, sans-serif; text-align:center; margin-top:15vh">
{body}
</body></html>
"""


def update_env_refresh_token(new_token: str) -> None:
    if not os.path.exists(ENV_PATH):
        return
    with open(ENV_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    found = False
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("GOOGLE_HEALTH_REFRESH_TOKEN="):
                f.write(f"GOOGLE_HEALTH_REFRESH_TOKEN={new_token}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"GOOGLE_HEALTH_REFRESH_TOKEN={new_token}\n")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/":
            self._respond(200, PAGE_STYLE.format(body=f"""
                <h1>Gaman</h1>
                <p>Connect your Fitbit (via Google Health) to pull in real activity data.</p>
                <a href="{AUTHORIZE_URL}"
                   style="background:#00B0B9;color:white;padding:12px 24px;
                   border-radius:6px;text-decoration:none;font-weight:bold">
                   Connect with Fitbit
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
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": REDIRECT_URI,
                },
                timeout=10,
            )
            token_resp.raise_for_status()
            data = token_resp.json()
            refresh_token = data.get("refresh_token")
            if not refresh_token:
                self._respond(400, PAGE_STYLE.format(body="""
                    <h1>No refresh token returned</h1>
                    <p>Google only returns one with access_type=offline and a fresh
                    consent. Revoke Gaman's access at
                    myaccount.google.com/permissions and try again.</p>
                """))
                return
            update_env_refresh_token(refresh_token)

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
        raise SystemExit("Set GOOGLE_HEALTH_CLIENT_ID and GOOGLE_HEALTH_CLIENT_SECRET in .env first.")
    print(f"Open http://localhost:{PORT} in your browser to connect Fitbit via Google Health.")
    HTTPServer(("localhost", PORT), Handler).serve_forever()
