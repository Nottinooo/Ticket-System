# **🎟️ Ticket Bot Documentation 📄**

Welcome to the official documentation for the **Ticket Bot**! 🎉  
This bot is built to streamline your Discord server’s support system with structured ticket creation, automatic transcripts, multilingual support, and complete moderation features. Let’s dive in and make support efficient and beautiful! 🚀

## **📚 Table of Contents**
1. [🌟 Features](#features)  
2. [📋 Requirements](#requirements)  
3. [🛠️ Installation](#installation)  
4. [⚙️ Configuration](#configuration)  
5. [🗂️ Ticket Categories & Questions](#ticket-categories--questions)  
6. [🌐 Hosting Options](#hosting-options)  
7. [🐍 Python Compatibility](#python-compatibility)  
8. [📦 Dependencies](#dependencies)  
9. [🚀 Usage Guide](#usage-guide)  
10. [🛠️ Admin Tools & Commands](#admin-tools--commands)  
11. [🔧 Troubleshooting](#troubleshooting)  
12. [🤝 Contributing](#contributing)  
13. [📜 License](#license)  
14. [💬 Support](#support)

## **🌟 Features**

- 🎫 **Category-Based Tickets**: Users select from dropdown categories with custom questions.
- ✨ **Unique Ticket IDs**: Every ticket gets a unique 5-char ID (e.g. `B1A4C`), persistent across renames.
- 📜 **Transcript System**: Complete transcripts sent to both user & staff channels, with claim/rename info.
- ✅ **Claim System**: Staff can claim tickets, which updates the name and logs the claimer.
- ✏️ **Rename System**: Tickets can be renamed with slash command or modal, with cooldown and logging.
- 🔒 **Close System**: Tickets are closed with a modal reason, and full info is logged.
- 🌍 **Multi-language Support**: Users choose between 🇬🇧 English and 🇮🇹 Italian support.
- ⏳ **Auto-Close for Inactivity**: Tickets without messages for `INACTIVE_TIMEOUT` hours are auto-closed.
- 📂 **Role-based Access**: Only specific roles can view certain ticket types.
- 🔁 **Persistent Views**: Buttons and dropdowns stay registered even after bot restart.
- 🖼️ **Custom Embed Styling**: Logos, colors, and footers fully customizable.

## **📋 Requirements**
You’ll need:

- ✅ Python 3.8 or higher  
- ✅ A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)  
- ✅ Your server ID and channel/category IDs  
- ✅ Basic Python knowledge  
- ✅ Permissions to manage channels, messages, and roles

## **🛠️ Installation**

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/yourusername/ticket-bot.git
cd ticket-bot
```

### **Step 2: Install Python Dependencies**
```bash
pip install discord.py
```

### **Step 3: Configure the Bot**
In `main.py` or `ticket.py`, modify the following:
```python
TOKEN = "YOUR_BOT_TOKEN"
GUILD_ID = 1234567890
TRANSCRIPT_CHANNEL_ID = 1234567890
CLAIM_ROLE_ID = 1234567890
VOICE_CHANNEL_ID = 1234567890
NOTIFICATION_CHANNEL_ID = 1234567890
INACTIVE_TIMEOUT = 24
```

### **Step 4: Run the Bot**
```bash
python main.py
```

## **⚙️ Configuration**

### **Bot Environment Variables**
| Variable                   | Description                                                  |
|----------------------------|--------------------------------------------------------------|
| `TOKEN`                    | Your Discord bot token                                       |
| `GUILD_ID`                 | Discord server ID                                            |
| `TRANSCRIPT_CHANNEL_ID`    | Channel where transcripts are sent                           |
| `CLAIM_ROLE_ID`            | Staff role allowed to claim and rename tickets               |
| `INACTIVE_TIMEOUT`         | Hours before a ticket is closed automatically                |
| `VOICE_CHANNEL_ID`         | Voice channel ID used for support pings                      |
| `NOTIFICATION_CHANNEL_ID`  | Channel where the bot notifies staff of users in VC          |

## **🗂️ Ticket Categories & Questions**

You can configure ticket types and their forms using the `TICKET_CATEGORIES` dictionary:

```python
TICKET_CATEGORIES = {
    "🎫 Category 1": {
        "id": 1234567890,
        "roles": [USER_ROLE_ID],
        "color": discord.Color.green(),
        "emoji": "🎫",
        "questions": [
            "Answer 1",
            "Answer 2",
            "Answer 3",
            "Answer 4",
            "Answer 5"
        ]
    },
    "📢 Category 2": { ... },
    "🔐 Category 3": { ... }
}
```

Each category:
- Can have **up to 10 questions**
- Displays **5 at a time** in modals
- Defines which roles can open tickets in that category

## **🌐 Hosting Options**

| Platform             | Pros                                | Cons                                |
|----------------------|--------------------------------------|-------------------------------------|
| **Local Machine**    | Easy to test, quick to start         | Must stay online                    |
| **VPS**              | Full control, scalable               | Requires setup & sysadmin skills    |
| **Cloud Services**   | (Heroku, GCP, AWS)                   | Managed hosting                     | Might be costly                     |
| **Pterodactyl**      | [Free panel hosting](https://pterodactyl.io) | Bot-oriented environment            | Limited UI                          |
| **DisCloud**         | Quick bot deployment                 | Less customization                  |

> 🔧 Need hosting? Try [nothosting.it](https://www.nothosting.it) 💙

## **🐍 Python Compatibility**

| Version   | Status |
|-----------|--------|
| 3.8       | ✅     |
| 3.9       | ✅     |
| 3.10      | ✅     |
| 3.11      | ✅     |
| 3.12      | ✅     |

## **📦 Dependencies**

| Package       | Version | Description                      |
|---------------|---------|----------------------------------|
| `discord.py`  | 2.3.2   | Python wrapper for Discord API   |

Install with:
```bash
pip install discord.py
```

## **🚀 Usage Guide**

### 🎫 `/ticketpanel`
Creates a dropdown ticket panel. Users select a category, fill out a modal form, choose language, and the bot creates a private ticket channel.

### ✅ Claim Button
Staff can claim a ticket. It renames the channel and logs the claimer with timestamp.

### ✏️ Rename
Staff can:
- Click Rename button
- Or use `/rename-ticket <new_name>`  
Includes 60-second cooldown and logging.

### 🔒 Close
Click "Close" and fill a modal with the reason. The bot:
- Sends a transcript to the user and staff
- Deletes the channel
- Logs claimers, renames, category, duration

### 🕐 Inactivity Auto-Close
Tickets with no new messages for `INACTIVE_TIMEOUT` hours are closed automatically and logged.

## **🛠️ Admin Tools & Commands**

| Command             | Description                                 |
|---------------------|---------------------------------------------|
| `/ticketpanel`      | Creates ticket selection panel              |
| `/rename-ticket`    | Renames a ticket channel (Staff only)       |
| `!help`             | Displays help/status message (customizable) |

## **🔧 Troubleshooting**

| Issue                                | Fix                                                         |
|--------------------------------------|--------------------------------------------------------------|
| Buttons don't work after restart     | Ensure `bot.add_view()` is used in `on_ready()`             |
| Transcripts not received             | Check `TRANSCRIPT_CHANNEL_ID` and permissions               |
| Tickets not closing                  | Make sure close modal returns a message                     |
| Duplicate IDs                        | Delete `ticket_log.json` to regenerate the ID pool          |
| Panel doesn’t show up                | Check if your slash commands are synced                     |

## **🤝 Contributing**

We 💙 contributions!

1. Fork the repo  
2. Make your changes  
3. Submit a Pull Request with a detailed explanation

## **📜 License**

Licensed under the **GNU General Public License v3.0 (GPL-3.0)**  
See the `LICENSE` file for full legal terms.

## **💬 Support**

Need help or want to suggest something?

- 💬 Discord: `flexin_roman`  
- 📸 Instagram: [@flexin_roman](https://instagram.com/flexin_roman)

Thanks for using the **Ticket Bot** — built for support teams that care.  
From creation to closure, every step is handled beautifully. 🎟️
