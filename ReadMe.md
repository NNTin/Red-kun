## Red-kun: RedDiscord-Bot meets Heroku

## Heroku Deployment Button

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Rambling

**Warning**: Red isn't built for Heroku. This repository is mainly written for **developers** who want to offer Heroku support to their users.  
The advantage of Heroku is it is free and once it is properly set up it is easy to use since no knowledge of python, git, ssh, etc. is required.  
However the initial setup is absolutely not user friendly. It is easier to run the bot off a VPS and it'll cause less issues.

The [master branch](https://github.com/NNTin/Red-kun/tree/master) has a template for adding cogs. Feel free forking it and adding whatever cog you need to your branch. Be sure to connect your GitHub repo to your Heroku account to ensure automatic deploys. The [trusty-cogs branch](https://github.com/NNTin/Red-kun/tree/trusty-cogs) adds Heroku Support to [TrustyJAID/Trusty-cogs/V3](https://github.com/TrustyJAID/Trusty-cogs/tree/V3). It functions as an example.

This project allows you to input your Discord token as an environment variable. This means you are not committing it to the GitHub git repository which is a common cause of bots going rogue.

The Heroku Support is **not** designed for you to continuously make changes to the RedDiscord-Bot. Loaded and unloaded cogs are lost [after 24-28 hours](https://devcenter.heroku.com/articles/dynos#restarting).  
However since RedDiscord-Bot supports mongoDB you have a persistent data storage method. Furthermore you can define via your environment variables (OPTIONAL_ARGS) which cogs you want to load. This means once you have it set up you can run your RedDiscord-Bot permanently with your favorite commands - given you don't change anything.  

I do not recommend hosting RedDiscord-Bot on Heroku but I do understand that some people cannot afford a VPS and need a free-tier solution for their personal bot.

**If you want Heroku Support but are struggling understanding this repository turn around. It is not worth the effort.  
This repository is mainly targeted towards developers who want to offer their users a one-click deployment solution.**

No sane developer would prefer hosting their RedDiscord-Bot on Heroku over a proper VPS.

## Random pictures

[Initial app page](https://i.imgur.com/JMWewgu.png) when deploying RedDiscord-Bot using the trusty-cogs branch.  
[The values](https://i.imgur.com/v12AAgj.png) are registered as environment variables. (You are **not** committing your Discord bot token to a git repository!)  
[Heroku console output](https://i.imgur.com/W9p1TZc.png): Error logs etc. can be found here.  
[The covfefe cog is loaded](https://i.imgur.com/4JOAY9I.png) because I explicitly told it to do so at the beginning.
