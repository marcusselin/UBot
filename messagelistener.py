import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from pathlib import Path

#Custom
from DatabaseHandler import DatabaseHandler
DatabaseHandlerUnit = DatabaseHandler()

env_dir = Path(__file__).resolve().parent
loaded = load_dotenv(env_dir / "conf" / "conf.env")
print(f"[INFO] [MESSAGELISTENER] Config state: {loaded}")
SERVERID = os.getenv("SERVERID")
MESSAGESREQUIREDTOLEVELUP = int(os.getenv("MESSAGESREQUIREDTOLEVELUP"))

class msgTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = {}
    
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            #channel_id = DatabaseHandlerUnit.get_channel_id(message.guild.id)
            #if not channel_id:
                #return
            #if message.channel.id != channel_id:
                #return

            allowed = True
            with open(env_dir / "status.txt", "r") as fs:
                status = fs.read().strip()
                if status == "maintenance" and int(message.guild.id) != int(SERVERID):
                    allowed = False
                    print(f"[WARN] Denied request")

            if not allowed:
                return

            #Ignore bots, process only users
            if message.author.bot:
                return

            uid = message.author.id
            name = message.author.name
            if uid in self.users:
                self.users[uid] += 1
            else:
                self.users[uid] = 1

            if self.users[uid] == MESSAGESREQUIREDTOLEVELUP:
                #Increase level (MESSAGESREQUIREDTOLEVELUP messages = 1 level)
                DatabaseHandlerUnit.increase_level(uid, name, 1, message.guild.id)
                self.users[uid] = 0
                channel_id = DatabaseHandlerUnit.get_channel_id(message.guild.id)
                if channel_id:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        #Get current level
                        currentlevel = DatabaseHandlerUnit.get_level(uid, message.guild.id)
                        if currentlevel is None:
                            currentlevel = 0

                        user = message.author
                        #Profile picture (URL)
                        avatar = user.display_avatar.url

                        embed = discord.Embed(
                            title=f":chart_with_upwards_trend: 𝑳𝒆𝒗𝒆𝒍-𝒖𝒑!",
                            description=f"𝑪𝒐𝒏𝒈𝒓𝒂𝒕𝒔 {user.mention}, 𝒚𝒐𝒖 𝒂𝒓𝒆 𝒏𝒐𝒘 𝒂𝒕 𝒍𝒆𝒗𝒆𝒍 **{currentlevel}** :tada:",
                            color=discord.Color.gold()
                        )
                        embed.set_thumbnail(url=avatar)

                        await channel.send(embed=embed)


            #Increase sent messages
            DatabaseHandlerUnit.increase_value(uid, name, message.guild.id)
        
        except Exception as e:
            print("[WARN] Invalid message, ignoring")
            print(e)
            return


async def setup(bot):
    await bot.add_cog(msgTracker(bot))