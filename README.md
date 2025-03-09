# **🎟️ Ticket Bot Documentation 📄**

Welcome to the official documentation for the **Ticket Bot**! 🎉 This bot is designed to make managing support tickets on Discord easy, efficient, and aesthetically pleasing. Below, you'll find everything you need to set up, host, and maintain the bot. Let's dive in! 🚀

---

## **📚 Table of Contents**
1. [🌟 Features](#features)
2. [📋 Requirements](#requirements)
3. [🛠️ Installation](#installation)
4. [⚙️ Configuration](#configuration)
5. [🌐 Hosting Options](#hosting-options)
6. [🐍 Python Version Compatibility](#python-version-compatibility)
7. [📦 Dependencies](#dependencies)
8. [🚀 Usage](#usage)
9. [🔧 Troubleshooting](#troubleshooting)
10. [🤝 Contributing](#contributing)
11. [📜 License](#license)

---

## **🌟 Features**
- **🎫 Ticket Creation**: Users can open tickets by selecting a category from a dropdown menu.
- **🔄 Persistent Views**: Buttons and panels remain functional even after bot restarts.
- **📜 Transcripts**: Full conversation logs are saved and sent to a designated channel and the user.
- **✅ Claiming Tickets**: Staff members can claim tickets to take ownership.
- **✏️ Renaming Tickets**: Staff members can rename tickets for better organization.
- **🔒 Closing Tickets**: Tickets can be closed with an optional reason.
- **⏳ Inactivity Timeout**: Tickets are automatically closed after a period of inactivity.
- **🎨 Custom Embeds**: Beautiful and customizable embeds for all messages.

---

## **📋 Requirements**
To run the Ticket Bot, you need the following:
- **Python 3.8 or higher** 🐍.
- A **Discord bot token** from the [Discord Developer Portal](https://discord.com/developers/applications) 🔑.
- A **Discord server** where you have administrative permissions 🛡️.
- Basic knowledge of Python and Discord bot development 🧠.

---

## **🛠️ Installation**
Follow these steps to set up the Ticket Bot on your local machine or hosting service.

### **Step 1: Clone the Repository**
Clone the repository to your local machine or server:
```bash
git clone https://github.com/Nottinooo/Ticket-System.git
cd Ticket-System
```

### **Step 2: Install Dependencies**
Install the required Python packages using `pip`:
```bash
pip install discord.py
```

### **Step 3: Configure the Bot**
1. Open the `main.py` file.
2. Replace the following placeholders with your actual values:
   ```python
   TOKEN = "YOUR_DISCORD_BOT_TOKEN"
   GUILD_ID = 123456789012345678  # Replace with your server ID
   TRANSCRIPT_CHANNEL_ID = 123456789012345678  # Replace with your transcript channel ID
   CLAIM_ROLE_ID = 123456789012345678  # Replace with your claim role ID
   ```

### **Step 4: Run the Bot**
Start the bot using the following command:
```bash
python main.py
```

---

## **⚙️ Configuration**
The bot can be customized by modifying the following variables in the code:

### **Bot Settings**
| Variable               | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `TOKEN`                | Your Discord bot token.                                                     |
| `GUILD_ID`             | The ID of your Discord server.                                              |
| `TRANSCRIPT_CHANNEL_ID`| The ID of the channel where transcripts will be sent.                       |
| `CLAIM_ROLE_ID`        | The ID of the role allowed to claim tickets.                                |

### **Inactivity Timeout**
You can adjust the inactivity timeout (in hours) by modifying the `INACTIVE_TIMEOUT` variable:
```python
INACTIVE_TIMEOUT = 24  # Timeout in hours
```

### **Ticket Categories**
You can customize the ticket categories by modifying the `TICKET_CATEGORIES` dictionary:
```python
TICKET_CATEGORIES = {
    "🛠️ Support": 123456789012345678,  # Replace with your category ID
    "🚨 Report": 123456789012345678,   # Replace with your category ID
    "🤝 Partner": 123456789012345678   # Replace with your category ID
}
```

---

## **🌐 Hosting Options**
You can host the Ticket Bot on various platforms. Below are some recommended options:

### **1. Local Machine**
- **Pros**: Easy to set up and test.
- **Cons**: Requires your machine to be always on.

### **2. VPS (Virtual Private Server)**
- **Recommended Providers**: DigitalOcean, Linode, Vultr.
- **Pros**: Full control over the environment.
- **Cons**: Requires technical knowledge to set up.

### **3. Cloud Hosting**
- **Recommended Providers**: Heroku, Google Cloud, AWS.
- **Pros**: Scalable and reliable.
- **Cons**: Can be expensive for high traffic.

### **4. Dedicated Bot Hosting**
- **Recommended Providers**: [Pterodactyl](https://pterodactyl.io/), [DisCloud](https://discloudbot.com/).
- **Pros**: Optimized for bot hosting.
- **Cons**: Limited customization.
- *Ps*: If you want you can easly host your bot on my own [hosting](https://mp.romandev.it)

---

## **🐍 Python Version Compatibility**
The Ticket Bot is compatible with the following Python versions:

| Python Version | Supported |
|----------------|-----------|
| 3.8            | ✅         |
| 3.9            | ✅         |
| 3.10           | ✅         |
| 3.11           | ✅         |
| 3.12           | ✅         |

---

## **📦 Dependencies**
The bot relies on the following Python packages:

| Package         | Version | Description                          |
|-----------------|---------|--------------------------------------|
| `discord.py`    | 2.3.2   | The core library for interacting with Discord. |

You can install the dependencies using:
```bash
pip install discord.py
```

---

## **🚀 Usage**
Once the bot is running, you can use the following commands:

### **1. Create a Ticket Panel**
Use the `/ticketpanel` command to create a ticket panel in your server. Users can select a category to open a ticket.

### **2. Manage Tickets**
- **Claim a Ticket**: Click the `✅ Claim` button to take ownership of a ticket.
- **Rename a Ticket**: Click the `✏️ Rename` button to change the ticket's name.
- **Close a Ticket**: Click the `🔒 Close` button to close the ticket.

### **3. View Transcripts**
Transcripts are automatically sent to the designated transcript channel and the user who opened the ticket.

---

## **🔧 Troubleshooting**
### **1. Bot Not Responding**
- Ensure the bot has the necessary permissions in your server.
- Check if the bot is online and running.

### **2. Buttons Not Working After Restart**
- Ensure you have registered the views using `bot.add_view()`.
- Verify that all buttons have a unique `custom_id`.

### **3. Transcripts Not Sending**
- Check if the `TRANSCRIPT_CHANNEL_ID` is correct.
- Ensure the bot has permission to send messages in the transcript channel.

---

## **🤝 Contributing**
We welcome contributions to the Ticket Bot! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

---

## **📜 License**
The Ticket Bot is licensed under the **GPL 3.0**. See the [LICENSE](LICENSE) file for more details.

---

## **💬 Support**
For additional help, feel free to ask me, if you want on discord **flexin_roman** or instagram (same username)

---

Thank you for using the **Ticket Bot**! 🎉 We hope it makes managing your server's support system a breeze. 🚀

---
