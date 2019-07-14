from discord.ext import commands
import discord
import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="bucketbot",
    use_unicode=True,
    charset='utf8mb4',
    port=3306
)
# test token
token = 'NTk4OTc5MDI2Mzc5NDcyOTA4.XSehHw.c-RNf1ijHyr-TyApLvDLiy0vHpI'
# Creates client and sets command prefixes to ! meaning that any function name can be called with ! before it.
client: commands.Bot = commands.Bot(command_prefix='b.')
roles_channel = 'reactionbucket'
mycursor = connection.cursor()


@client.event
async def on_command_error(ctx, error):
    if ctx.channel.name == roles_channel:
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('That command doesn\'t exist.')
        elif isinstance(error, commands.MissingRequiredArgument):
            if ctx.command.qualified_name == 'add_reaction_role':
                await ctx.send('It seems like you may have forgotten one of the arguments!\n'
                               'Please use the correct format: [command] [message ID] [emoji] ["existing role"] '
                               'example: \n\nb.add_reaction_role 50542471247133859 :wink: "League Of Legends"')
            elif ctx.command.qualified_name == 'remove_reaction_role':
                await ctx.send('It seems like you may have forgotten one of the arguments!\n'
                               'Please use the correct format: [command] [message ID] ["existing role"] '
                               'example: \n\nb.remove_reaction_role 50542471247133859 "League Of Legends"')
            elif ctx.command.qualified_name == 'set_log_channel':
                await ctx.send('It seems like you may have forgotten one of the arguments!\n'
                               'Please use the correct format: [command] ["channel name"] example:\n\n'
                               'b.set_log_channel "reactionlog"')
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'add_reaction_role':
                await ctx.send('It seems like you may have entered parameters in the wrong order '
                               'or tried wrong parameters!'
                               '\n Make sure the message id is correct and the role exists!'
                               '\nPlease use the correct format: [command] [message ID] [emoji] ["existing role"] '
                               'example: \n\nb.add_reaction_role 50542471247133859 :wink: "League Of Legends"')
            elif ctx.command.qualified_name == 'remove_reaction_role':
                await ctx.send('It seems like you may have entered parameters in the wrong order '
                               'or tried wrong parameters!'
                               '\n Make sure the message id is correct and the role exists!'
                               '\nPlease use the correct format: [command] [message ID] ["existing role"] '
                               'example: \n\nb.remove_reaction_role 50542471247133859 "League Of Legends"')
            elif ctx.command.qualified_name == 'set_log_channel':
                await ctx.send('It seems like you may have entered parameters in the wrong '
                               'order or tried wrong parameters!'
                               '\n Make sure the channel exists and is typed properly with quotations!'
                               'Please use the correct format: [command] ["channel name"] example:\n\n'
                               'b.set_log_channel "rolelog"')
        else:
            await ctx.send('An unexpected general error has occurred. '
                           'Please contact Sandbucket#6689 to see if this can be solved. \n'
                           ' Make sure you can repeat the process and '
                           'describe exactly what caused the problem first though!\n'
                           ' Include the error if there is one below this: \n\n' + str(error))


@client.command()
async def add_reaction_role(ctx: discord.ext.commands.Context, message_id, emoji, role: discord.Role):
    if ctx.channel.name == roles_channel:
        try:
            sql = "INSERT INTO emoji (message_id, emoji_id, role_id, guild_id) VALUES (%s, %s, %s, %s)"
            val = (message_id, emoji, role.id, ctx.guild.id)
            mycursor.execute(sql, val)
            connection.commit()
            await ctx.send(f"Added {emoji} as the reaction to assign [{role.name}] as a role")
        except mysql.connector.errors.IntegrityError:
            sql = "SELECT role_id FROM emoji WHERE message_id = %s and emoji_id = %s and guild_id = %s"
            val = (message_id, emoji, ctx.guild.id)
            mycursor.execute(sql, val)
            old_role = ctx.guild.get_role(mycursor.fetchone()[0])
            await ctx.send(f"It would seem {emoji} is currently assigned to [{old_role.name}] already, "
                           f"use b.remove_reaction_role to unassign this first.")


@client.command()
async def remove_reaction_role(ctx, message_id, role: discord.Role):
    if ctx.channel.name == roles_channel:
        sql = "DELETE FROM emoji WHERE role_id = %s AND guild_id = %s AND message_id = %s"
        val = (role.id, ctx.guild.id, message_id)
        mycursor.execute(sql, val)
        connection.commit()
        await ctx.send(f'```[{role.name}] will no longer be assigned by emojis in that message```')


@client.event
async def on_raw_reaction_add(raw):
    role_id = await get_role_from_db(raw)
    if role_id is not False:
        await remove_or_add_roles("add", role_id, raw)


@client.event
async def on_raw_reaction_remove(raw):
    role_id = await get_role_from_db(raw)
    if role_id is not False:
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


@client.command()
async def set_log_channel(ctx: discord.ext.commands.Context, spam_channel: discord.TextChannel):
    if ctx.channel.name == roles_channel:
        if client.get_channel(spam_channel.id) is not None:
            sql = "INSERT INTO guild (guild_id, spam_channel) VALUES(%s, %s) ON DUPLICATE KEY UPDATE spam_channel = %s"
            update_values = (ctx.guild.id, spam_channel.id, spam_channel.id)
            mycursor.execute(sql, update_values)
            connection.commit()
            await ctx.send(f'#{spam_channel.name} is now the log for role assignments')
        else:
            await ctx.send(f'That channel ID doesn\'t seem to exist on this server!')


@client.command()
async def remove_log_channel(ctx: discord.ext.commands.Context):
    if ctx.channel.name == roles_channel:
        sql = "DELETE FROM guild WHERE guild_id = %s"
        val = (ctx.guild.id,)
        mycursor.execute(sql, val)
        connection.commit()
        await ctx.send(f'```logging has been disabled.```')


async def remove_or_add_roles(remove_or_add, role_id, raw: discord.RawReactionActionEvent):
    spam_channel = 0
    sql = "SELECT spam_channel FROM guild WHERE guild_id = %s"
    search_for = (raw.guild_id,)
    mycursor.execute(sql, search_for)
    result = mycursor.fetchone()
    if result is not None:
        spam_channel = client.get_channel(result[0])
    user_guild: discord.guild = client.get_guild(raw.guild_id)
    member = user_guild.get_member(raw.user_id)
    role = user_guild.get_role(role_id)
    if remove_or_add == "add":
        await member.add_roles(role)
        await spam_channel.send(f'```Gave {member.name} the {role.name} role```') if spam_channel != 0 else False
    if remove_or_add == "remove":
        await member.remove_roles(role)
        await spam_channel.send(f'```Removed {role.name} from {member.name}\'s roles```') if spam_channel != 0 else False


client.run(token)
# async def set_role():
#     game = discord.Game("Custom Role Bot")
#     await client.change_presence(status=discord.Status.idle, activity=game)

