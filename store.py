import discord
from discord.ext import commands
from discord import ui, SelectOption
import math
from dotenv import load_dotenv
import os
from pathlib import Path

#Custom
from DatabaseHandler import DatabaseHandler
DatabaseHandlerUnit = DatabaseHandler()

env_dir = Path(__file__).resolve().parent
loaded = load_dotenv(env_dir / "conf" / "conf.env")
print(f"[INFO] [STORE] Config state: {loaded}")

oneTokenAmount = int(os.getenv("ONETOKENAMOUNT"))

#Store
class StoreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) #timeout=None
    
    @discord.ui.button(label="𝑩𝒖𝒚 𝒍𝒆𝒗𝒆𝒍𝒔", style=discord.ButtonStyle.green)
    async def buylevelsbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        levelupoptions = DatabaseHandlerUnit.get_levelups(interaction.guild.id)
        if not levelupoptions:
            view = ShoppingFailureLevelups()
            await interaction.response.edit_message(content=f"𝑵𝒐 𝑳𝒆𝒗𝒆𝒍-𝒖𝒑𝒔 𝒊𝒏 𝒔𝒕𝒐𝒄𝒌 :[", view=view)
            return
        
        view = LevelUpStoreView(levelupoptions, interaction.user.id, interaction.guild.id)
        await interaction.response.edit_message(content="𝑳𝒆𝒗𝒆𝒍-𝒖𝒑𝒔 𝒊𝒏 𝒔𝒕𝒐𝒄𝒌:", view=view)

    @discord.ui.button(label="𝑩𝒖𝒚 𝒓𝒐𝒍𝒆𝒔", style=discord.ButtonStyle.blurple)
    async def buyrolesbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles = DatabaseHandlerUnit.get_roles(interaction.guild.id)
        if not roles:
            view = ShoppingFailureRoles()
            await interaction.response.edit_message(content=f"𝑵𝒐 𝒓𝒐𝒍𝒆𝒔 𝒊𝒏 𝒔𝒕𝒐𝒄𝒌 :[", view=view)
            return
        
        roles_with_names = []
        for rid, price in roles:
            role_obj = interaction.guild.get_role(rid)
            if role_obj:
                roles_with_names.append((rid, price, role_obj.name))
        
        view = RoleStoreView(roles_with_names, interaction.user.id, interaction.guild.id)
        await interaction.response.edit_message(content="𝑹𝒐𝒍𝒆𝒔 𝒊𝒏 𝒔𝒕𝒐𝒄𝒌:", view=view)
#----------------------------------------------------------------------------------------------------------
#Buy role
#Main
class RoleStoreView(ui.View):
    def __init__(self, roles, user_id, guild_id):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.guild_id = guild_id

        options = [
            SelectOption(label=f"{role_name}", value=str(role_id), description=f"𝑷𝒓𝒊𝒄𝒆: {price} 𝒕𝒐𝒌𝒆𝒏𝒔")
            for role_id, price, role_name in roles
        ]

        self.add_item(RoleDropdown(options, self.user_id, self.guild_id))
        self.add_item(BackButtonToMain())

class RoleDropdown(ui.Select):
    def __init__(self, options, user_id, guild_id):
        super().__init__(placeholder="𝑪𝒉𝒐𝒐𝒔𝒆 𝒂 𝒓𝒐𝒍𝒆", options=options)
        self.user_id = user_id
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return

            #Get role id & price
            role_id = int(self.values[0])
            price = DatabaseHandlerUnit.get_role_price(role_id, interaction.guild.id)

            #Get user tokens
            value = DatabaseHandlerUnit.get_value(interaction.guild.id, interaction.user.id, ) or 0
            additional = DatabaseHandlerUnit.get_additional(interaction.user.id, interaction.guild.id) or 0
            tokens = math.floor(value / oneTokenAmount) + additional

            if tokens < price:
                view = ShoppingFailureRoles()
                await interaction.response.edit_message(content=f":no_entry: 𝒀𝒐𝒖 𝒅𝒐𝒏'𝒕 𝒉𝒂𝒗𝒆 𝒆𝒏𝒐𝒖𝒈𝒉 𝒕𝒐𝒌𝒆𝒏𝒔!", view=view)
                return

            role = interaction.guild.get_role(role_id)

            await interaction.user.add_roles(role)
            DatabaseHandlerUnit.decrease_additional(interaction.user.id, price, interaction.user.name, interaction.guild.id)
            view = ShoppingSuccessRoles()
            await interaction.response.edit_message(content=f":shopping_cart: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒃𝒐𝒖𝒈𝒉𝒕 𝒓𝒐𝒍𝒆 {role.mention} 𝒇𝒐𝒓 {price} :coin:", view=view)

        except Exception as e:
            await interaction.response.edit_message(content=f":x: **ERROR:** {e}", view=None)

