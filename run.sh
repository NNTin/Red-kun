#!/bin/bash

# creating necessary .config/Red-DiscordBot directory
mkdir ~/.config
mkdir ~/.config/Red-DiscordBot

# extracting HOST, PORT, USERNAME, PASSWORD and DB_NAME from MONGODB_URI
# echo $MONGODB_URI

# regex="mongodb:\/\/([a-z0-9_]+):([a-z0-9]+)@([a-z0-9.]+):(\d+)\/([a-z0-9_]+)"
regex="mongodb://([[:alnum:]_]+):([[:alnum:]]+)@([[:alnum:].]+):([[:digit:]]+)/([[:alnum:]_]+)"
if [[ $MONGODB_URI =~ $regex ]]
then
    USERNAME="${BASH_REMATCH[1]}"
    PASSWORD="${BASH_REMATCH[2]}"
    HOST="${BASH_REMATCH[3]}"
    PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo "$MONGODB_URI doesn't exist or is in an inproper format" >&2
    exit 1
fi

# creating new CONFIG_JSON
CONFIG_JSON="{\"heroku\":{\"DATA_PATH\":\"/app\",\"COG_PATH_APPEND\":\"cogs\",\"CORE_PATH_APPEND\":\"core\",\"STORAGE_TYPE\":\"MongoDB\",\"STORAGE_DETAILS\":{\"HOST\":\"$HOST\",\"PORT\":$PORT,\"USERNAME\":\"$USERNAME\",\"PASSWORD\":\"$PASSWORD\",\"DB_NAME\":\"$DB_NAME\",\"URI\":\"mongodb\"}}}"
# echo $CONFIG_JSON

echo $CONFIG_JSON > ~/.config/Red-DiscordBot/config.json

python3 -m redbot heroku --token $TOKEN --prefix $PREFIX $OPTIONAL_ARGS
