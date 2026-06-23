## Usage

### Installation

1. Download newest release
2. Install following depencies:
```
discord.py
python-dotenv
```
   with 
```
pip install discord.py python-dotenv
```

### Configuring

Open `conf/configtemplate.env`, add your discord bot token and configure other fields with values of your liking.
On new discord server, run `/configure channel(discord.Channel) role (discord.Role)`, where channel is the channel you wish the bot to send e.g. level-up notifications & system messages

### Secure configuration base!
Put your custom configuration to your `configtemplate.env` file in `conf` folder, and load them using `os.getenv(var_name)`.

### Features 
Current Features of the bot:
- Tracks sent messages and rewards with levels & tokens, and of course, having leaderboard for both levels and tokens!
- Role store where admins can add roles whose users can buy with tokens theyve earned
- Change bot name easily with `/changename new_name(str)`!
- Reaction role command for basic user role setup (allow users to choose e.g. notification preferences this way, for example)
