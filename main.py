import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime, UTC
import io
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("discord")

TOKEN = "YOUR_DISCORD_BOT_TOKEN"
GUILD_ID = 123456789012345678
TICKET_CATEGORIES = {
    "🛠️ Support": 123456789012345678,
    "🚨 Report": 123456789012345678,
    "🤝 Partner": 123456789012345678
}
TRANSCRIPT_CHANNEL_ID = 123456789012345678
CLAIM_ROLE_ID = 123456789012345678
INACTIVE_TIMEOUT = 24

ticket_counters = {key: 0 for key in TICKET_CATEGORIES.keys()}
ticket_data = {}
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

class RenameModal(Modal, title="✏️ Rename Ticket"):
    new_name = TextInput(label="Enter new ticket name", placeholder="support-123")

    async def on_submit(self, interaction: discord.Interaction):
        if CLAIM_ROLE_ID not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("🚫 You don't have permission to rename this ticket.", ephemeral=True)
        await interaction.channel.edit(name=self.new_name.value)
        await interaction.response.send_message(f"✏️ Ticket renamed to **{self.new_name.value}**.", ephemeral=False)

class CloseModal(Modal, title="🔒 Close Ticket"):
    reason = TextInput(label="Reason for closing", placeholder="Describe why this ticket is being closed.")

    async def on_submit(self, interaction: discord.Interaction):
        await save_transcript(interaction.channel, interaction.user)
        await interaction.response.send_message(f"🔒 Ticket closed for reason: **{self.reason.value}**.", ephemeral=False)
        await interaction.channel.delete()

def create_embed(title, description, color=discord.Color.blue(), thumbnail=None, image=None, footer=None):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now(UTC))
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if footer:
        embed.set_footer(text=footer["text"], icon_url=footer["icon_url"])
    return embed

async def generate_transcript(channel):
    transcript = ""
    async for message in channel.history(limit=None, oldest_first=True):
        timestamp = message.created_at.strftime("[%Y-%m-%d %H:%M:%S]")
        transcript += f"{timestamp} {message.author.name}: {message.content}\n"
    return transcript

async def save_transcript(channel, closer):
    transcript_content = await generate_transcript(channel)
    transcript_channel = bot.get_channel(TRANSCRIPT_CHANNEL_ID)

    opened_at = channel.created_at.replace(tzinfo=UTC)
    closed_at = datetime.now(UTC)
    duration = closed_at - opened_at

    opener = bot.get_user(ticket_data[channel.id]["user_id"]) if channel.id in ticket_data else None
    opener_tag = opener.mention if opener else "Unknown"

    claimed_by = ticket_data[channel.id]["claimed_by"] if channel.id in ticket_data else None
    claimed_by_user = bot.get_user(claimed_by) if claimed_by else None
    claimed_by_tag = claimed_by_user.mention if claimed_by_user else "Not Claimed"

    staff_messages = 0
    async for message in channel.history(limit=None):
        if CLAIM_ROLE_ID in [role.id for role in message.author.roles]:
            staff_messages += 1

    file_buffer = io.BytesIO(transcript_content.encode("utf-8"))
    file_buffer.seek(0)
    file = discord.File(fp=file_buffer, filename=f"transcript-{channel.name}.txt")

    staff_embed = create_embed(
        title="📜 **Ticket Transcript**",
        description=(
            "Here is the complete transcript of the ticket. Below you will find all the details about the ticket, "
            "including who opened it, who closed it, and how long it was active.\n\n"
            "**Ticket Details:**\n"
            f"• **Opened By:** {opener_tag}\n"
            f"• **Claimed By:** {claimed_by_tag}\n"
            f"• **Closed By:** {closer.mention}\n"
            f"• **Opened At:** {opened_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• **Closed At:** {closed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• **Duration:** {str(duration)}\n"
            f"• **Category:** {channel.category.name if channel.category else 'Unknown'}\n"
            f"• **Staff Messages:** {staff_messages}\n\n"
            "**Transcript:**\n"
            "The full transcript is attached as a `.txt` file below."
        ),
        color=discord.Color.blue(),
        thumbnail=channel.guild.icon.url,
        image="https://example.com/banner.png",
        footer={"text": f"Ticket ID: {channel.id} | Closed by {closer.name}", "icon_url": closer.avatar.url}
    )

    await transcript_channel.send(file=file, embed=staff_embed)

    user_details_embed = create_embed(
        title="📜 **Your Ticket Transcript**",
        description=(
            "Here is the transcript of your ticket. Below you will find all the details about the ticket, "
            "including who closed it and how long it was active.\n\n"
            "**Ticket Details:**\n"
            f"• **Closed By:** {closer.mention}\n"
            f"• **Closed At:** {closed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• **Duration:** {str(duration)}\n"
            f"• **Category:** {channel.category.name if channel.category else 'Unknown'}\n\n"
            "Thank you for using our support system! 🙏"
        ),
        color=discord.Color.blue(),
        thumbnail=channel.guild.icon.url,
        footer={"text": f"Ticket ID: {channel.id}", "icon_url": closer.avatar.url}
    )

    user_transcript_embed = create_embed(
        title="📄 **Full Transcript**",
        description=f"```{transcript_content}```",
        color=discord.Color.blue(),
        thumbnail=channel.guild.icon.url,
        footer={"text": f"Ticket ID: {channel.id}", "icon_url": closer.avatar.url}
    )

    if opener:
        try:
            await opener.send(embed=user_details_embed)
            await opener.send(embed=user_transcript_embed)
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {opener.name}. They might have DMs disabled.")

