#!/bin/bash

# creating necessary .config/Red-DiscordBot directory
mkdir -p ~/.config/Red-DiscordBot

# faking redbot-setup
cat /app/config.json > ~/.config/Red-DiscordBot/config.json

# running the bot
python3 -m redbot json --token $TOKEN --prefix $PREFIX $OPTIONAL_ARGS
