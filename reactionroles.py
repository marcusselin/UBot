import discord
from discord import ui, SelectOption
from dotenv import load_dotenv
from pathlib import Path

#Custom
from DatabaseHandler import DatabaseHandler
DatabaseHandlerUnit = DatabaseHandler()

env_dir = Path(__file__).resolve().parent
loaded = load_dotenv(env_dir / "conf" / "conf.env")
print(f"[INFO] [REACTIONROLES] Config state: {loaded}")

#Reaction roles dropdown
class ReactionRoles(discord.ui.View):
    def __init__(self, roles, user_id, guild_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.guild_id = guild_id

        self.add_item(ReactionRolesDropdown(roles, user_id, guild_id))

    @classmethod
    async def build(cls, interaction: discord.Interaction):
        raw_roles = DatabaseHandlerUnit.get_reaction_roles(interaction.guild.id)
        if not raw_roles:  # Empty. Return
            return None

        roles_parsed = []
        for rid, desc in raw_roles:
            role_obj = interaction.guild.get_role(rid)
            if role_obj:
                roles_parsed.append(
                    discord.SelectOption(
                        label=role_obj.name,
                        value=rid,
                        description=desc
                    )
                )

        if not roles_parsed:
            return None

        return cls(
            roles=roles_parsed,
            user_id=interaction.user.id,
            guild_id=interaction.guild.id
        )

class ReactionRolesDropdown(discord.ui.Select):
    def __init__(self, roles, user_id, guild_id):
        super().__init__(placeholder="Choose a role", options=roles)
        self.user_id = user_id
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        try:
            role_id = int(self.values[0])
            role = interaction.guild.get_role(role_id)
            msg = ""

            if (role in interaction.user.roles):
                #Remove
                await interaction.user.remove_roles(role)
                msg = f":white_check_mark: 𝑹𝒆𝒎𝒐𝒗𝒆𝒅 {role.mention} 𝒇𝒓𝒐𝒎 𝒚𝒐𝒖𝒓 𝒓𝒐𝒍𝒆𝒔!"
            else:
                #Give
                await interaction.user.add_roles(role)
                msg = f":white_check_mark: 𝑨𝒅𝒅𝒆𝒅 {role.mention} 𝒕𝒐 𝒚𝒐𝒖𝒓 𝒓𝒐𝒍𝒆𝒔!"

            #await interaction.message.delete()
            new_view = await ReactionRoles.build(interaction)
            await interaction.response.edit_message(content=msg, view=new_view)

        except Exception as e:
            await interaction.response.edit_message(content=f":x: **ERROR:** {e}", view=None)
