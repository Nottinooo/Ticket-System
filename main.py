import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput, Item
from datetime import datetime, UTC
import io
import logging
import re
import asyncio
import os
import json
import time
import string
import random
from discord.errors import HTTPException, NotFound, Forbidden, DiscordServerError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("discord")

TOKEN = "BOT_TOKEN"
GUILD_ID = 1234567890
TRANSCRIPT_CHANNEL_ID = 1234567890
CLAIM_ROLE_ID = 1234567890
UNVERIFIED_ROLE_ID = 1234567890
USER_ROLE_ID = 1234567890
PRE_STAFF_ROLE_ID = 1234567890
INACTIVE_TIMEOUT = 24  # Ore
VOICE_CHANNEL_ID = 1234567890
NOTIFICATION_CHANNEL_ID = 1234567890

TICKET_LOG_FILE = "ticket_log.json"

def load_ticket_log():
    try:
        if not os.path.exists(TICKET_LOG_FILE):
            return []
        with open(TICKET_LOG_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            return json.loads(data) if data else []
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading ticket log: {e}")
        if os.path.exists(TICKET_LOG_FILE):
            backup_file = f"{TICKET_LOG_FILE}.backup.{int(time.time())}"
            os.rename(TICKET_LOG_FILE, backup_file)
        return []

def save_ticket_log(logs):
    try:
        temp_file = f"{TICKET_LOG_FILE}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4, default=str)
        os.replace(temp_file, TICKET_LOG_FILE)
    except Exception as e:
        logger.error(f"Error saving ticket log: {e}")

def append_ticket_log(entry):
    try:
        logs = load_ticket_log()
        logs = [log for log in logs if log.get("channel_name") != entry.get("channel_name")]
        sanitized_entry = {k: v for k, v in entry.items() if not callable(v)}
        logs.append(sanitized_entry)
        save_ticket_log(logs)
    except Exception as e:
        logger.error(f"Error appending to ticket log: {e}")

def get_next_ticket_number(category_key):
    """Get the next available ticket number for a category"""
    try:
        logs = load_ticket_log()
        prefix = category_key.split()[1].lower() + "-"
        numbers = []
        
        for log in logs:
            channel_name = log.get("channel_name", "")
            if channel_name.startswith(prefix):
                try:
                    num = int(channel_name.split("-")[-1])
                    numbers.append(num)
                except (ValueError, IndexError):
                    continue
                    
        return max(numbers, default=0) + 1
    except Exception as e:
        logger.error(f"Error getting next ticket number: {e}")
        return int(time.time()) % 10000 

def generate_unique_ticket_id():
    """Generate a unique 5-character ticket ID"""
    used_ids = set()
    try:
        logs = load_ticket_log()
        for log in logs:
            if "unique_id" in log:
                used_ids.add(log["unique_id"])
    except Exception:
        pass
    
    while True:
        new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if new_id not in used_ids:
            return new_id

async def send_transcript_to_user(user: discord.Member, transcript_content: str, channel_name: str, ticket_info=None, staff_embed=None):
    """Send transcript to user via DM"""
    try:
        embed = discord.Embed(
            title="📜 Your Ticket Transcript",
            description=(
                "📄 Here is the transcript of your ticket. Below you will find all the details about the ticket, "
                "including who closed it and how long it was active.\n\n"
                "📋 Ticket Details:\n"
                f"• 🔒 **Closed By:** {staff_embed.description.split('Closed By:**')[1].split('\n')[0] if staff_embed else 'Unknown'}\n"
                f"• ⏰ **Closed At:** {ticket_info.get('closed_at', 'Unknown')}\n"
                f"• ⏳ **Duration:** {ticket_info.get('duration', 'Unknown')}\n"
                f"• 📂 **Category:** {ticket_info.get('category', 'Unknown')}\n"
                f"• 🌍 **Language:** {'English 🇬🇧' if ticket_info.get('language') == 'en' else 'Italian 🇮🇹'}\n"
                f"• 🎫 **Ticket ID:** {ticket_info.get('unique_id', 'Unknown')}\n\n"
                "🙏 Thank you!"
            ),
            color=discord.Color.blue()
        )
        file = discord.File(
            io.StringIO(transcript_content),
            filename=f"{channel_name}_transcript.txt"
        )
        await user.send(embed=embed, file=file)
    except Exception as e:
        logger.error(f"Failed to send transcript to user: {e}")

TICKET_CATEGORIES = {
    "Cattegory 1": {
        "id": 1234567890,
        "roles": [USER_ROLE_ID],
        "color": discord.Color.green(),
        "emoji": "{EMOJI}",
        "questions": [
            "Question 1",
            "Question 2",
            "Question 3",
            "Question 4",
            "Question 5",
            "Question 6",
            "Question 7"
        ]
    },
    "CATTEGORY 2": {
        "id": 1234567890,
        "roles": [USER_ROLE_ID],
        "color": discord.Color.red(),
        "emoji": "EMOJI",
        "questions": [
            "Question 1",
            "Question 2",
            "Question 3",
            "Question 4",
            "Question 5",
            "Question 6",
            "Question 7"
        ]
    },
    "CATTEGORY 3": {
        "id": 1234567890,
        "roles": [UNVERIFIED_ROLE_ID],
        "color": discord.Color.orange(),
        "emoji": "EMOJI",
        "questions": [
            "Question 1",
            "Question 2",
            "Question 3",
            "Question 4",
            "Question 5",
            "Question 6",
            "Question 7"
        ]
    },
    "CATTEGORY 4": {
        "id": 1234567890,
        "roles": [PRE_STAFF_ROLE_ID],
        "color": discord.Color.blurple(),
        "emoji": "EMOJI",
        "questions": [
            "Question 1",
            "Question 2",
            "Question 3",
            "Question 4",
            "Question 5",
            "Question 6",
            "Question 7"
        ]
    },
    "CATTEGORY 5": {
        "id": 1234567890,
        "roles": [USER_ROLE_ID],
        "color": discord.Color.blue(),
        "emoji": "EMOJI",
        "questions": [
            "Question 1",
            "Question 2",
            "Question 3",
            "Question 4",
            "Question 5",
            "Question 6",
            "Question 7"
        ]
    }
}

SUPPORT_ROLES = {
    "en": 1234567890,
    "it": 1234567890
}

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
ticket_counters = {category: 0 for category in TICKET_CATEGORIES}
ticket_data = {}
notified_users = set()

claim_cooldowns = {}
rename_cooldowns = {}
ticket_claimers = {}
ticket_renames = {}

class SupportTicketModal(Modal, title="FORM 1"):
    issue = TextInput(
        label="Question 1",
        style=discord.TextStyle.long,
        placeholder="ABCD",
        required=True
    )
    
    contact = TextInput(
        label="Question 2",
        placeholder="ABCD",
        required=False
    )
    
    urgency = TextInput(
        label="Question 3",
        placeholder="ABCD",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        additional_info = f"**Issue:** {self.issue.value}\n**Contact Method:** {self.contact.value}\n**Urgency:** {self.urgency.value}"
        await interaction.response.defer(ephemeral=True)
        await ask_for_language(interaction, "CATTEGORY", additional_info)

class StaffApplicationModal(Modal, title="FORM 2"):
    age = TextInput(
        label="Question 1",
        placeholder="ABCD",
        required=True
    )
    
    timezone = TextInput(
        label="Question 2",
        placeholder="ABCD",
        required=True
    )
    
    experience = TextInput(
        label="Question 3",
        style=discord.TextStyle.long,
        placeholder="ABCD",
        required=True
    )
    
    motivation = TextInput(
        label="Question 4",
        style=discord.TextStyle.long,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        additional_info = f"**Age:** {self.age.value}\n**Timezone:** {self.timezone.value}\n**Experience:** {self.experience.value}\n**Motivation:** {self.motivation.value}"
        await interaction.response.defer(ephemeral=True)
        await create_ticket_channel(interaction, "CATTEGORY", additional_info)

class TicketRenameModal(Modal, title="✏️ Rename Ticket"):
    new_name = TextInput(
        label="New ticket name",
        placeholder="support-123",
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        if CLAIM_ROLE_ID not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("🚫 You don't have permission to rename this ticket.", ephemeral=True)
        old_name = interaction.channel.name
        try:
            await interaction.channel.edit(name=self.new_name.value)
            channel_id = interaction.channel.id
            if channel_id not in ticket_renames:
                ticket_renames[channel_id] = []
            ticket_renames[channel_id].append(
                (old_name, self.new_name.value, interaction.user.id, datetime.now(UTC))
            )
            await interaction.response.send_message(
                f"✏️ Ticket renamed to **{self.new_name.value}**.\n"
                f"To rename again you must wait 1 minute.", ephemeral=False
            )
        except HTTPException as e:
            if e.status == 429:
                await interaction.response.send_message(
                    "⏳ Rate limited by Discord. Please wait a moment before renaming again.", ephemeral=True
                )
            else:
                logger.error(f"Error renaming channel: {e}")
                await interaction.response.send_message(
                    "❌ Unable to rename the ticket due to an error.", ephemeral=True
                )
        except Exception as e:
            logger.error(f"Unexpected error renaming channel: {e}")
            await interaction.response.send_message(
                "❌ Unexpected error occurred while renaming.", ephemeral=True
            )

class CloseTicketModal(Modal, title="🔒 Close Ticket"):
    reason = TextInput(
        label="Reason for closing",
        placeholder="Describe why this ticket is being closed.",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🔒 Closing ticket for reason: **{self.reason.value}**...", ephemeral=False)
        try:
            await save_transcript(interaction.channel, interaction.user)
            await interaction.channel.delete()
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            await interaction.followup.send("❌ An error occurred while closing the ticket. Please try again.", ephemeral=True)

class CategoryQuestionsModal(Modal):
    def __init__(self, category: str, questions: list):
        self.category = category
        super().__init__(title=f"📝 {category} Questions")
        
        for i, question in enumerate(questions[:5]): 
            self.add_item(TextInput(
                label=question[:45],  
                placeholder="Type your answer here...",
                style=discord.TextStyle.paragraph,
                required=True,
                custom_id=f"question_{i+1}"
            ))

    async def on_submit(self, interaction: discord.Interaction):
        responses = []
        questions = TICKET_CATEGORIES[self.category]["questions"][:5]
        
        for i, child in enumerate(self.children):
            responses.append(f"**{questions[i]}**\n{child.value}")
        
        additional_info = "\n\n".join(responses)
        await interaction.response.defer(ephemeral=True)
        await ask_for_language(interaction, self.category, additional_info)

class TicketControls(View):
    def __init__(self, ticket_owner: discord.Member):
        super().__init__(timeout=None)
        self.ticket_owner = ticket_owner
        self.message = None
        self._refresh_cooldown = {}

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
        if any(role.id == CLAIM_ROLE_ID for role in interaction.user.roles) or interaction.user == self.ticket_owner:
            return True
        await interaction.response.send_message("You don't have permission to use these controls.", ephemeral=True)
        return False

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: Item) -> None:
        logger.error(f"Error in button {item.custom_id if hasattr(item, 'custom_id') else 'unknown'}: {error}")
        try:
            await interaction.response.send_message("An error occurred. Please try again.", ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.followup.send("An error occurred. Please try again.", ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    @discord.ui.button(label="✅ Claim", style=discord.ButtonStyle.success, custom_id="ticket_claim_button")
    async def claim_button(self, interaction: discord.Interaction, button: Button):
        channel_id = interaction.channel.id
        now = time.time()
        if channel_id in self._refresh_cooldown:
            remaining = self._refresh_cooldown[channel_id] - now
            if remaining > 0:
                await interaction.response.send_message(
                    f"Please wait {int(remaining)} seconds before claiming again.",
                    ephemeral=True
                )
                return

        try:
            await interaction.response.defer()
            new_name = f"{interaction.channel.name}-claimed"
            await interaction.channel.edit(name=new_name)
            
            ticket_data[channel_id] = ticket_data.get(channel_id, {})
            ticket_data[channel_id]["claimed_by"] = interaction.user.id
            
            if channel_id not in ticket_claimers:
                ticket_claimers[channel_id] = []
            ticket_claimers[channel_id].append((interaction.user.id, datetime.now(UTC)))
            
            self._refresh_cooldown[channel_id] = now + 60
            
            await interaction.followup.send(
                f"🎫 Ticket claimed by {interaction.user.mention}",
                ephemeral=False
            )
            button.disabled = True
            if self.message:
                await self.message.edit(view=self)
                
        except Exception as e:
            logger.error(f"Error in claim button: {e}")
            await interaction.followup.send("Failed to claim ticket. Please try again.", ephemeral=True)

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.danger, custom_id="ticket_close_button")
    async def close_button(self, interaction: discord.Interaction, button: Button):
        try:
            await interaction.response.send_modal(CloseTicketModal())
        except Exception as e:
            logger.error(f"Error sending close modal: {e}")
            await self.on_error(interaction, e, button)

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
        user = interaction.user
        
        if category_name == "✅ Verification" and UNVERIFIED_ROLE_ID not in [role.id for role in user.roles]:
            return await interaction.response.send_message(
                f"🚫 Hey {user.mention} you don't have the UnVerified role to open this type of ticket.",
                ephemeral=True
            )

        try:
            if category_name == "📋 Staff Application":
                modal = StaffApplicationModal()
            else:
                questions = TICKET_CATEGORIES[category_name]["questions"][:5]
                modal = CategoryQuestionsModal(category_name, questions)
            
            await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"Error sending modal: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while creating the form. Please try again.",
                ephemeral=True
            )

async def ask_for_language(interaction: discord.Interaction, category: str, additional_info: str):
    embed = discord.Embed(
        title="🌍 Select Support Language",
        description="Please choose your preferred support language:",
        color=discord.Color.blue()
    )
    
    class LanguageSelect(View):
        def __init__(self):
            super().__init__(timeout=180)
        @discord.ui.select(
            placeholder="Choose language...",
            options=[
                discord.SelectOption(label="English", value="en", emoji="🇬🇧"),
                discord.SelectOption(label="Italian", value="it", emoji="🇮🇹")
            ]
        )
        async def select_callback(self, select_interaction: discord.Interaction, select: Select):
            if select_interaction.user.id != interaction.user.id:
                return await select_interaction.response.send_message("You can't select a language for this ticket.", ephemeral=True)
            lang = select.values[0]
            await select_interaction.response.defer()
            await create_ticket_channel(interaction, category, additional_info, lang)
            await select_interaction.followup.send(f"✅ Selected {lang.upper()} - Ticket created!", ephemeral=True)
            self.stop()
    view = LanguageSelect()
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

async def create_ticket_channel(interaction, category, additional_info, lang="en"):
    try:
        config = TICKET_CATEGORIES[category]
        guild = interaction.guild

        ticket_number = get_next_ticket_number(category)
        channel_name = f"{category.split()[1].lower()}-{ticket_number}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        staff_role = guild.get_role(CLAIM_ROLE_ID)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        if lang in SUPPORT_ROLES:
            lang_role = guild.get_role(SUPPORT_ROLES[lang])
            if lang_role:
                overwrites[lang_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        category_channel = discord.utils.get(guild.categories, id=config["id"])
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category_channel,
            overwrites=overwrites
        )

        unique_id = generate_unique_ticket_id()

        ticket_data[ticket_channel.id] = {
            "user_id": interaction.user.id,
            "claimed_by": None,
            "language": lang,
            "additional_info": additional_info,
            "category": category,
            "unique_id": unique_id
        }

        if category in ["📋 Staff Application"]:
            staff_role = guild.get_role(CLAIM_ROLE_ID)
            pre_staff_role = guild.get_role(PRE_STAFF_ROLE_ID)
            mention_str = f"{staff_role.mention} {pre_staff_role.mention}"
        else:
            staff_role = guild.get_role(CLAIM_ROLE_ID)
            lang_role = guild.get_role(SUPPORT_ROLES[lang]) if lang in SUPPORT_ROLES else None
            mention_str = f"{staff_role.mention} {lang_role.mention if lang_role else ''}"

        questions_formatted = "\n".join(f"• **{i+1}.** {q}" for i, q in enumerate(config["questions"]))
        
        embed = discord.Embed(
            title=f"🎟️ {category} Ticket Opened",
            description=(
                f"👋 Hello {interaction.user.mention}, thank you for reaching out to **SERVER NAME**! A {category} ticket has been opened for you.\n\n"
                "**📝 Please answer these questions:**\n"
                f"{questions_formatted}\n\n"
                "**📝 What happens next?**\n"
                "1. A member of our support team will be with you shortly. ⏳\n"
                "2. Please provide as much detail as possible about your issue or request. 📄\n"
                "3. Use the buttons below to manage your ticket (e.g., rename, close). 🔧\n\n"
                f"**🌍 Language Selected:** {'English 🇬🇧' if lang == 'en' else 'Italian 🇮🇹'}\n\n"
                "**📜 Guidelines:**\n"
                "• Be respectful and patient. 🙏\n"
                "• Do not share personal or sensitive information. 🔒\n"
                "• Use the `🔒 Close` button to close the ticket once your issue is resolved. ✅"
            ),
            color=config["color"],
            timestamp=datetime.now(UTC)
        )
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_image(url="htts://example.com/image.png")
        embed.set_footer(text=f"🎟️ Opened by {interaction.user.name}", icon_url=interaction.user.avatar.url)

        # Add ticket ID to embed
        embed.add_field(
            name="🎫 Ticket Information",
            value=(
                f"• **Ticket ID:** `{unique_id}`\n"
                f"• **Channel:** {ticket_channel.mention}\n"
                f"• **Number:** #{ticket_number}\n"
                "• Use `/rename-ticket` to rename this ticket (Staff only)"
            ),
            inline=False
        )

        if additional_info:
            embed.add_field(name="📝 Additional Information Provided", value=additional_info, inline=False)

        view = TicketControls(interaction.user)
        await ticket_channel.send(
            f"{mention_str} {interaction.user.mention}",
            embed=embed,
            view=view
        )
        log_entry = {
            "channel_name": channel_name,
            "category": category,
            "opened_by": interaction.user.id,
            "claimed_by": None,
            "renames": [],
            "opened_at": datetime.now(UTC).isoformat(),
            "closed_at": None,
            "duration": None,
            "language": lang,
            "staff_messages": 0,
            "claimers": [],
            "closer": None,
            "unique_id": unique_id
        }
        append_ticket_log(log_entry)

        try:
            await interaction.followup.send(
                content=f"🎟️ {category} ticket created successfully: {ticket_channel.mention}",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error sending ticket confirmation: {e}")
            try:
                await interaction.user.send(f"🎟️ Your {category} ticket was created: {ticket_channel.mention}")
            except Exception as e:
                logger.error(f"Failed to DM user about ticket: {e}")

    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        try:
            await interaction.followup.send(
                "❌ An error occurred while creating the ticket. Please try again.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
            try:
                await interaction.user.send("❌ An error occurred while creating your ticket. Please try again.")
            except Exception as e:
                logger.error(f"Failed to DM user about error: {e}")

async def save_transcript(channel, closer):
    try:
        transcript_content = await generate_transcript(channel)
        transcript_channel = bot.get_channel(TRANSCRIPT_CHANNEL_ID)
        if not transcript_channel:
            logger.error("Transcript channel not found")
            return
        staff_messages = 0
        async for message in channel.history(limit=None):
            if hasattr(message.author, "roles") and any(role.id == CLAIM_ROLE_ID for role in getattr(message.author, "roles", [])):
                staff_messages += 1

        opened_at = channel.created_at.replace(tzinfo=UTC)
        closed_at = datetime.now(UTC)
        duration = closed_at - opened_at

        ticket_info = ticket_data.get(channel.id, {})
        opener_id = ticket_info.get("user_id")
        opener = bot.get_user(opener_id)
        opener_tag = opener.mention if opener else "Unknown"

        claimed_by = ticket_info.get("claimed_by")
        claimed_by_user = bot.get_user(claimed_by) if claimed_by else None
        claimed_by_tag = claimed_by_user.mention if claimed_by_user else "Not Claimed"

        language = ticket_info.get("language", "en")
        language_display = "English 🇬🇧" if language == "en" else "Italian 🇮🇹"

        claimers_info = ""
        if channel.id in ticket_claimers and ticket_claimers[channel.id]:
            claimers_info = "\n".join(
                f"- <@{uid}> at {dt.strftime('%Y-%m-%d %H:%M:%S')}" for uid, dt in ticket_claimers[channel.id]
            )
        else:
            claimers_info = "No staff claimed this ticket."

        renames_info = ""
        if channel.id in ticket_renames and ticket_renames[channel.id]:
            renames_info = "\n".join(
                f"- `{old}` ➔ `{new}` by <@{uid}> at {dt.strftime('%Y-%m-%d %H:%M:%S')}"
                for old, new, uid, dt in ticket_renames[channel.id]
            )
        else:
            renames_info = "No renames performed."

        staff_embed = discord.Embed(
            title="📜 **Ticket Transcript**",
            description=(
                "📄 Here is the complete transcript of the ticket. Below you will find all the details about the ticket, "
                "including who opened it, who closed it, and how long it was active.\n\n"
                "**📋 Ticket Details:**\n"
                f"• **👤 Opened By:** {opener_tag}\n"
                f"• **🛠️ Claimed By:** {claimed_by_tag}\n"
                f"• **🔒 Closed By:** {closer.mention}\n"
                f"• **📅 Opened At:** {opened_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"• **⏰ Closed At:** {closed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"• **⌛ Duration:** {str(duration).split('.')[0]}\n"
                f"• **🌐 Language:** {language_display}\n"
                f"• **👥 Staff Messages:** {staff_messages}\n"
                f"• **📝 Claimers:**\n{claimers_info}\n"
                f"• **✏️ Renames:**\n{renames_info}\n"
            ),
            color=discord.Color.blurple(),
            timestamp=closed_at
        )
        staff_embed.set_footer(text="Ticket System")
        staff_embed.add_field(name="Transcript", value="See attached file.", inline=False)

        transcript_file = discord.File(io.StringIO(transcript_content), filename=f"{channel.name}_transcript.txt")
        await transcript_channel.send(embed=staff_embed, file=transcript_file)
        if opener:
            await send_transcript_to_user(opener, transcript_content, channel.name, ticket_info, staff_embed)

        def convert(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, list):
                return [convert(i) for i in obj]
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            return obj
        log_entry = {
            "channel_name": channel.name,
            "category": ticket_info.get("category", "Unknown"),
            "opened_by": opener_id,
            "claimed_by": claimed_by,
            "renames": convert(ticket_renames.get(channel.id, [])),
            "opened_at": opened_at.isoformat(),
            "closed_at": closed_at.isoformat(),
            "duration": str(duration).split('.')[0],
            "language": language,
            "staff_messages": staff_messages,
            "claimers": convert(ticket_claimers.get(channel.id, [])),
            "closer": getattr(closer, "id", str(closer)),
            "unique_id": ticket_info.get("unique_id", "Unknown")
        }
        append_ticket_log(log_entry)
    except Exception as e:
        logger.error(f"Error creating ticket transcript: {e}")

async def generate_transcript(channel):
    try:
        transcript = []
        async for message in channel.history(limit=None, oldest_first=True):
            timestamp = message.created_at.strftime("[%Y-%m-%d %H:%M:%S]")
            content = message.content or "[No text content]"
            transcript.append(f"{timestamp} {message.author.name}: {content}")
        return "\n".join(transcript)
    except Exception as e:
        logger.error(f"Error generating transcript: {e}")
        return "Error generating transcript"

@tasks.loop(hours=1)
async def check_inactive_tickets():
    guild = bot.get_guild(GUILD_ID)
    for channel in guild.text_channels:
        if channel.category and channel.category.name in [c.split(' ', 1)[1] for c in TICKET_CATEGORIES]:
            last_message = await channel.history(limit=1).flatten()
            if last_message:
                last_message_time = last_message[0].created_at
                if (datetime.now(UTC) - last_message_time).total_seconds() > INACTIVE_TIMEOUT * 3600:
                    await channel.send("🔒 This ticket is being closed due to inactivity.")
                    try:
                        await save_transcript(channel, bot.user)
                        await channel.delete()
                    except Exception as e:
                        logger.error(f"Error closing inactive ticket: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id == VOICE_CHANNEL_ID:
        if member.id not in notified_users:
            notification_channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
            if notification_channel:
                await notification_channel.send(f"🔔 ||<@&{CLAIM_ROLE_ID}>|| **{member.mention}**, the user **{member.name}** has entered the assistance voice channel. Support them! 🛠️")
                notified_users.add(member.id)
    elif before.channel and before.channel.id == VOICE_CHANNEL_ID:
        if member.id in notified_users:
            notified_users.remove(member.id)

@bot.event
async def on_ready():
    try:
        logger.info(f"{bot.user} is online! 🎉")
        
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="tickets | !help",
            state="Managing Support Tickets",
            details="Ready to help!"
        )
        await bot.change_presence(
            status=discord.Status.dnd,
            activity=activity
        )
        
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} commands")
        
        check_inactive_tickets.start()
        
        guild = bot.get_guild(GUILD_ID)
        if guild:
            for channel in guild.text_channels:
                if channel.category and channel.category.id in [c["id"] for c in TICKET_CATEGORIES.values()]:
                    view = TicketControls(None)
                    async for message in channel.history(limit=50):
                        if message.author == bot.user and message.components:
                            view.message = message
                            bot.add_view(view)
                            break
        
        logger.info("Ticket system initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error in on_ready: {e}")

@bot.tree.command(name="ticketpanel", description="🆘 Create a ticket panel for support!")
@app_commands.default_permissions(manage_guild=True)
async def ticketpanel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 **Ticket System**",
        description=(
            "🌟 Welcome to **SERVER NAME**'s ticket system! 🎉\n\n"
            "**📝 How to open a ticket:**\n"
            "1. Select the category that best matches your request from the dropdown menu below. 🖱️\n"
            "2. Fill out the form with all required information. 📝\n"
            "3. Choose your preferred support language (English or Italian). 🌍\n"
            "4. A private channel will be created where you can discuss your issue with our support team. 🛠️\n"
            "5. Use the buttons in the ticket channel to manage your ticket (e.g., rename, close). 🔧\n\n"
            "**📂 Available Categories:**\n"
            "1\n"
            "2"
            "3\n"
            "4\n"
            "5\n\n"
            "🙏 Thank you for using **SERVER NAME**'s support system! If you have any questions, feel free to reach out. 🚀"
        ),
        color=discord.Color.blue(),
        timestamp=datetime.now(UTC)
    )
    embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_image(url="https://example.com/image.png")
    
    view = TicketPanel()
    view.timeout = None
    
    message = await interaction.response.send_message(embed=embed, view=view)
    try:
        stored_message = await interaction.original_response()
        view.message = stored_message
    except:
        pass

@bot.tree.command(name="support", description="ℹ️ Get support information")
async def support(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Support Information",
        description="Here's how to get help from our team:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🛠️ Technical Support",
        value="For server issues and technical problems",
        inline=False
    )
    embed.add_field(
        name="🚨 Reporting Users",
        value="To report rule violations or abuse",
        inline=False
    )
    embed.add_field(
        name="⏳ Response Times",
        value="We aim to respond to all tickets within 24 hours",
        inline=False
    )
    embed.add_field(
        name="🌍 Languages",
        value="We support English and Italian assistance",
        inline=False
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="rename-ticket", description="🔄 Rename current ticket")
@app_commands.describe(new_name="New name for the ticket")
async def rename_ticket(interaction: discord.Interaction, new_name: str):
    if not interaction.channel.category or interaction.channel.category.id not in [c["id"] for c in TICKET_CATEGORIES.values()]:
        return await interaction.response.send_message("❌ This command can only be used in ticket channels!", ephemeral=True)
    if CLAIM_ROLE_ID not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("🚫 Only staff members can rename tickets!", ephemeral=True)
    
    channel_id = interaction.channel.id
    now = time.time()
    if channel_id in rename_cooldowns:
        remaining = rename_cooldowns[channel_id] - now
        if remaining > 0:
            return await interaction.response.send_message(
                f"⏳ Please wait {int(remaining)} seconds before renaming again.",
                ephemeral=True
            )
    
    old_name = interaction.channel.name
    ticket_info = ticket_data.get(channel_id, {})
    unique_id = ticket_info.get("unique_id", generate_unique_ticket_id())
    
    try:
        ticket_number = old_name.split("-")[-1]
        if not ticket_number.isdigit():
            ticket_number = get_next_ticket_number(ticket_info.get("category", "support"))
        new_base_name = f"{new_name}-{ticket_number}"
        
        await interaction.channel.edit(name=new_base_name)
        rename_cooldowns[channel_id] = now + 60
        
        if channel_id not in ticket_renames:
            ticket_renames[channel_id] = []
        ticket_renames[channel_id].append(
            (old_name, new_base_name, interaction.user.id, datetime.now(UTC))
        )
        
        await interaction.response.send_message(
            f"✅ Ticket renamed from `{old_name}` to `{new_base_name}`\n"
            f"🎫 Ticket ID: `{unique_id}`\n"
            f"*You can use `/rename-ticket` again in 60 seconds*"
        )
    except Exception as e:
        logger.error(f"Error renaming ticket: {e}")
        await interaction.response.send_message("❌ Failed to rename ticket.", ephemeral=True)

bot.run(TOKEN)
