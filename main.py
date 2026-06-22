import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
import io
import math
import asyncio
from discord.ext import tasks
from typing import Literal

#Custom
from DatabaseHandler import DatabaseHandler
from reactionroles import ReactionRoles

DatabaseHandlerUnit = DatabaseHandler()
from store import StoreView
from pathlib import Path

#Load config
env_dir = Path(__file__).resolve().parent
loaded = load_dotenv(env_dir / "conf" / "conf.env")
print(f"[INFO] [MAIN] Config state: {loaded}")

#Import config
TOKEN = os.getenv("TOKEN")
SERVERID = os.getenv("SERVERID")
oneTokenAmount = int(os.getenv("ONETOKENAMOUNT"))

#Initialize
guild = discord.Object(int(SERVERID))
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents, help_commands=None)

@bot.event
async def on_ready():
    #Global var
    global allowed
    allowed = True

    #await bot.user.edit(username="𝑴𝑺𝑮𝑻𝒓𝒂𝒄𝒌𝒆𝒓")

    activity = discord.Activity(type=discord.ActivityType.listening, name=f"𝒏𝒆𝒘 𝒎𝒆𝒔𝒔𝒂𝒈𝒆𝒔 𝒕𝒐 𝒌𝒆𝒆𝒑 𝒕𝒓𝒂𝒄𝒌 𝒉𝒐𝒘 𝒎𝒖𝒄𝒉 𝒖𝒔𝒆𝒓𝒔 𝒉𝒂𝒗𝒆 𝒔𝒆𝒏𝒕 𝒕𝒉𝒆𝒎")
    await bot.change_presence(status=discord.Status.idle, activity=activity)

    #Extension load
    await bot.load_extension("messagelistener")

    #Sync commands
    #bot.tree.remove_command("gettokens")
    try:
        #synced = await bot.tree.sync(guild=guild)
        synced = await bot.tree.sync()
        print(f"Synced total of {len(synced)} commands")
    except Exception as e:
        print(f"Err: {e}")
    
    try:
        changeStatus = True
        with open(env_dir / "status.txt", "r") as fs:
            status = fs.read().strip()
            if status == "maintenance":
                changeStatus = False
                allowed = False
        
        if changeStatus:
            with open(env_dir / "status.txt", "w") as f:
                f.write("online")
            for g in bot.guilds:
                channel_id = DatabaseHandlerUnit.get_channel_id(g.id)
                role_id = DatabaseHandlerUnit.get_role_id(g.id)
                role = None
                if role_id:
                    role = g.get_role(role_id)
                if channel_id:
                    channel = bot.get_channel(channel_id)
                    if channel:
                        if role is None:
                            await channel.send(":information_source: 𝑰 𝒂𝒎 𝒃𝒂𝒄𝒌 𝒐𝒏 𝒕𝒓𝒂𝒄𝒌 :sunglasses: 𝑪𝒐𝒎𝒆 𝒂𝒏𝒅 𝒆𝒂𝒓𝒏 𝒎𝒐𝒓𝒆 𝒕𝒐𝒌𝒆𝒏𝒔 :coin:" )
                        else:
                            await channel.send(f":information_source: {role.mention} 𝑰 𝒂𝒎 𝒃𝒂𝒄𝒌 𝒐𝒏 𝒕𝒓𝒂𝒄𝒌 :sunglasses: 𝑪𝒐𝒎𝒆 𝒂𝒏𝒅 𝒆𝒂𝒓𝒏 𝒎𝒐𝒓𝒆 𝒕𝒐𝒌𝒆𝒏𝒔 :coin:" )
    except:
        print("status.txt is missing...")

    check_status.start()

