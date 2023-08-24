# diversabot
DiversaTech's Slack management bot for the DiversaSpotting competition.

**app.py**: entry-point executable to run a diversabot server instance. does not support concurrent server instnaces
**utils.py**: misc utility functions
**models**: sqlalchemy ORM models
**blocks**: slack block templates for message output UIs

Currently supports:
- spotting (uploading an image and tag people records a diversaspot)
- diversabot miss
- diversabot leaderboard
- diversabot stats
- diversabot rules
- diversabot flag

Features up next:
- diversabot chum
- diversabot unflag
- diversabot recap
- diversabot team-leaderboard


Major Updates in V2:
- DB migrated from Google Sheets to PostgreSQL
- All images are now permanently stored in S3 (Slack has a 90-day message retention limit)

Legacy Diversabot: https://github.com/thomaspwang/DiversaBot