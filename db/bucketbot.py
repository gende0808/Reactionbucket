from discord.ext import commands
import discord
import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password123",
    database="bucketbot",
    use_unicode=True,
    charset='utf8mb4',
    port=3307
)
# bot token
token = "NTY0NDg5MDk5NTEyMzgxNDQw.XKondw.feVRAvJHQvImttAd8X7EBxSkfNw"
# Creates client and sets command prefixes to ! meaning that any function name can be called with ! before it.
client: commands.Bot = commands.Bot(command_prefix='b.')
client.remove_command('help')
mycursor = connection.cursor(buffered=True)


@client.command()
async def help(ctx):
    if ctx.guild is None:
        await ctx.send('ReactionBucket does not take commands through DM\'s')
    elif ctx.author.guild_permissions.manage_roles is True:
        await ctx.send(f'```diff'
                       f'\nReactionBucket Options:'
                       f'\n\n+   b.add_reaction_role [message ID] [emoji] ["existing role"]'
                       f'\n\n-       Sets a role to assign with a reaction to this specific message. Capitalization is '
                       f'important in the role name so copy it perfectly!'
                       f'\n\n+   b.remove_reaction_role [message ID] ["existing role"]'
                       f'\n\n-       Will no longer recognize any emoji that assigns this role. Capitalization is '
                       f'important for the role name so copy it perfectly!'
                       f'\n\n+   ADMIN ONLY: b.set_log_channel ["channel name"]'
                       f'\n\n-       Sets a channel to be the log for all role assignments/removals.'
                       f'\n\n+   ADMIN ONLY: b.remove_log_channel'
                       f'\n\n-       Stops the logging of role assignments.'
                       f'\n\n+   NEW: b.add_confirm_button [message ID] [emoji] ["existing role"]'
                       f'\n\n-       Sets a reaction to remove a role when clicked. '
                       f'Handy for newcomers to your server if you have a rules channel you want them to '
                       f'agree to having read.'
                       f'\n\n+   NEW (FREE!): b.add_timed_role [message ID] [emoji] ["existing role"] [lifespan in seconds]'
                       f'\n\n-       This reaction role only works for a limited time! Fun for events. Lifespan has to '
                       f'be assigned in seconds so for days/weeks/months that\'s a lot of seconds! '
                       f'Can be removed with b.remove_reaction_role.'
                       f'\n__________________________________________________________________________________'
                       f'\n https://www.patreon.com/ReactionBucket features:\n'
                       f'Absolutely nothing, everything is free! Please do consider supporting the bot though!'
                       f'\nSupport at https://www.reddit.com/r/ReactionBucket```'
                       )


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Role Handler | b.help'))


@client.event
async def on_guild_join(guild: discord.Guild):
    owner: discord.Member = guild.owner
    await owner.send(f'Hey there and thank you for installing ReactionBucket.'
                     f'\nTo get started make sure the bot has sufficient permissions'
                     f' (at least manage roles).\nFor the bot to be able to assign roles make sure the bot has a role '
                     f'that is higher up the hierarchy than the roles you want it to assign (see video).'
                     f'Only users who have permissions to manage roles will be able to use the bot.'
                     f'https://www.youtube.com/watch?v=WCfMYo2NGN8')
    sql = "INSERT INTO guild (guild_id, spam_channel) VALUES(%s, %s) ON DUPLICATE KEY UPDATE spam_channel = %s"
    update_values = (guild.id, 0, 0)
    mycursor.execute(sql, update_values)
    connection.commit()


