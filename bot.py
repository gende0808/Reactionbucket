import json
from discord.ext import commands
import discord
import mysql.connector
from discord.utils import get

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password123",
    database="bucketbot",
    use_unicode=True,
    charset='utf8mb4'
)

# bot token
token = "NTY0NDg5MDk5NTEyMzgxNDQw.XKondw.feVRAvJHQvImttAd8X7EBxSkfNw"
# Creates client and sets command prefixes to ! meaning that any function name can be called with ! before it.
client: commands.Bot = commands.Bot(command_prefix='.')

# assign_channel = 'reactionbucket'
roles_channel = 'roles'
mycursor = connection.cursor()


@client.event
async def on_command_error(ctx, error):
    if ctx.message.channel.name == roles_channel:
        await ctx.send('Please use the correct format: [command] [message ID] [emoji] ["existing role"] '
                       'example: \n\n\n.manage_role 50542471247133859 :wink: "League Of Legends"')


@client.command()
async def add_reaction_role(ctx, message_id, emoji, role: discord.Role):
    if ctx.author.top_role.name == "Admin":
        sql = "INSERT INTO emoji (message_id, emoji_id, role_id) VALUES (%s, %s, %s)"
        val = (message_id, emoji, role.id)
        try:
            mycursor.execute(sql, val)
            connection.commit()
            await ctx.send(f"Added {emoji} as the reaction to assign [{role.name}] as a role")
        except mysql.connector.errors.IntegrityError:
            sql = "SELECT role_id FROM emoji WHERE message_id = %s and emoji_id = %s"
            val = (message_id, emoji)
            mycursor.execute(sql, val)
            old_role = ctx.guild.get_role(mycursor.fetchone()[0])
            await ctx.send(f"```It would seem {emoji} is currently assigned to [{old_role.name}] already, "
                           f"use .remove_reaction_role to unassign this first.```")


@client.command()
async def remove_reaction_role(ctx, role: discord.Role):
    if ctx.author.top_role.name == 'Admin':
        sql = "DELETE FROM emoji WHERE role_id = %s"
        try:
            val = (role.id,)
            mycursor.execute(sql, val)
            connection.commit()
            await ctx.send(f'```[{role.name}] will no longer be assigned by emojis```')
        except discord.ext.commands.errors.BadArgument:
            await ctx.send('```That role does not exist. Remember that roles are case-sensitive!```')


@client.event
async def on_raw_reaction_add(raw):
    channel = client.get_channel(raw.channel_id)
    if channel.name == roles_channel:
        role_id = await get_role_from_db(raw)
        await remove_or_add_roles("add", role_id, raw)


@client.event
async def on_raw_reaction_remove(raw):
    channel = client.get_channel(raw.channel_id)
    if channel.name == roles_channel:
        role_id = await get_role_from_db(raw)
        await remove_or_add_roles("remove", role_id, raw)


async def get_role_from_db(raw: discord.RawReactionActionEvent):
    if raw.emoji.is_custom_emoji():
        emoji_code = '<:' + raw.emoji.name + ':' + str(raw.emoji.id) + '>'
    else:
        emoji_code = raw.emoji.name
    sql = "SELECT role_id FROM emoji WHERE message_id = %s AND emoji_id = %s"
    search_for = (raw.message_id, emoji_code)
    mycursor.execute(sql, search_for)
    result = mycursor.fetchone()
    if result is not None:
        return result[0]
    else:
        return False


async def remove_or_add_roles(remove_or_add, role_id, raw: discord.RawReactionActionEvent):
    user_guild: discord.guild = client.get_guild(raw.guild_id)
    member = user_guild.get_member(raw.user_id)
    if role_id is not False:
        role = user_guild.get_role(role_id)
        if remove_or_add == "add":
            await member.add_roles(role)
        if remove_or_add == "remove":
            await member.remove_roles(role)


client.run(token)
