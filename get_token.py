"""
get_token.py — Run this ONCE to authorize your Twitch account.

This opens a browser window, asks you to log in to Twitch, then
automatically saves your access token into config.json.

You only need to re-run this if your token expires (~60 days).
"""

import http.server
import threading
import webbrowser
import urllib.parse
import requests
import json
import sys

REDIRECT_URI = "http://localhost:3000"
SCOPES = "channel:read:redemptions"


class _OAuthHandler(http.server.BaseHTTPRequestHandler):
    """Tiny local web server that catches the redirect from Twitch."""
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
        pass  # Suppress noisy request logs in the terminal


def main():
    # Load config
    try:
        with open("config.json") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found. Make sure you're running this from the StreamRewards folder.")
        sys.exit(1)

    client_id = config.get("client_id", "")
    client_secret = config.get("client_secret", "")

    if not client_id or client_id == "paste_your_client_id_here":
        print("❌ Please fill in your client_id in config.json first.")
        sys.exit(1)
    if not client_secret or client_secret == "paste_your_client_secret_here":
        print("❌ Please fill in your client_secret in config.json first.")
        sys.exit(1)

    # Build the Twitch authorization URL
    auth_url = (
        f"https://id.twitch.tv/oauth2/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope={urllib.parse.quote(SCOPES)}"
    )

    print("━" * 50)
    print("  StreamRewards — Twitch Authorization")
    print("━" * 50)
    print()
    print("IMPORTANT: Log in as the BROADCASTER account (your stream account).")
    print("           The token must belong to the channel you're watching.")
    print()
    print("Opening your browser now...")
    print("(If it doesn't open, paste this URL manually:)")
    print(f"\n  {auth_url}\n")

    # Start the one-shot local server to catch the redirect
    server = http.server.HTTPServer(("localhost", 3000), _OAuthHandler)
    server_thread = threading.Thread(target=server.handle_request)
    server_thread.daemon = True
    server_thread.start()

    webbrowser.open(auth_url)
    server_thread.join(timeout=120)  # Wait up to 2 minutes for the user to authorize

    if not _OAuthHandler.captured_code:
        print("❌ Authorization timed out or was denied.")
        sys.exit(1)

    print("✅ Authorization received! Exchanging code for token...")

    # Exchange the authorization code for an access + refresh token
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
        print(f"❌ Token exchange failed: {token_data}")
        sys.exit(1)

    # Save tokens back into config.json
    config["access_token"] = token_data["access_token"]
    config["refresh_token"] = token_data.get("refresh_token", "")

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("✅ Token saved to config.json!")
    print()
    print("You can now run:  python main.py")
    print()


if __name__ == "__main__":
    main()
