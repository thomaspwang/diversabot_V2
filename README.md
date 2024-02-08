# diversabot_V2
Slack management bot for the DiversaSpotting competition.

## How to contribute
1. Reach out to Thomas Wang  for `.env` variables and to add collaborators on the Slack API console
2. Run `./setup.sh` to download CockroachDB certificates, create your local python virtual environment, and download dependencies
3. Test locally, and make a PR :)

Note that the production app is hosted on Heroku, which updates automatically upon any changes to `main`. So please, don't push to main.

## How to run locally
*TODO: Add a --test flag to differentiate production and testing environments*
*TODO: Need to create seperate testing server endpoints for Slack*
1. Run the server using either:
	- `python app.py` (if virtual environment is activated)
	- `./diversavenv/bin/python3.10 app.py` 
2. Run `ngrok http 3000` to expose the port 
3. Copy paste the expose web link and add it in the `Event Subscriptions` and the `Interactivity & Shortcuts` sidebar tabs.

## Relevant Files
- **app.py**: entry-point executable to run a diversabot server instance. does not support concurrent server instnaces 
- **utils.py**: misc utility functions 
- **models**: sqlalchemy ORM models 
- **blocks**: slack block templates for message output UIs

## Currently supports:
- spotting (uploading an image and tag people records a diversaspot)
- diversabot miss
- diversabot leaderboard
- diversabot stats
- diversabot rules
- diversabot flag
- diversabot unflag

## Features up next:
- diversabot chum
- diversabot recap
- diversabot team-leaderboard
- diversabot ultimate-leaderboard


## Major Updates in V2:
- DB migrated from Google Sheets to PostgreSQL
- All images are now permanently stored in S3 (Slack has a 90-day message retention limit)

*Legacy Diversabot: https://github.com/thomaspwang/DiversaBot*
