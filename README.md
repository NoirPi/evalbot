EVALBOT
------

Discord Code eval bot using the [Rextester][rextester] API.

### SETUP
 - Create a discord bot account at [the discord developers page][discord-devs]. **IMPORTANT** Create a bot user as well.
 - clone the repository and create a [Virtual Environment][venv]
 - Install all the requirements via `pip install -r requirements.txt`
 - Create a `config.ini` in the following format:
```ini
[discord]
token = YOURDISCORDTOKEN. DISCORD! TOKEN! NOT ID OR SECRET

```
 - Launch the bot via `python main.py`. If you want to run the bot permanently i recommend using `tmux` or `screen`.

[discord-devs]: https://discordapp.com/developers/applications/me
[venv]: https://docs.python.org/3/library/venv.html
[rextester]: http://rextester.com/main
