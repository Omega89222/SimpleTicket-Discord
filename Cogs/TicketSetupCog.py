import discord
from discord.ext import commands
from discord import app_commands
from MessageApi import MessageAPI
import json
import os

CONFIG_FILE = "ticket_config.json"

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        ticket_config = json.load(f)
else:
    ticket_config = {}


def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(ticket_config, f, indent=4)


class TicketCloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Fermer le ticket", style=discord.ButtonStyle.danger, custom_id="ticket_close")

    async def callback(self, interaction: discord.Interaction):
        await interaction.channel.delete()


class TicketSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api = MessageAPI(bot)
        options = [
            discord.SelectOption(label="Recrutement", description="Pour être recruté", emoji="🔓"),
            discord.SelectOption(label="Alliance", description="Pour faire une alliance", emoji="⌛"),
        ]
        super().__init__(placeholder="Choisis une option", min_values=1, max_values=1, options=options, custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        guild = interaction.guild
        member = interaction.user

        config = ticket_config.get(str(guild.id))
        if not config:
            view = self.api.get_view(
                main_text="⚠️ Le système de tickets n'a pas encore été configuré avec `/ticket_config`."
            )
            await interaction.response.send_message(view=view, ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        staff_role = guild.get_role(config["staff_role"])
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        category = guild.get_channel(config["category_id"])

        if choice == "Recrutement":
            ticket_channel = await guild.create_text_channel(
                name=f"rc-{member.name}".lower().replace(" ", "-"),
                overwrites=overwrites,
                topic=f"Ticket ouvert par {member.name} ({member.id})",
                category=category
            )
            view_ticket = self.api.get_view(
                title_text=f"Ticket de {member.mention}",
                main_text=(
                    "Merci d'attendre un staff.\n"
                    "Appuie sur le bouton **Fermer le ticket** pour fermer le ticket.\n\n"
                    "Merci de fournir **ton pseudo** après ce message."
                ),
                add_separator=False,
                buttons=[TicketCloseButton()]
            )
            view_confirm = self.api.get_view(
                main_text="✅ Ticket créé !"
            )
            await interaction.response.send_message(view=view_confirm, ephemeral=True)
            await ticket_channel.send(view=view_ticket)

        elif choice == "Alliance":
            ticket_channel = await guild.create_text_channel(
                name=f"ally-{member.name}".lower().replace(" ", "-"),
                overwrites=overwrites,
                topic=f"Ticket ouvert par {member.name} ({member.id})",
                category=category
            )
            view_ticket = self.api.get_view(
                title_text=f"Ticket de {member.mention}",
                main_text=(
                    "Merci d'attendre un staff.\n"
                    "Appuie sur le bouton **Fermer le ticket** pour fermer le ticket.\n\n"
                    "Merci de fournir **ton pseudo** et **ta faction** après ce message."
                ),
                add_separator=False,
                buttons=[TicketCloseButton()]
            )
            view_confirm = self.api.get_view(
                main_text="✅ Ticket créé !"
            )
            await interaction.response.send_message(view=view_confirm, ephemeral=True)
            await ticket_channel.send(view=view_ticket)


class TicketSetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api = MessageAPI(bot)

    @app_commands.command(name="ticket_setup", description="Placer le sélecteur de tickets dans le salon")
    async def ticket_setup(self, interaction: discord.Interaction):
        config = ticket_config.get(str(interaction.guild.id))
        if not config:
            view = self.api.get_view(
                main_text="⚠️ Vous devez d'abord configurer le système avec `/ticket_config`."
            )
            await interaction.response.send_message(view=view, ephemeral=True)
            return

        view = self.api.get_view(
            title_text="Support",
            main_text="Vous pouvez créer un ticket pour être **recruté** ou pour faire **une alliance**.\n\nTout abus sera sanctionné.",
            add_separator=True,
            selects=[TicketSelect(self.bot)]
        )
        await interaction.channel.send(view=view)
        confirm = self.api.get_view(
            main_text="✅ Sélecteur de tickets placé dans ce salon."
        )
        await interaction.response.send_message(view=confirm, ephemeral=True)

    @app_commands.command(name="ticket_config", description="Configurer le système de tickets")
    async def ticket_config_cmd(self, interaction: discord.Interaction, category: discord.CategoryChannel, staff_role: discord.Role):
        ticket_config[str(interaction.guild.id)] = {
            "category_id": category.id,
            "staff_role": staff_role.id
        }
        save_config()
        view = self.api.get_view(
            title_text="Configuration ticket",
            main_text=f"✅ Configuration sauvegardée :\n- Catégorie : {category.mention}\n- Rôle staff : {staff_role.mention}\n\n> Utilisez `/ticket_setup` pour placer le sélecteur."
        )
        await interaction.response.send_message(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketSetupCog(bot))