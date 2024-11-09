# Nicholas the 8th - New Instance

This is a setup guide for `Linux (Ubuntu)`. This is just a guide for future me, but if you want to use it, feel free to do so. 

Main [README.md](../README.md)

## Discord Developer Portal
- Go to the [Discord Developer Portal](https://discord.com/developers/applications)
- Create a new application

##### Bot tab
- Create a new bot
- Copy the `BOT_TOKEN`
- Check all the Privileged Gateway Intents

##### OAuth2 tab
- Copy the `CLIENT_ID` and `CLIENT_SECRET`
- In the OAuth2 tab under Default Authorization Link, check `In-App Authorization` (this will show a button in the bot profile)
- Scopes: `bot` and `application.commands`
- Bot Permissions: `Administrator` or 
>`Add Reactions` `Attach Files` `Connect` `Embed Links` `Read Message History` `Send Messages` `Send Messages in Threads` `Speak` `Use Slash Commands` `View Channels` 

##### Optional
- Add a bot icon
- Add a bot description

## Config setup

These are the required environment variables for the bot.

- Create a file called `.env` in the main directory
```dotenv
# Description: Configuration file for the bot
# Discord
CLIENT_ID='YOUR_CLIENT_ID' # This is your bots id
OWNER_ID='YOUR_USER_ID' # This is your user id
BOT_TOKEN='YOUR_BOT_TOKEN' # This is the token for the bot
CLIENT_SECRET="YOUR_CLIENT_SECRET" # This is the client secret for the bot

# Prefix
PREFIX="ncl." # This is the prefix for the bot

# Notification
NOTIF="" # This message will be appended to the end of every message sent by the bot (leave empty for normal behaviour)

# Authorised Users
AUTHORIZED_USERS='[416254812339044365, 349164237605568513]' # has to be this format | ='[1, 2, 3, ...]' | This is a list of authorised users (add your user id here - not required)

# Spotify
SPOTIFY_CLIENT_ID='YOUR_SPOTIFY_CLIENT_ID' # This is the client id for the spotify api
SPOTIFY_CLIENT_SECRET='YOUR_SPOTIFY_CLIENT_SECRET' # This is the client secret for the spotify api
SPOTIFY_REDIRECT_URI='https://localhost:8888/callback' # This is the redirect uri for the spotify api

# SoundCloud
SOUNDCLOUD_CLIENT_ID='YOUR_SOUNDCLOUD_ID' # SoundCloud ID (you can use your accounts id -> developer tools)

# DEFAULT VALUES - DO NOT CHANGE UNLESS YOU KNOW WHAT YOU'RE DOING
DEFAULT_DISCORD_AVATAR="https://cdn.discordapp.com/embed/avatars/0.png"
VLC_LOGO="https://upload.wikimedia.org/wikipedia/commons/3/38/VLC_icon.png"
DEVELOPER_ID=349164237605568513

# Discord
INVITE_URL="https://discord.com/oauth2/authorize?client_id=${CLIENT_ID}"
```

# Two ways to run the bot

The bot can be run two ways. 

- [Docker](#docker-setup) (I am currently using this method)
- [Directly](#direct-setup) (Just run the main.py file)

# Docker setup

### [Install docker](DOCKER.md)

### Docker compose

Build the container - this will take a while
```bash
docker compose build
```
Run the containers - you can use `-d` to run in the background
```bash
docker compose up -d
```

### Check if it works

Check if the container is running
```bash
docker compose ps
```
It should look something like this:
```
NAME      IMAGE              COMMAND                                                     SERVICE   CREATED        STATUS        PORTS
bot       bot-bot     "/bin/sh -c 'python main.py >> logs/bot.log 2>&1'"   bot       19 hours ago   Up 18 hours   5420-5422/tcp
```

### Troubleshooting

If the container is not running (or is restarting), you can check the logs with this command:
```bash
docker logs CONTAINER_NAME
```

If you want to access the container, you can use this command:
```bash
docker exec -t -i CONTAINER_NAME /bin/bash
```

### General commands


If you want to stop the containers, you can use this command:
```bash
docker compose stop
```
or this command to stop and remove the containers:
```bash
docker compose down
```
If you want to start the containers again, you can use this command:
```bash
docker compose start
```

# Direct setup

## Initial Setup

- ``sudo su`` - Make yourself a super-user

- ``apt update && apt upgrade -y`` - Update your system

- ``apt install git -y`` - Install git

- ``apt install python3 -y`` - Install python3

- ``apt install python3-pip -y`` - Install pip3

- ``apt install ffmpeg -y`` - Install ffmpeg

### Folder setup

Navigate to the desired directory for the bot
```bash
cd /path_to_directory 
```
Clone the [nicholas_the_8th](https://github.com/Tomer27cz/nicholas_the_8th) repository
```bash
git clone https://github.com/Tomer27cz/nicholas_the_8th.git
```
Rename the folder
```bash
mv nicholas_the_8th bot
```
Move into the folder
```bash
cd bot
```
Give permissions for the folder to everyone (very bad practice - probably should not do this, but it works)
```bash
chmod -R 777 /path_to_directory
```

### Python setup

Install the required packages
```bash
pip3 install -r requirements.txt
```

### Run the bot

Nohup is a command that runs a command in the background, and the `&` at the end of the command tells the command to run in the background. The `>>` command is used to append the output to a file. The `-u` flag is used to run the command in unbuffered mode.
```
nohup python3 -u main.py &>> logs/bot.log &
```

Now you can check if the bot is running
```bash
ps aux | grep main.py
```

If you want to stop the bot, you can use this command
```bash
kill -9 PID
```

Now the bot should be running.
If not... check the logs and good luck.
