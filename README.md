# InviteTracker

InviteTracker is a discord bot used to track user invites, only acknowledging the invite after the new member has been give a verified role.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 invitetracker.py
```
This will create a file named "config.json". Edit it to the fields provided and re-run the bot.

Discord Commands:

`%stats (@mention)` - shows stats of yourself or of the user provided if mention

`%lb` - shows leaderboard based on invite points

`%addpoints` - moderation command used to manually add points (can be negative, **requires Manage Roles**)



## License
[MIT](https://choosealicense.com/licenses/mit/)