class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="🎫 Select a category to open a ticket",
        options=[
            discord.SelectOption(label=cat, description=f"Open a {cat} ticket", emoji=cat.split()[0])
            for cat in TICKET_CATEGORIES.keys()
        ],
        custom_id="ticket_panel_select"
    )
    async def ticket_select(self, interaction: discord.Interaction, select: Select):
        category_name = select.values[0]
        category_id = TICKET_CATEGORIES[category_name]
        category = discord.utils.get(interaction.guild.categories, id=category_id)
        global ticket_counters
        ticket_counters[category_name] += 1

        ticket_channel = await interaction.guild.create_text_channel(
            f"{category_name.split()[1].lower()}-{ticket_counters[category_name]}", category=category)

        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"🎟️ Your ticket has been created: {ticket_channel.mention}", ephemeral=True)

        ticket_data[ticket_channel.id] = {
            "user_id": interaction.user.id,
            "claimed_by": None
        }

        embed = create_embed(
            title=f"🎟️ {category_name} Ticket Opened",
            description=(
                f"Hello {interaction.user.mention}, thank you for reaching out! A {category_name} ticket has been opened for you.\n\n"
                "**What happens next?**\n"
                "1. A member of our support team will be with you shortly.\n"
                "2. Please provide as much detail as possible about your issue or request.\n"
                "3. Use the buttons below to manage your ticket.\n\n"
                "**Guidelines:**\n"
                "• Be respectful and patient.\n"
                "• Do not share personal or sensitive information.\n"
                "• Use the `🔒 Close` button to close the ticket once your issue is resolved."
            ),
            color=discord.Color.blue(),
            thumbnail=interaction.guild.icon.url,
            image="https://example.com/banner.png",
            footer={"text": f"Opened by {interaction.user.name}", "icon_url": interaction.user.avatar.url}
        )
        view = TicketControls()
        staff_role = discord.utils.get(interaction.guild.roles, id=CLAIM_ROLE_ID)
        await ticket_channel.send(f"{staff_role.mention} {interaction.user.mention}, a new {category_name} ticket has been opened!", embed=embed, view=view)

class TicketControls(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Claim", style=discord.ButtonStyle.success, emoji="✅", custom_id="ticket_claim_button")
    async def claim_button(self, interaction: discord.Interaction, button: Button):
        if CLAIM_ROLE_ID not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("🚫 You don't have permission to claim this ticket.", ephemeral=True)
        await interaction.channel.edit(name=f"{interaction.channel.name}-claimed")
        ticket_data[interaction.channel.id]["claimed_by"] = interaction.user.id
        await interaction.response.send_message(f"🎟️ {interaction.user.mention} has claimed this ticket!", ephemeral=False)

    @discord.ui.button(label="✏️ Rename", style=discord.ButtonStyle.secondary, emoji="✏️", custom_id="ticket_rename_button")
    async def rename_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RenameModal())

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close_button")
    async def close_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(CloseModal())

@tasks.loop(hours=1)
async def check_inactive_tickets():
    guild = bot.get_guild(GUILD_ID)
    for channel in guild.text_channels:
        if channel.category and channel.category.name == "Tickets":
            last_message = await channel.history(limit=1).flatten()
            if last_message:
                last_message_time = last_message[0].created_at
                if (datetime.now(UTC) - last_message_time).total_seconds() > INACTIVE_TIMEOUT * 3600:
                    await channel.send("🔒 This ticket is being closed due to inactivity.")
                    await save_transcript(channel, bot.user)
                    await channel.delete()

@bot.event
async def on_ready():
    logger.info(f"{bot.user} is online! 🎉")
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game("Managing Tickets"))
    await bot.tree.sync()
    logger.info("All commands are synced successfully!")
    guild = bot.get_guild(GUILD_ID)
    for category_name, category_id in TICKET_CATEGORIES.items():
        if not discord.utils.get(guild.categories, id=category_id):
            await guild.create_category(category_name)
    check_inactive_tickets.start()

    bot.add_view(TicketPanel())
    bot.add_view(TicketControls())

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):
    embed = create_embed(
        title="🎫 **Ticket System**",
        description=(
            "Welcome to our ticket system! 🎉\n\n"
            "**How to open a ticket:**\n"
            "1. Select the category that best matches your request from the dropdown menu below.\n"
            "2. A private channel will be created where you can discuss your issue with our support team.\n"
            "3. Use the buttons in the ticket channel to manage your ticket (e.g., rename, close).\n\n"
            "**Available Categories:**\n"
            "• 🛠️ Support: For general assistance.\n"
            "• 🚨 Report: To report an issue or problem.\n"
            "• 🤝 Partner: For partnership inquiries.\n\n"
            "Thank you for using our support system! 🙏"
        ),
        color=discord.Color.blue(),
        thumbnail=interaction.guild.icon.url,
        image="https://example.com/banner.png",
        footer={"text": f"Requested by {interaction.user.name}", "icon_url": interaction.user.avatar.url}
    )
    view = TicketPanel()
    await interaction.response.send_message(embed=embed, view=view)

bot.run(TOKEN)