@client.event
async def on_command_error(ctx: discord.ext.commands.Context, error):
    if ctx.guild is None:
        await ctx.send('ReactionBucket does not take commands through DM\'s')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('That command doesn\'t exist.')
    elif isinstance(error, commands.MissingPermissions):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.qualified_name == 'add_reaction_role':
            await ctx.send('It seems like you may have forgotten one of the arguments!\n'
                           'Please use the correct format: [command] [message ID] [emoji] ["existing role"] '
                           'example: \n\nb.add_reaction_role 50542471247133859 :wink: "League of Legends"')
        elif ctx.command.qualified_name == 'remove_reaction_role':
            await ctx.send('It seems like you may have forgotten one of the arguments!\n'
                           'Please use the correct format: [command] [message ID] ["existing role"] '
                           'example: \n\nb.remove_reaction_role 50542471247133859 "League of Legends"')
        elif ctx.command.qualified_name == 'set_log_channel':
            await ctx.send('It seems like you may have forgotten one of the arguments!\n'
                           'Please use the correct format: [command] ["channel name"] example:\n\n'
                           'b.set_log_channel "reactionlog"')
        elif ctx.command.qualified_name == 'add_timed_role':
            await ctx.send('It seems like you may have forgotten one of the arguments!\n'
                           'Please use the correct format: [command] [message ID] [emoji] ["existing role"] '
                           '[lifespan in seconds]'
                           'example: \n\nb.add_timed_role 50542471247133859 :wink: "League of Legends" 432000')
        elif ctx.command.qualified_name == 'add_confirm_button':
            await ctx.send('It seems like you may have forgotten one of the arguments!\n'
                           'Please use the correct format: [command] [message ID] [emoji] ["existing role"]'
                           'example: \n\nb.add_confirm_button 50542471247133859 :wink: "Newcomer"')
    elif isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'add_reaction_role':
            await ctx.send('It seems like you may have entered parameters in the wrong order '
                           'or tried wrong parameters!'
                           '\n Make sure the message id is correct and the role exists!'
                           '\nPlease use the correct format: [command] [message ID] [emoji] ["existing role"] '
                           'example: \n\nb.add_reaction_role 50542471247133859 :wink: "League Of Legends"')
            if ctx.command.qualified_name == 'add_timed_role':
                await ctx.send('It seems like you may have entered parameters in the wrong order '
                               'or tried wrong parameters!'
                               '\n Make sure the message id is correct and the role exists!'
                               '\nPlease use the correct format: [command] [message ID] [emoji] ["existing role"] '
                               '[lifespan in seconds]'
                               'example: \n\nb.add_timed_role 50542471247133859 :wink: "League Of Legends" 432000')
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
        elif ctx.command.qualified_name == 'add_confirm_button':
            await ctx.send('It seems like you may have entered parameters in the wrong '
                           'order or tried wrong parameters!'
                           '\nMake sure the channel exists and is typed properly with quotations! '
                           'Please use the correct format: [command] [message ID] [emoji] ["existing role"] '
                           'example: \n\nb.add_confirm_button 50542471247133859 :wink: "Newcomer"')
    else:
        await ctx.send('An unexpected general error has occurred. '
                       'Please try posting on reddit.com/r/reactionbucket or the official discord '
                       'to see if this can be solved. \n'
                       ' Make sure you can repeat the process and '
                       'describe exactly what caused the problem first though!\n'
                       ' Include the error if there is one below this: \n\n' + str(error))


@client.command()
async def add_confirm_button(ctx: discord.ext.commands.Context, message_id, emoji, role: discord.Role):
    if ctx.guild is None:
        await ctx.send('ReactionBucket does not take commands through DM\'s')
    elif ctx.author.guild_permissions.manage_roles is True:
        if ctx.author.top_role < role and ctx.author.guild_permissions.administrator is False:
            await ctx.send('It seems like that role is higher than your highest role so I won\'t be able to add that.')
        elif ctx.guild.me.top_role < role and ctx.guild.me.guild_permissions.administrator is False:
            await ctx.send('The role you tried to assign is higher than this bot\'s. '
                           'Please move me up in the hierarchy.')
        else:
            try:
                sql = "INSERT INTO welcome (message_id, emoji_id, role_id, guild_id) VALUES (%s, %s, %s, %s) " \
                      "ON DUPLICATE KEY UPDATE message_id = %s, emoji_id = %s, role_id = %s"
                val = (message_id, emoji, role.id, ctx.guild.id, message_id, emoji, role.id)
                mycursor.execute(sql, val)
                connection.commit()
                await ctx.send(f"Added {emoji} as the button to confirm server rules")
            except:
                await ctx.send("Something went horribly wrong! Please contact my creator on reddit.com/r/reactionbucket")


