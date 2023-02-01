# EscapeBot

A 24/7 Text-adventure game bot (non-profit) deployed on fly.io with GitHub Action.

## Invite the bot to your DC server
> **Warning**
> Don't use it in a community or a large server.  

https://discord.com/api/oauth2/authorize?client_id=861144762358169626&permissions=59392&scope=bot

## How to use it
`help`: Show the detailed command list.  
`escape N`: Start a new text adventure.  
`clear {num}`: Clear {num} messages in the channel.

## Command in Game
Example plot:
> I have a [ball] on the [floor].  
> Obtained command: `look-at`

You may type `look-at ball` and the bot may response you `It is a basketball`.

## Version log
- v0.1: Released level 1
- v0.2: Added record system and fixed some bugs.
- v0.3: Made the bot suitable for a server, supporting multiple players.
    - v0.3.1: Optimized. Added General extension
    - v0.3.2: Deployed 24/7 service and fixed bugs.
    - v0.3.3: Added the clear command to clean the chat room.
- v0.4: Updated Discord API to 2.0 and redeployed the service.
- v0.5: Revised to English version.
