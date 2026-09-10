# 🐍 Cobra Chatbot

An advanced, intelligent Telegram AI Chatbot built with Pyrofork, Python 3, and MongoDB. Cobra Chatbot learns conversational patterns directly from your group chats and replies naturally using text and stickers!

<p align="center">
  <img src="https://graph.org/file/a0d949ae033c97bb60c0b-238eeecbc9c32d092f.mp4" width="350" alt="Cobra Chatbot">
</p>

## ✨ Features

- 🧠 **Dynamic Auto-Learning**: Automatically learns responses and stickers from group interactions.
- 💬 **Text & Sticker Support**: Can reply with both text messages and animated/static stickers.
- 👥 **Group Admin Controls**: Enable or disable the chatbot per-group using `/chatbot on` and `/chatbot off`.
- ⚡ **Optimized MongoDB Connection Pooling**: Ultra-fast responses with persistent connection pooling (no connection leaks).
- 🎬 **Video/Animation Thumbnail**: Supports animated MP4 video thumbnails natively.
- ⚙️ **Configurable**: Easily configure via `.env` file or environment variables.

## 🚀 Commands

| Command | Description |
| :--- | :--- |
| `/start` | Start the bot and view the welcome menu |
| `/help` | View help guide and available features |
| `/chatbot on` | Enable Cobra Chatbot in the current group (Admins only) |
| `/chatbot off` | Disable Cobra Chatbot in the current group (Admins only) |
| `/chatbot` | Check chatbot status and usage guide |
| `/ping` | Check bot latency and responsiveness |

## 🛠️ Local Setup

1. **Clone repository**:
   ```bash
   git clone https://github.com/your-repo/Cobra_chatbot.git
   cd Cobra_chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your values:
   ```env
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   MONGO_URL=your_mongodb_connection_string
   ```

4. **Run the bot**:
   ```bash
   python main.py
   ```

## 📜 License
Released under the GNU General Public License v3.0.
