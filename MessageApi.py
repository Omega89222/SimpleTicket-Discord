import discord
from discord.ext import commands


class MessageAPI:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_view(
        self,
        title_text: str = None,
        main_text: str = None,
        add_separator: bool = False,
        buttons: list[discord.ui.Button] = None,
        selects: list[discord.ui.Select] = None,
    ) -> discord.ui.LayoutView:

        container = discord.ui.Container()

        if title_text:
            container.add_item(discord.ui.TextDisplay(f"# {title_text}"))

        if add_separator:
            container.add_item(discord.ui.Separator())

        if main_text:
            container.add_item(discord.ui.TextDisplay(main_text))

        if buttons:
            row = discord.ui.ActionRow()
            for btn in buttons:
                if btn.style == discord.ButtonStyle.link:
                    row.add_item(btn)
                else:
                    if getattr(btn, "custom_id", None) is None:
                        btn.custom_id = f"btn_{btn.label.lower().replace(' ', '_')}"
                    row.add_item(btn)
            container.add_item(row)

        if selects:
            row = discord.ui.ActionRow()
            for sel in selects:
                if getattr(sel, "custom_id", None) is None:  
                    sel.custom_id = f"select_{sel.placeholder.lower().replace(' ', '_')}"
                row.add_item(sel)
            container.add_item(row)

        view = discord.ui.LayoutView(timeout=None) 
        view.add_item(container)
        return view