#Check current status (to shutdown)
@tasks.loop(seconds=5)
async def check_status():
    mstatus = 0
    try:
        with open(env_dir / "maintenace.txt", "r") as f:
            mstatus = int(f.read().strip())
    except:
        print("maintenace.txt is missing...")
    
    try:
        with open(env_dir / "status.txt", "r") as f:
            status = f.read().strip()
            #print(f"{status} and {mstatus}")
            if status == "offline":
                for g in bot.guilds:
                    role_id = DatabaseHandlerUnit.get_role_id(g.id)
                    role = None
                    if role_id:
                        role = g.get_role(role_id)
                    channel_id = DatabaseHandlerUnit.get_channel_id(g.id)
                    if channel_id:
                        channel = bot.get_channel(channel_id)
                        if channel:
                            if role is None:
                                await channel.send(f":information_source: 𝑰 𝒂𝒎 𝒔𝒉𝒖𝒕𝒕𝒊𝒏𝒈 𝒅𝒐𝒘𝒏. 𝑪𝒐𝒎𝒆 𝒃𝒂𝒄𝒌 𝒍𝒂𝒕𝒆𝒓 𝒕𝒐 𝒆𝒂𝒓𝒏 𝒎𝒐𝒓𝒆 𝒕𝒐𝒌𝒆𝒏𝒔!")
                            else:
                                await channel.send(f":information_source: {role.mention} 𝑰 𝒂𝒎 𝒔𝒉𝒖𝒕𝒕𝒊𝒏𝒈 𝒅𝒐𝒘𝒏. 𝑪𝒐𝒎𝒆 𝒃𝒂𝒄𝒌 𝒍𝒂𝒕𝒆𝒓 𝒕𝒐 𝒆𝒂𝒓𝒏 𝒎𝒐𝒓𝒆 𝒕𝒐𝒌𝒆𝒏𝒔!")
                await bot.close()
            elif status == "maintenance" and mstatus == 0:
                for g in bot.guilds:
                    role_id = DatabaseHandlerUnit.get_role_id(g.id)
                    role = None
                    if role_id:
                        role = g.get_role(role_id)
                    channel_id = DatabaseHandlerUnit.get_channel_id(g.id)
                    if channel_id:
                        channel = bot.get_channel(channel_id)
                        if channel:
                            if role is None:
                                await channel.send(f":information_source: 𝑰 𝒂𝒎 𝒊𝒏 𝒎𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 :tools: 𝒔𝒐 𝒊 𝒘𝒐𝒏𝒕 𝒘𝒐𝒓𝒌 𝒑𝒓𝒐𝒑𝒆𝒓𝒍𝒚 𝒆𝒗𝒆𝒏 𝒕𝒐𝒖𝒈𝒉 𝒊 𝒎𝒊𝒈𝒉𝒕 𝒃𝒆 𝒐𝒏𝒍𝒊𝒏𝒆. 𝑺𝒐𝒓𝒓𝒚 𝒇𝒐𝒓 𝒕𝒉𝒆 𝒊𝒏𝒄𝒐𝒏𝒗𝒆𝒏𝒊𝒆𝒏𝒄𝒆!")
                            else:
                                await channel.send(f":information_source: {role.mention} 𝑰 𝒂𝒎 𝒊𝒏 𝒎𝒂𝒊𝒏𝒕𝒆𝒏𝒂𝒏𝒄𝒆 :tools: 𝒔𝒐 𝒊 𝒘𝒐𝒏𝒕 𝒘𝒐𝒓𝒌 𝒑𝒓𝒐𝒑𝒆𝒓𝒍𝒚 𝒆𝒗𝒆𝒏 𝒕𝒐𝒖𝒈𝒉 𝒊 𝒎𝒊𝒈𝒉𝒕 𝒃𝒆 𝒐𝒏𝒍𝒊𝒏𝒆. 𝑺𝒐𝒓𝒓𝒚 𝒇𝒐𝒓 𝒕𝒉𝒆 𝒊𝒏𝒄𝒐𝒏𝒗𝒆𝒏𝒊𝒆𝒏𝒄𝒆!")
                await bot.close()
    except:
        pass        

#COMMANDS----------------------------------------------------------------------------------------
#Reconf the value
@bot.tree.command(name="setvalue", description="Reconfigure the amount of messages sent by user")
@app_commands.describe(user="The user whose amounts you want to reconfigure", value="The new value")
async def setvalue(interaction: discord.Interaction, user: discord.Member, value: int):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return

        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
            
        if user.bot:
            raise TypeError("Invalid user type")
        uid = user.id
        name = user.name
        DatabaseHandlerUnit.set_value(uid, value, name, interaction.guild.id)
        await interaction.response.send_message(f":information_source: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒔𝒆𝒕 𝒖𝒔𝒆𝒓 **{user.mention}** 𝒎𝒆𝒔𝒔𝒂𝒈𝒆 𝒂𝒎𝒐𝒖𝒏𝒕 𝒊𝒏 𝒕𝒉𝒆 𝒅𝒂𝒕𝒂𝒃𝒂𝒔𝒆 𝒕𝒐 **{value}**")
    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#Get data from spesific user
