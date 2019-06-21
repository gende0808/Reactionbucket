import json
from discord.ext import commands
import discord
from discord.ext.commands import has_permissions, MissingPermissions

#bot token
token = "NTY0NDg5MDk5NTEyMzgxNDQw.XKondw.feVRAvJHQvImttAd8X7EBxSkfNw"
# Creates client and sets command prefixes to ! meaning that any function name can be called with ! before it.
client = commands.Bot(command_prefix='.')

# Opens the JSON file and loads it as a JSON object
emojifile = open('db/Emoji.json')
emojiDict = json.load(emojifile)
emojifile.close()


@client.command()
async def modify_role(ctx, emoji="", rolename=""):
    if ctx.author.top_role.name == "Admin":
        if emoji != "" and rolename != "":
            emojiDict.update({emoji: rolename})
            with open('db/Emoji.json', 'w') as fp:
                json.dump(emojiDict, fp)
            await ctx.send(f"Added {emoji} as the reaction to be assigned {rolename} as a role")
        else:
            await ctx.send('Please use the correct format: [command] [emoji] ["game"] '
                           'example: .modify_role :wink: "League Of Legends"')


@client.event
async def on_raw_reaction_add(raw):
    channel = client.get_channel(raw.channel_id)
    user: discord.member = client.get_user(raw.user_id)
    if channel.name == 'buckettest':
        if raw.emoji in emojiDict:
            # Finds out what 'guild' a user is in and gets the role by ID
            role = user.guild.get_role(emojiDict[raw.emoji])
            await user.add_roles(role)
    if channel.name == 'roles':
        print(json.dumps(raw.emoji.name))

@client.event
async def on_raw_reaction_remove(raw):
    channel = client.get_channel(raw.channel_id)
    user = client.get_user(raw.user_id)
    if channel.name == 'buckettest':
        if raw.emoji in emojiDict:
            # Finds out what 'guild' a user is in and gets the role by ID
            role = user.guild.get_role(emojiDict[raw.emoji])
            await user.remove_roles(role)
    if channel.name == 'roles':
        print("Hey")
        print(raw.emoji.name.encode('utf-8'))

client.run(token)