class BackButtonToMain(ui.Button):
    def __init__(self):
        super().__init__(label="𝑩𝒂𝒄𝒌", style=discord.ButtonStyle.red)
    
    async def callback(self, interaction: discord.Interaction):
        view = StoreView()
        await interaction.response.edit_message(content="𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝒕𝒐 𝒕𝒉𝒆 𝒕𝒐𝒌𝒆𝒏 𝒔𝒕𝒐𝒓𝒆!", view=view)

class ShoppingSuccessRoles(ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(BackButtonToMain())

class ShoppingFailureRoles(ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(BackButtonToMain())
#----------------------------------------------------------------------------------------------------------
#Buy level up
#Main
class LevelUpStoreView(ui.View):
    def __init__(self, levelups, user_id, guild_id):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.guild_id = guild_id

        options = [
            SelectOption(label=f"{levels} 𝒍𝒆𝒗𝒆𝒍𝒔", value=levels, description=f"𝑷𝒓𝒊𝒄𝒆: {price} 𝒕𝒐𝒌𝒆𝒏𝒔")
            for levels, price in levelups
        ]

        self.add_item(LevelUpDropdown(options, self.user_id, self.guild_id))
        self.add_item(BackButtonToMain())
    
class LevelUpDropdown(ui.Select):
    def __init__(self, options, user_id, guild_id):
        super().__init__(placeholder="𝑪𝒉𝒐𝒐𝒔𝒆 𝒍𝒆𝒗𝒆𝒍𝒖𝒑:", options=options)
        self.user_id = user_id
        self.guild_id = guild_id
    
    async def callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(":x: 𝑨𝒄𝒄𝒆𝒔𝒔 𝑫𝒆𝒏𝒊𝒆𝒅", ephemeral=True)
                return

            #Get level up amount & price
            levelup_amount = int(self.values[0])
            price = DatabaseHandlerUnit.get_levelup_price(levelup_amount, interaction.guild.id)

            #Get user tokens
            value = DatabaseHandlerUnit.get_value(interaction.guild.id, interaction.user.id, ) or 0
            additional = DatabaseHandlerUnit.get_additional(interaction.user.id, interaction.guild.id) or 0
            tokens = math.floor(value / oneTokenAmount) + additional

            if tokens < price:
                view = ShoppingFailureLevelups()
                await interaction.response.edit_message(content=f":no_entry: 𝒀𝒐𝒖 𝒅𝒐𝒏'𝒕 𝒉𝒂𝒗𝒆 𝒆𝒏𝒐𝒖𝒈𝒉 𝒕𝒐𝒌𝒆𝒏𝒔!", view=view)
                return

            DatabaseHandlerUnit.increase_level(interaction.user.id, levelup_amount, interaction.guild.id)
            current_level = DatabaseHandlerUnit.get_level(interaction.user.id, interaction.guild.id)
            if current_level is None:
                current_level = 0
            DatabaseHandlerUnit.decrease_additional(interaction.user.id, price, interaction.user.name, interaction.guild.id)
            view = ShoppingSuccessLevelups()
            await interaction.response.edit_message(content=f":shopping_cart: 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝒃𝒐𝒖𝒈𝒉𝒕 {levelup_amount} 𝒍𝒆𝒗𝒆𝒍𝒔 𝒇𝒐𝒓 {price} :coin:\n{interaction.user.mention}, 𝒀𝒐𝒖 𝒂𝒓𝒆 𝒏𝒐𝒘 𝒂𝒕 𝒍𝒆𝒗𝒆𝒍 {current_level}!", view=view)

        except Exception as e:
            await interaction.response.edit_message(content=f":x: **ERROR:** {e}", view=None)

class ShoppingSuccessLevelups(ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(BackButtonToMain())

class ShoppingFailureLevelups(ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(BackButtonToMain())