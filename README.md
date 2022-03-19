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

Config:
```json
{
    "token": "",
    "guild-id": "",
    "logs-channel": "",
    "role1-id": "",
    "role1-pts": "",
    "role2-id": "",
    "role2-pts": ""
}
```
`token`: Discord bot token

`guild-id`: ID of the server you are running it in

`logs-channel`: Channel ID of your log channel

`roleX-id`: id of role X that is being tracked

`roleX-pts`: points that role X gives to the inviter

Discord Commands:

`%stats (@mention)` - shows stats of yourself or of the user provided if mention

`%lb` - shows leaderboard based on invite points

`%addpoints` - moderation command used to manually add points (can be negative, **requires Manage Roles**)



## License
[MIT](https://choosealicense.com/licenses/mit/)