@bot.tree.command(name="get", description="Get data from spesific user")
@app_commands.describe(user="The user whose data you want to view")
async def get(interaction: discord.Interaction, user: discord.Member):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
            
        if user.bot:
            raise TypeError("Invalid user type")
        uid = user.id
        name = user.name

        #Messages
        amount = DatabaseHandlerUnit.get_value(interaction.guild.id, uid)
        if not amount:
            amount = 0

        #Tokens
        tokens_raw = amount / oneTokenAmount
        additional = DatabaseHandlerUnit.get_additional(user.id, interaction.guild.id)
        if not additional:
            additional = 0
        additional = int(additional)
        tokens_earned = math.floor(tokens_raw) + additional
        
        #Levels
        level = DatabaseHandlerUnit.get_level(user.id, interaction.guild.id)
        if level is None:
            level = 0

        await interaction.response.send_message(f"### **{user.mention}** *({uid})*:\n𝑺𝒆𝒏𝒕 𝒎𝒆𝒔𝒔𝒂𝒈𝒆𝒔: {amount}\n𝑩𝒂𝒍𝒂𝒏𝒄𝒆: {tokens_earned} :coin:\n𝑳𝒆𝒗𝒆𝒍: {level}")
    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#Get all the data
@bot.tree.command(name="getall", description="Returns all amounts of sent messages from every user that has sent something")
async def getall(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.followup.send(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
            
        data = DatabaseHandlerUnit.getalldata(interaction.guild.id)
        if data is None:
            await interaction.followup.send(":no_entry: 𝑴𝒚 𝒅𝒂𝒕𝒂𝒃𝒂𝒔𝒆 𝒂𝒑𝒑𝒆𝒂𝒓𝒔 𝒕𝒐 𝒃𝒆 𝒆𝒎𝒑𝒕𝒚, 𝒔𝒐 𝒊 𝒄𝒂𝒏𝒏𝒐𝒕 𝒇𝒆𝒕𝒄𝒉 𝒊𝒕 :face_with_diagonal_mouth:")
            return
        #Create text file
        #Create temp
        txt_buffer = io.StringIO()
        #Write data
        txt_buffer.write(data)
        #Go to the top of the file
        txt_buffer.seek(0)

        discord_file = discord.File(fp=txt_buffer, filename="data.txt")
        await interaction.followup.send("𝑰 𝒉𝒂𝒗𝒆 𝒇𝒆𝒕𝒄𝒉𝒆𝒅 𝒂𝒍𝒍 𝒕𝒉𝒆 𝒅𝒂𝒕𝒂 𝒇𝒓𝒐𝒎 𝒎𝒚 𝒅𝒂𝒕𝒂𝒃𝒂𝒔𝒆, 𝒉𝒆𝒓𝒆𝒔 𝒕𝒉𝒆 𝒓𝒆𝒔𝒖𝒍𝒕:", file=discord_file)
    except Exception as e:
        await interaction.followup.send(f"**ERROR:** {e}")

#Configure
@bot.tree.command(name="configure", description="Configure bot")
@app_commands.describe(channel="The channel where i send e.g. status notifications", role="The role which i will ping always when my status changes")
async def configure(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
        
        channel_id = channel.id
        DatabaseHandlerUnit.set_channel_id(interaction.guild.id, channel_id, role.id)
        await interaction.response.send_message(f":information_source: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒄𝒐𝒏𝒇𝒊𝒈𝒖𝒓𝒆𝒅 𝒕𝒉𝒆 𝒃𝒐𝒕, 𝑰 𝒘𝒊𝒍𝒍 𝒔𝒆𝒏𝒅 𝒏𝒐𝒕𝒊𝒇𝒊𝒄𝒂𝒕𝒊𝒐𝒏𝒔 𝒕𝒐 𝒄𝒉𝒂𝒏𝒏𝒆𝒍 **{channel.name}** 𝒂𝒏𝒅 𝒘𝒊𝒍𝒍 𝒏𝒐𝒕𝒊𝒇𝒚 𝒓𝒐𝒍𝒆 {role.mention}!")
    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#Clear database
@bot.tree.command(name="clear", description="Clears all databases of data about this server")
async def clear(interaction: discord.Interaction):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
            
        DatabaseHandlerUnit.clear_user_data(interaction.guild.id)
        DatabaseHandlerUnit.clear_store_data(interaction.guild.id)
        DatabaseHandlerUnit.clear_config(interaction.guild.id)
        await interaction.response.send_message(f":information_source: 𝑨𝒍𝒍 𝒕𝒉𝒊𝒔 𝒔𝒆𝒓𝒗𝒆𝒓 𝒅𝒂𝒕𝒂 𝒇𝒓𝒐𝒎 𝒕𝒉𝒆 𝒅𝒂𝒕𝒂𝒃𝒂𝒔𝒆𝒔 𝒘𝒂𝒔 𝒆𝒓𝒂𝒔𝒆𝒅 𝒔𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚!")
    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#Clear per user data
@bot.tree.command(name="clearusers", description="Clears the per user data")
async def clearusers(interaction: discord.Interaction):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
            
        DatabaseHandlerUnit.clear_user_data(interaction.guild.id)
        await interaction.response.send_message(f":information_source: 𝑨𝒍𝒍 𝒅𝒂𝒕𝒂 𝒇𝒓𝒐𝒎 𝒕𝒉𝒆 𝒖𝒔𝒆𝒓 𝒅𝒂𝒕𝒂𝒃𝒂𝒔𝒆 𝒘𝒂𝒔 𝒆𝒓𝒂𝒔𝒆𝒅 𝒔𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚!")
    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")    
    
#Clear config

@bot.tree.command(name="clearconfig", description="Clears the configuration data")
async def clearconfig(interaction: discord.Interaction):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
            
        DatabaseHandlerUnit.clear_config(interaction.guild.id)
        await interaction.response.send_message(f":information_source: 𝑪𝒐𝒏𝒇𝒊𝒈𝒖𝒓𝒂𝒕𝒊𝒐𝒏 𝒅𝒂𝒕𝒂 𝒘𝒂𝒔 𝒆𝒓𝒂𝒔𝒆𝒅 𝒔𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚!")
    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")    

#Increase tokens manually

@bot.tree.command(name="givetokens", description="Give tokens to spesific user")
@app_commands.describe(user="The user whose token amount you want to increase", tokens="Amount of tokens you want to give")
async def givetokens(interaction: discord.Interaction, user: discord.Member, tokens: int):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
        
        DatabaseHandlerUnit.increase_additional(user.id, tokens, user.name, interaction.guild.id)
        await interaction.response.send_message(f":information_source: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒂𝒅𝒅𝒆𝒅 {tokens} :coin: 𝒕𝒐 {user.mention}")
    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#Open store
@bot.tree.command(name="store", description="Open the store")
async def store(interaction: discord.Interaction):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        view = StoreView()
        await interaction.response.send_message("𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝒕𝒐 𝒕𝒉𝒆 𝒕𝒐𝒌𝒆𝒏 𝒔𝒕𝒐𝒓𝒆!", view=view, ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#Add a new role to the store
@bot.tree.command(name="storeaddrole", description="Add role to the store")
@app_commands.describe(role="The role to add", price="The price of the role")
async def storeaddrole(interaction: discord.Interaction, role: discord.Role, price: int):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return

        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return

        storerole_pos = role.position
        bot_role_pos = interaction.guild.me.top_role.position

        if storerole_pos > bot_role_pos:
            await interaction.response.send_message(f":x: 𝑰 𝒄𝒂𝒏𝒏𝒐𝒕 𝒂𝒅𝒅 𝒓𝒐𝒍𝒆 {role.mention} 𝒕𝒐 𝒔𝒕𝒐𝒓𝒆 𝒃𝒆𝒄𝒂𝒖𝒔𝒆 𝒊𝒕𝒔 𝒑𝒐𝒔𝒊𝒕𝒊𝒐𝒏 𝒊𝒔 𝒉𝒊𝒈𝒉𝒆𝒓 𝒕𝒉𝒂𝒏 𝒎𝒚 𝒉𝒊𝒈𝒉𝒆𝒔𝒕 𝒓𝒐𝒍𝒆 𝒑𝒐𝒔𝒊𝒕𝒊𝒐𝒏, 𝒘𝒉𝒊𝒄𝒉 𝒎𝒆𝒂𝒏𝒔 𝒊 𝒅𝒐𝒏𝒕 𝒉𝒂𝒗𝒆 𝒑𝒆𝒓𝒎𝒊𝒔𝒔𝒊𝒐𝒏𝒔 𝒕𝒐 𝒈𝒊𝒗𝒆 𝒊𝒕!", ephemeral=True)
            return

        if price <= 0:
            await interaction.response.send_message(f":x: 𝑷𝒓𝒊𝒄𝒆 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 0 𝒐𝒓 𝒍𝒆𝒔𝒔!", ephemeral=True)
            return

        DatabaseHandlerUnit.add_role_to_store(role.id, price, interaction.guild.id)
        await interaction.response.send_message(f":information_source: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒂𝒅𝒅𝒆𝒅 {role.mention} 𝒘𝒊𝒕𝒉 𝒑𝒓𝒊𝒄𝒆 𝒐𝒇 {price} :coin: 𝒕𝒐 𝒕𝒉𝒆 𝒔𝒕𝒐𝒓𝒆!")

    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

@bot.tree.command(name="removerole", description="Removes spesific role offer from store")
@app_commands.describe(role="Role to remove from the store")
async def removerole(interaction: discord.Interaction, role: discord.Role):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
        
        DatabaseHandlerUnit.remove_role_from_store(role.id, interaction.guild.id)
        await interaction.response.send_message(f":information_source: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒓𝒆𝒎𝒐𝒗𝒆𝒅 𝒓𝒐𝒍𝒆 {role.mention} 𝒐𝒇𝒇𝒆𝒓 𝒇𝒓𝒐𝒎 𝒕𝒉𝒆 𝒔𝒕𝒐𝒓𝒆!")

    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#Add a new levelup to the store
@bot.tree.command(name="storeaddlevelup", description="Add level-up to the store")
@app_commands.describe(levels="The amount of levels", price="The price of the level-up")
async def storeaddlevelup(interaction: discord.Interaction, levels: int, price: int):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return

        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return

        if price <= 0:
            await interaction.response.send_message(f":x: 𝑷𝒓𝒊𝒄𝒆 𝒄𝒂𝒏𝒏𝒐𝒕 𝒃𝒆 0 𝒐𝒓 𝒍𝒆𝒔𝒔!", ephemeral=True)
            return

        DatabaseHandlerUnit.add_levelup_to_store(levels, price, interaction.guild.id)
        await interaction.response.send_message(f":information_source: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒂𝒅𝒅𝒆𝒅 𝑳𝒆𝒗𝒆𝒍-𝑼𝒑 𝒐𝒇 {levels} 𝒍𝒆𝒗𝒆𝒍𝒔 𝒘𝒊𝒕𝒉 𝒑𝒓𝒊𝒄𝒆 𝒐𝒇 {price} :coin: 𝒕𝒐 𝒕𝒉𝒆 𝒔𝒕𝒐𝒓𝒆!")

    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

@bot.tree.command(name="removelevelup", description="Removes spesific Level-Up offer from store")
@app_commands.describe(levelup="Level-Up to remove from the store (Level)")
async def removerole(interaction: discord.Interaction, levelup: int):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
        
        DatabaseHandlerUnit.remove_level_from_store(levelup, interaction.guild.id)
        await interaction.response.send_message(f":information_source: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒓𝒆𝒎𝒐𝒗𝒆𝒅 𝑳𝒆𝒗𝒆𝒍-𝑼𝒑 {levelup} 𝒐𝒇𝒇𝒆𝒓 𝒇𝒓𝒐𝒎 𝒕𝒉𝒆 𝒔𝒕𝒐𝒓𝒆!")

    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#Set levels
@bot.tree.command(name="setlevel", description="Sets spesific user level")
@app_commands.describe(user="The user whose level you want to set", level="new level for the user")
async def setlevel(interaction: discord.Interaction, user: discord.Member, level: int):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return
        
        uid = user.id
        name = user.name
        DatabaseHandlerUnit.set_level(uid, name, level, interaction.guild.id)
        await interaction.response.send_message(f":information_source: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒔𝒆𝒕 {user.mention} 𝒍𝒆𝒗𝒆𝒍 𝒕𝒐 {level}")

    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#Show leaderboard (levels)
@bot.tree.command(name="leaderboard", description="Show top 10 members leaderboard")
@app_commands.describe(by="By levels or tokens")
async def leaderboard_levels(interaction: discord.Interaction, by: Literal["Levels", "Tokens"]):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return
        
        if by == "Levels":
            data = DatabaseHandlerUnit.get_top10_levels(interaction.guild.id)
            if data is None:
                await interaction.response.send_message("𝑵𝒐 𝒅𝒂𝒕𝒂 𝒂𝒗𝒂𝒊𝒃𝒍𝒆 :[")
                return

            leaderboard_text = "## 🏆 𝑻𝒐𝒑 10 𝑴𝒆𝒎𝒃𝒆𝒓𝒔 𝒃𝒚 𝑳𝒆𝒗𝒆𝒍𝒔 🏆\n"
            for i, (name, level) in enumerate(data, start=1):
                leaderboard_text += f"{i}. {name}: 𝑳𝒆𝒗𝒆𝒍 {level}\n"
            
            await interaction.response.send_message(leaderboard_text)
        else:
            raw_data = DatabaseHandlerUnit.get_tokens_for_leaderboard(interaction.guild.id)
            if raw_data is None:
                await interaction.response.send_message("𝑵𝒐 𝒅𝒂𝒕𝒂 𝒂𝒗𝒂𝒊𝒃𝒍𝒆 :[")
                return

            data = []
            for name, value, additional in raw_data:
                if additional is None:
                    additional = 0
                tokens_raw = value / oneTokenAmount
                tokens_earned = math.floor(tokens_raw) + int(additional)
                data.append((name, tokens_earned))

            sorted_data = sorted(data, key=lambda x: x[1], reverse=True)[:10]

            leaderboard_text = "## 🏆 𝑻𝒐𝒑 10 𝑴𝒆𝒎𝒃𝒆𝒓𝒔 𝒃𝒚 𝑻𝒐𝒌𝒆𝒏𝒔 🏆\n"
            for i, (name, tokens_earned) in enumerate(sorted_data, start=1):
                leaderboard_text += f"{i}. {name}: {tokens_earned} :coin:\n"
            
            await interaction.response.send_message(leaderboard_text)

    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#UTILITY COMMANDS--------------------------------------------
@bot.tree.command(name="reactionroles", description="Show message that allows users to choose roles")
async def reaction_roles(interaction: discord.Interaction):
    if not allowed and interaction.guild.id != int(SERVERID):
        await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
        return

    try:
        view = await ReactionRoles.build(interaction)
        if view is None:
            await interaction.response.send_message(content="𝑹𝒆𝒂𝒄𝒕𝒊𝒐𝒏 𝒓𝒐𝒍𝒆 𝒍𝒊𝒔𝒕 𝒆𝒎𝒑𝒕𝒚 :pensive:")
            return

        await interaction.response.send_message("", view=view, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

@bot.tree.command(name="addreactionrole", description="Add reaction role to the avaible roles list")
@app_commands.describe(role="The role to add", description="Short description of what this role is")
async def add_reaction_role(interaction: discord.Interaction, role: discord.Role, description: str):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return

        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return

        if (DatabaseHandlerUnit.has_reaction_role(role.id, interaction.guild.id)):
            await interaction.response.send_message(
                f":no_entry_sign: {role.mention} 𝒂𝒍𝒓𝒆𝒂𝒅𝒚 𝒆𝒙𝒊𝒔𝒕𝒔 𝒊𝒏 𝒂𝒗𝒂𝒊𝒍𝒂𝒃𝒍𝒆 𝒓𝒆𝒂𝒄𝒕𝒊𝒐𝒏 𝒓𝒐𝒍𝒆𝒔 𝒍𝒊𝒔𝒕!")
            return

        DatabaseHandlerUnit.add_reaction_role(role.id, description, interaction.guild.id)
        await interaction.response.send_message(
            f":white_check_mark: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒂𝒅𝒅𝒆𝒅 {role.mention} 𝒕𝒐 𝒕𝒉𝒆 𝒍𝒊𝒔𝒕 𝒐𝒇 𝒂𝒗𝒂𝒊𝒍𝒂𝒃𝒍𝒆 𝒓𝒆𝒂𝒄𝒕𝒊𝒐𝒏 𝒓𝒐𝒍𝒆𝒔!")

    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

@bot.tree.command(name="removereactionrole", description="Remove reaction role from the avaible roles list")
@app_commands.describe(role="The role to add")
async def add_reaction_role(interaction: discord.Interaction, role: discord.Role):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return

        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return

        if (DatabaseHandlerUnit.has_reaction_role(role.id, interaction.guild.id)):
            DatabaseHandlerUnit.remove_reaction_role(role.id, interaction.guild.id)
            await interaction.response.send_message(
                f":white_check_mark: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒓𝒆𝒎𝒐𝒗𝒆𝒅 {role.mention} 𝒇𝒓𝒐𝒎 𝒕𝒉𝒆 𝒍𝒊𝒔𝒕 𝒐𝒇 𝒂𝒗𝒂𝒊𝒍𝒂𝒃𝒍𝒆 𝒓𝒆𝒂𝒄𝒕𝒊𝒐𝒏 𝒓𝒐𝒍𝒆𝒔")
        else:
            await interaction.response.send_message(f":no_entry_sign: 𝑹𝒐𝒍𝒆 𝒏𝒐𝒕 𝒐𝒏 𝒕𝒉𝒆 𝒓𝒆𝒂𝒄𝒕𝒊𝒐𝒏 𝒓𝒐𝒍𝒆𝒔 𝒍𝒊𝒔𝒕!")

    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

@bot.tree.command(name="removeallroles", description="Remove all roles from all members")
async def remove_all_roles(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.followup.send(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return

        if not interaction.user == interaction.guild.owner:
            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return

        success = 0
        failed = 0

        async for user in interaction.guild.fetch_members(limit=None):
            if user.bot:
                continue #No bots
            try:
                for role in user.roles:
                    if role == interaction.guild.default_role or role.managed or role >= interaction.guild.me.top_role:
                        continue
                    try:
                        await user.remove_roles(role)
                    except Exception as e:
                        print(e)
                success += 1
            except Exception as e: #This occurs if we fail to remove roles
                failed += 1
                print(e)
                continue

        if failed == 0:
            await interaction.followup.send(
                f":white_check_mark: 𝑹𝒆𝒎𝒐𝒗𝒆𝒅 𝒂𝒍𝒍 𝒓𝒐𝒍𝒆𝒔 𝒇𝒓𝒐𝒎 {success} 𝒖𝒔𝒆𝒓𝒔")
        else:
            await interaction.followup.send(
                f":warning: 𝑹𝒆𝒎𝒐𝒗𝒆𝒅 𝒂𝒍𝒍 𝒓𝒐𝒍𝒆𝒔 𝒇𝒓𝒐𝒎 {success} 𝒖𝒔𝒆𝒓𝒔 𝒂𝒏𝒅 𝒇𝒂𝒊𝒍𝒆𝒅 𝒕𝒐 𝒓𝒆𝒎𝒐𝒗𝒆 𝒇𝒓𝒐𝒎 {failed} 𝒖𝒔𝒆𝒓𝒔 (𝑪𝒉𝒆𝒄𝒌 𝒕𝒉𝒆 𝒓𝒐𝒍𝒆𝒔 - 𝑰 𝒄𝒂𝒏𝒏𝒐𝒕 𝒓𝒆𝒎𝒐𝒗𝒆 𝒔𝒖𝒑𝒆𝒓𝒊𝒐𝒓 𝒓𝒐𝒍𝒆𝒔!)")

    except Exception as e:
        await interaction.followup.send(f":x: **ERROR:** {e}")

@bot.tree.command(name="changename", description="Change the name of the bot")
@app_commands.describe(name="New name for the bot")
async def change_name(interaction: discord.Interaction, name: str):
    try:
        if not allowed and interaction.guild.id != int(SERVERID):
            await interaction.response.send_message(f":x: 𝑺𝒆𝒓𝒗𝒆𝒓 𝒅𝒆𝒏𝒊𝒆𝒅 𝒕𝒉𝒆 𝒓𝒆𝒒𝒖𝒆𝒔𝒕", ephemeral=True)
            return

        if not interaction.user == interaction.guild.owner:
            await interaction.response.send_message(f":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
            return

        await interaction.guild.me.edit(nick=name)
        await interaction.response.send_message(
            f":tada: 𝑴𝒚 𝒏𝒂𝒎𝒆 𝒊𝒔 𝒏𝒐𝒘 {name}!")

    except Exception as e:
        await interaction.response.send_message(f":x: **ERROR:** {e}")

#MAIN
bot.run(TOKEN)