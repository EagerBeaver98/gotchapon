"""
get_token.py — Run this ONCE to authorize both your broadcaster and bot accounts.

You'll be asked to log in to Twitch TWICE:
  1. As your BROADCASTER account (your main stream account)
  2. As your BOT account (the separate bot account)

Tokens are automatically saved into config.json.
Re-run this if either token expires (~60 days).
"""

import http.server
import threading
import webbrowser
import urllib.parse
import requests
import json
import sys

REDIRECT_URI = "http://localhost:3000"


class _OAuthHandler(http.server.BaseHTTPRequestHandler):
    captured_code = None

    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if "code" in params:
            _OAuthHandler.captured_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family:sans-serif;text-align:center;padding:60px">
                <h1>&#10003; Authorized!</h1>
                <p>You can close this tab and return to the terminal.</p>
                </body></html>
            """)
        elif "error" in params:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization denied. Please try again.</h1>")
        else:
            self.send_response(200)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def authorize_account(client_id, client_secret, scopes, account_label):
    """
    Opens a browser auth flow for one account and returns (access_token, refresh_token).
    account_label is just a display string like "BROADCASTER" or "BOT".
    """
    scope_string = " ".join(scopes)

    auth_url = (
        f"https://id.twitch.tv/oauth2/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope={urllib.parse.quote(scope_string)}"
        # force_verify makes Twitch always show the account picker,
        # which is essential when authorizing two different accounts back to back
        f"&force_verify=true"
    )

    print()
    print(f"  ▶  Log in as your {account_label} account in the browser window.")
    if not scopes:
        print(f"     (No scopes required — just confirming the account identity)")
    else:
        print(f"     Scopes: {scope_string}")
    print()
    print("  Opening browser...")
    print(f"  (If it doesn't open, paste this URL manually:)\n  {auth_url}")
    print()

    _OAuthHandler.captured_code = None
    server = http.server.HTTPServer(("localhost", 3000), _OAuthHandler)
    server_thread = threading.Thread(target=server.handle_request)
    server_thread.daemon = True
    server_thread.start()

    webbrowser.open(auth_url)
    server_thread.join(timeout=120)
    server.server_close()

    if not _OAuthHandler.captured_code:
        print(f"❌ Authorization timed out or was denied for {account_label} account.")
        sys.exit(1)

    print(f"  ✅ {account_label} authorization received! Exchanging code for token...")

    response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": _OAuthHandler.captured_code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
    )

    token_data = response.json()

    if "access_token" not in token_data:
        print(f"❌ Token exchange failed for {account_label}: {token_data}")
        sys.exit(1)

    return token_data["access_token"], token_data.get("refresh_token", "")


def main():
    try:
        with open("config.json") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found. Make sure you're running this from the StreamRewards folder.")
        sys.exit(1)

    client_id     = config.get("client_id", "")
    client_secret = config.get("client_secret", "")
    scopes        = config.get("scopes", {})

    if not client_id or client_id.startswith("paste_"):
        print("❌ Please fill in your client_id in config.json first.")
        sys.exit(1)
    if not client_secret or client_secret.startswith("paste_"):
        print("❌ Please fill in your client_secret in config.json first.")
        sys.exit(1)

    print()
    print("━" * 50)
    print("  StreamRewards — Twitch Authorization")
    print("━" * 50)
    print()
    print("You will be asked to log in TWICE:")
    print("  1. As your BROADCASTER account")
    print("  2. As your BOT account")
    print()
    print("Make sure http://localhost:3000 is listed as an")
    print("OAuth Redirect URL in your Twitch Developer App.")
    input("Press Enter when ready...")

    # --- Step 1: Broadcaster ---
    print()
    print("━" * 50)
    print("  STEP 1 of 2 — BROADCASTER account")
    print("━" * 50)

    broadcaster_scopes = scopes.get("broadcaster", [])
    b_access, b_refresh = authorize_account(client_id, client_secret, broadcaster_scopes, "BROADCASTER")
    config["broadcaster_access_token"] = b_access
    config["broadcaster_refresh_token"] = b_refresh

    # Save after each step in case the second one fails
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    print(f"  ✅ Broadcaster token saved.")

    # --- Step 2: Bot ---
    print()
    print("━" * 50)
    print("  STEP 2 of 2 — BOT account")
    print("━" * 50)

    bot_scopes = scopes.get("bot", [])
    bot_access, bot_refresh = authorize_account(client_id, client_secret, bot_scopes, "BOT")
    config["bot_access_token"] = bot_access
    config["bot_refresh_token"] = bot_refresh

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    print()
    print("━" * 50)
    print("  All done!")
    print("━" * 50)
    print()
    print("  Both tokens saved to config.json.")
    print("  You can now run:  gotchapon.exe")
    print()


if __name__ == "__main__":
    main()