@client.command()
async def add_reaction_role(ctx: discord.ext.commands.Context, message_id, emoji, role: discord.Role):
    if ctx.guild is None:
        await ctx.send('ReactionBucket does not take commands through DM\'s')
    elif ctx.author.guild_permissions.manage_roles is True:
        if ctx.author.top_role < role and ctx.author.guild_permissions.administrator is False:
            await ctx.send('It seems like that role is higher than your highest role so I won\'t be able to add that.')
        elif ctx.guild.me.top_role < role and ctx.guild.me.guild_permissions.administrator is False:
            await ctx.send('The role you tried to assign is higher than this bot\'s. '
                           'Please move me up in the hierarchy.')
        else:
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
async def add_timed_role(ctx: discord.ext.commands.Context, message_id, emoji, role: discord.Role, seconds_until_expires):
    if ctx.guild is None:
        await ctx.send('ReactionBucket does not take commands through DM\'s')
    elif ctx.author.guild_permissions.manage_roles is True:
        if ctx.author.top_role < role and ctx.author.guild_permissions.administrator is False:
            await ctx.send('It seems like that role is higher than your highest role so I won\'t be able to add that.')
        elif ctx.guild.me.top_role < role and ctx.guild.me.guild_permissions.administrator is False:
            await ctx.send('The role you tried to assign is higher than this bot\'s. '
                           'Please move me up in the hierarchy.')
        else:
            try:
                sql = "INSERT INTO emoji (message_id, emoji_id, role_id, guild_id, valid_until) " \
                      "VALUES (%s, %s, %s, %s, DATE_ADD(NOW(), INTERVAL %s SECOND))"
                val = (message_id, emoji, role.id, ctx.guild.id, seconds_until_expires)
                mycursor.execute(sql, val)
                connection.commit()
                await ctx.send(f"Added {emoji} as the reaction to assign [{role.name}] as a role until it expires after"
                               f" {seconds_until_expires} seconds")
            except mysql.connector.errors.IntegrityError:
                sql = "SELECT role_id FROM emoji WHERE message_id = %s and emoji_id = %s and guild_id = %s"
                val = (message_id, emoji, ctx.guild.id)
                mycursor.execute(sql, val)
                old_role = ctx.guild.get_role(mycursor.fetchone()[0])
                await ctx.send(f"It would seem {emoji} is currently assigned to [{old_role.name}] already, "
                               f"use b.remove_reaction_role to unassign this first.")


@client.command()
async def remove_reaction_role(ctx: discord.ext.commands.Context, message_id, role: discord.Role):
    if ctx.guild is None:
        await ctx.send('ReactionBucket does not take commands through DM\'s')
    elif ctx.author.guild_permissions.manage_roles is True:
        if ctx.author.top_role < role and ctx.author.guild_permissions.administrator is False:
            await ctx.send('It seems like that role is higher than your highest role so '
                           'I won\'t be able to remove that.')
        elif ctx.guild.me.top_role < role and ctx.guild.me.guild_permissions.administrator is False:
            await ctx.send('The role you tried to remove is higher than this bot\'s. '
                           'Please move me up in the hierarchy.')
        else:
            sql = "DELETE FROM emoji WHERE role_id = %s AND guild_id = %s AND message_id = %s"
            val = (role.id, ctx.guild.id, message_id)
            mycursor.execute(sql, val)
            connection.commit()
            await ctx.send(f'```[{role.name}] will no longer be assigned by emojis in that message```')


@client.event
async def on_raw_reaction_add(raw: discord.RawReactionActionEvent):
    role_id = await get_role_from_db(raw)
    if role_id is not False:
        await remove_or_add_roles("add", role_id, raw)
    else:
        welcome_role_id = await get_welcome_role_from_db(raw)
        if welcome_role_id is not False:
            await remove_or_add_roles("remove", welcome_role_id[0], raw)
            if welcome_role_id[1] is not 0:
                await remove_or_add_roles("add", welcome_role_id[1], raw)


