# Gotchapon

Gotchapon is a gacha-style Twitch channel points overlay. When a chatter redeems a configured reward, the application rolls against a set of configurable probability tiers and displays the result on stream — reward image, chatter name, sound cues, and redemption history — through an OBS Browser Source.

## Requirements

- Windows 10/11 (the packaged build is Windows-only)
- OBS Studio, with an available Browser Source slot in the target scene
- A Twitch account for the broadcaster channel, with Channel Points enabled in the Creator Dashboard
- Two-factor authentication enabled on the Twitch account used to register a developer application (required by the Twitch Developer Console)
- A second Twitch account for the bot identity is recommended but not required; the broadcaster account may be used for both roles

## 1. Installation

Download the latest release archive from this repository's Releases page and extract it. The archive contains `gotchapon.exe` and a `display/` folder. These two must remain in the same directory; the application resolves `display/` relative to its own location.

## 2. Initial Setup

Run `gotchapon.exe`. On each launch, the application checks for required files in a fixed order and exits with a message box describing the next missing item. Resolve each item and relaunch until the application remains running. The checks occur in this order:

1. **Reward images** — creates `display/rewards/10/`, `display/rewards/50/`, and `display/rewards/75/`. At least one image file must be added to at least one tier folder. See [Section 8](#8-reward-tiers-background-and-sound-files) for how tier folders determine odds.
2. **Background image** — a file named `background`, with any common image extension, placed directly in `display/`.
3. **`config.json`** — a template is generated in the application directory. See [Section 3](#3-configuration-reference) for field definitions.
4. **Sound files** — creates `display/sounds/` and requires five files, described in [Section 8](#8-reward-tiers-background-and-sound-files).

## 3. Configuration Reference

Open `config.json` and populate each field:

| Field | Description |
|---|---|
| `twitch_channel` | Broadcaster's Twitch login name (lowercase, no `@`) |
| `owner_id` | Broadcaster's numeric Twitch user ID — see [Section 5](#5-obtaining-broadcaster-and-bot-account-ids) |
| `bot_username` | Bot account's Twitch login name |
| `bot_id` | Bot account's numeric Twitch user ID — see [Section 5](#5-obtaining-broadcaster-and-bot-account-ids) |
| `client_id` / `client_secret` | Credentials from the registered Twitch application — see [Section 4](#4-registering-a-twitch-application) |
| `redeem_id` | ID of the custom channel points reward that triggers a roll — see [Section 6](#6-creating-the-reward-and-obtaining-its-id) |
| `overlay_port` | Local port the overlay's web page is served on. Default: `8080` |
| `websocket_port` | Local port used to push live redemption events to the overlay. Default: `8081` |
| `overlay_duration_fade_in_gap` | Seconds between the background appearing and the reward/name/history fading in |
| `overlay_duration_hold` | Seconds the result remains fully visible before clearing or advancing to the next queued redemption |
| `font-color` | CSS color value (e.g. `"white"` or `"#ffffff"`) applied to the chatter-name text |
| `font-shadow-color` | CSS color value applied to the drop shadow behind the chatter-name text |
| `font-family` | Filename of a `.ttf` file placed directly in `display/`, for a custom font. Leave the placeholder value to use the default font |
| `obs_host` | Bind address for the overlay's local HTTP and WebSocket servers. Leave as `"localhost"` unless the overlay must be reachable from another device on the network |
| `obs_port` / `obs_password` | Not currently used by the application; reserved for a future direct OBS-WebSocket integration |

## 4. Registering a Twitch Application

`client_id` and `client_secret` are obtained from a Twitch developer application.

1. Navigate to [dev.twitch.tv/console](https://dev.twitch.tv/console) and sign in.
2. Select **Register Your Application**.
3. Enter a **Name** (any value not already in use, e.g. "Gotchapon - <channel name>").
4. Under **OAuth Redirect URLs**, add exactly: `http://localhost:4343/oauth/callback`.
5. Select a **Category** (`Chat Bot` or `Application Integration`).
6. Select **Create**, then open the application and select **Manage**.
7. Copy the **Client ID** into `client_id` in `config.json`.
8. Select **New Secret** to generate a **Client Secret** and copy it into `client_secret`. The secret is displayed once; if it is lost, generate a new one.

## 5. Obtaining Broadcaster and Bot Account IDs

Twitch user IDs are numeric and are not displayed in the standard Twitch web interface. Two methods are available that do not require installing a command-line tool.

**Option A — Page source lookup**

1. Open the target account's channel page in a browser (e.g. `https://www.twitch.tv/<username>`).
2. View the page source (`Ctrl+U` in most browsers, or right-click → View Page Source).
3. Search the page source for `channel_id`. The associated numeric value is the account's user ID.

**Option B — Third-party lookup tool**

A number of community-maintained tools convert a Twitch username to a numeric ID (for example, StreamWeasels' Username-to-ID converter, `streamweasels.com/tools/convert-twitch-username-to-user-id/`). These tools query the Twitch API on the user's behalf and require no installation. Repeat the lookup for both the broadcaster and bot usernames to obtain `owner_id` and `bot_id`.

## 6. Creating the Reward and Obtaining Its ID

1. In the Twitch Creator Dashboard, navigate to **Viewer Rewards → Channel Points → Manage Rewards** and add a custom reward. Set a title, cost, and enable it.
2. Obtain the reward's ID using one of the following methods.

**Option A — Community lookup tool**

Open `https://www.instafluff.tv/TwitchCustomRewardID?channel=<broadcaster_username>` in a browser, replacing `<broadcaster_username>` with the broadcaster's Twitch login name. Redeem the custom reward once while the page is open; the reward's ID is displayed on the page when the redemption is detected. This is a community-maintained tool, not an official Twitch product.

**Option B — Manual API request with a graphical REST client**

This option uses only official Twitch endpoints and a graphical HTTP client (e.g. Postman or Insomnia); no command-line tool is required.

1. Generate a temporary broadcaster access token by navigating, while signed in as the broadcaster account, to:
   ```
   https://id.twitch.tv/oauth2/authorize?client_id=<client_id>&redirect_uri=http://localhost:4343/oauth/callback&response_type=token&scope=channel:read:redemptions
   ```
   After approving access, Twitch redirects to the registered redirect URL with the access token appended to the address bar following `#access_token=`. The page itself does not need to load successfully; the token is visible in the address bar regardless. Copy this value.
2. In the REST client, issue a `GET` request to:
   ```
   https://api.twitch.tv/helix/channel_points/custom_rewards?broadcaster_id=<owner_id>
   ```
   with headers:
   ```
   Client-Id: <client_id>
   Authorization: Bearer <access token from step 1>
   ```
3. Locate the reward by its title in the response body and copy its `id` value into `redeem_id` in `config.json`.

## 7. Authorizing the Application

With `config.json` fully populated, launch `gotchapon.exe`. The application starts a local server on port `4343`. Using the account indicated, visit each of the following URLs once:

- **Broadcaster**: `http://localhost:4343/oauth?scopes=channel:bot+channel:read:redemptions`
- **Bot**: `http://localhost:4343/oauth?scopes=channel:read:redemptions+user:read:chat+channel:bot&force_verify=true`

If both accounts are logged into the same browser, use separate browser profiles or a private/incognito window for one of the two authorizations to avoid authorizing the wrong account.

## 8. Reward Tiers, Background, and Sound Files

- **Reward images**: placed in `display/rewards/<tier>/`, where `<tier>` is a folder named with a number from 1–99. Each tier represents its own independent chance (out of 100) of being selected on a given roll. Rolls are evaluated from the lowest-numbered tier to the highest; the first tier to succeed is selected. If no tier succeeds, the highest-numbered tier is used as a guaranteed fallback. Lower numbers should therefore be used for rare tiers and higher numbers for common tiers. Any number of tiers may be defined.
- **Background**: a single file named `background.<extension>` placed directly in `display/`.
- **Sound files**: five files placed in `display/sounds/`, named exactly `coin`, `crank`, `rumble`, `open`, and `celebrate` (file extension is not significant; any browser-playable audio format is supported, e.g. `.mp3`, `.wav`, `.ogg`).
- **Custom font** (optional): a `.ttf` file placed directly in `display/` and referenced by filename in the `font-family` field of `config.json`.

## 9. Configuring the OBS Browser Source

1. In OBS, add a **Browser Source** to the target scene.
2. Set **URL** to `http://localhost:8080/` (or the configured `overlay_port`).
3. Set **Width** and **Height** to match the canvas resolution (e.g. `1920x1080`).
4. Position and resize the source as required within the scene layout.

## Troubleshooting

- **"No overlay clients detected" printed to the console**: the OBS Browser Source must be loaded before a redemption occurs. Open or refresh the source, then retry.
- **Real redemptions do not trigger a result**: verify that `redeem_id` exactly matches the custom reward's ID, and that both the broadcaster and bot authorizations in Section 7 were completed successfully.
- **Bot does not appear or respond in chat**: verify that `bot_username` and `bot_id` correspond to the account used to complete the bot authorization link, not the broadcaster's account.

## Running from Source

- Requires Python 3.12 or later
- `pip install -r requirements.txt`
- `python main.py`
- The setup and configuration steps described above apply identically when running from source.

## License

Distributed under the MIT License. See [LICENSE](./LICENSE) for full text.
