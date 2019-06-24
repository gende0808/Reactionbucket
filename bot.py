import json
from discord.ext import commands
import discord
import mysql.connector


connection = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="bucketbot",
  use_unicode=True,
  charset='utf8mb4'
)

# bot token
token = "NTY0NDg5MDk5NTEyMzgxNDQw.XKondw.feVRAvJHQvImttAd8X7EBxSkfNw"
# Creates client and sets command prefixes to ! meaning that any function name can be called with ! before it.
client: commands.Bot = commands.Bot(command_prefix='.')

# Opens the JSON file and loads it as a JSON object
roles_channel = 'buckettest'
emojifile = open('db/Emoji.json')
emojiList = json.load(emojifile)
emojifile.close()
mycursor = connection.cursor()


def convert_json_to_mariadb():
    for records in emojiList:
        sql = "INSERT INTO emoji (message_id, emoji_id, role_id) VALUES (%s, %s, %s)"
        val = (records[0], records[1], records[2])
        mycursor.execute(sql, val)
        connection.commit()


@client.event
async def on_command_error(ctx, error):
    if ctx.message.channel.name == 'buckettest':
        await ctx.send('Please use the correct format: [command] [message ID] [emoji] ["existing role"] '
                       'example: .manage_role 50542471247133859 :wink: "League Of Legends"')


@client.command()
async def manage_role(ctx, message_id: discord.Message.id, emoji, role: discord.Role):
    if ctx.author.top_role.name == "Admin":
        if isinstance(emoji, discord.Emoji):
            emoji = emoji.id
        emojiList.append([message_id, emoji, role.id])
        with open('db/Emoji.json', 'w') as fp:
            json.dump(emojiList, fp)
        await ctx.send(f"Added {emoji} as the reaction to be assigned {role} as a role")


@client.event
async def on_raw_reaction_add(raw):
    channel = client.get_channel(raw.channel_id)
    if channel.name == roles_channel:
        role_id = await get_role_from_db(raw)
        await remove_or_add_roles("add", role_id, raw)
        # TODO Below can be deleted after initial roles are added
        # if channel.name == 'roles':
        # if raw.emoji.is_custom_emoji():
        #     emoji_code = '<:' + raw.emoji.name + ':' + str(raw.emoji.id) + '>'
        #     await check_db_for_emoji(emoji_code)
        # else:
        #     await check_db_for_emoji(raw.emoji.name)


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