@client.event
async def on_raw_reaction_remove(raw):
    role_id = await get_role_from_db(raw)
    if role_id is not False:
        await remove_or_add_roles("remove", role_id, raw)


async def is_member(guild_id):
    sql = "SELECT guild_id FROM guild WHERE is_member = %s AND guild_id = %s"
    search_for = (True, guild_id)
    mycursor.execute(sql, search_for)
    result = mycursor.fetchone()
    if result is not None:
        return True
    else:
        return False


async def get_welcome_role_from_db(raw: discord.RawReactionActionEvent):
    if raw.emoji.is_custom_emoji():
        emoji_code = '<:' + raw.emoji.name + ':' + str(raw.emoji.id) + '>'
    else:
        emoji_code = raw.emoji.name
    sql = "SELECT role_id, optional_role_add FROM welcome WHERE message_id = %s AND emoji_id = %s"
    search_for = (raw.message_id, emoji_code)
    mycursor.execute(sql, search_for)
    result = mycursor.fetchone()
    if result is not None:
        return result[0]
    else:
        return False


async def get_role_from_db(raw: discord.RawReactionActionEvent):
    if raw.emoji.is_custom_emoji():
        emoji_code = '<:' + raw.emoji.name + ':' + str(raw.emoji.id) + '>'
    else:
        emoji_code = raw.emoji.name
    sql = "SELECT role_id FROM emoji WHERE (message_id = %s AND emoji_id = %s " \
          "AND valid_until IS NULL) OR (message_id = %s AND emoji_id = %s AND valid_until > NOW())"
    search_for = (raw.message_id, emoji_code, raw.message_id, emoji_code)
    mycursor.execute(sql, search_for)
    result = mycursor.fetchone()
    if result is not None:
        return result[0]
    else:
        return False


@client.command()
async def set_log_channel(ctx: discord.ext.commands.Context, spam_channel: discord.TextChannel):
    if ctx.guild is None:
        await ctx.send('ReactionBucket does not take commands through DM\'s')
    elif ctx.author.guild_permissions.administrator is True:
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
    if ctx.guild is None:
        await ctx.send('ReactionBucket does not take commands through DM\'s')
    elif ctx.author.guild_permissions.administrator is True:
        sql = 'UPDATE guild SET spam_channel = 0 WHERE guild_id = %s'
        val = (ctx.guild.id,)
        mycursor.execute(sql, val)
        connection.commit()
        await ctx.send(f'```logging has been disabled.```')


async def remove_or_add_roles(remove_or_add, role_id, raw: discord.RawReactionActionEvent):
    user_guild: discord.guild = client.get_guild(raw.guild_id)
    spam_channel = await get_spam_channel(raw)
    member: discord.Member = user_guild.get_member(raw.user_id)
    role: discord.Role = user_guild.get_role(role_id)
    if user_guild.me.guild_permissions.manage_roles is True and member is not None:
        if remove_or_add == "add":
            await member.add_roles(role)
            if spam_channel is not None:
                await spam_channel.send(f'```Gave {member} the {role.name} role```')
        if remove_or_add == "remove":
            await member.remove_roles(role)
            if spam_channel is not None:
                await spam_channel.send(f'```Removed {role.name} from {member}\'s roles```')
    else:
        if spam_channel is not None:
            await spam_channel.send(f'```Couldn\'t give or remove the role: {role.name} from {member} because I don\'t '
                                    f'have the permission to change roles```')


async def get_spam_channel(raw: discord.RawReactionActionEvent):
    sql = "SELECT spam_channel FROM guild WHERE guild_id = %s"
    search_for = (raw.guild_id,)
    mycursor.execute(sql, search_for)
    result = mycursor.fetchone()
    if result is not None:
        return client.get_channel(result[0])
    else:
        return None

client.run(token)
