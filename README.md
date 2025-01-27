# TGNews2Meme

TGNews2Meme is an AI-powered application that parses news articles, generates jokes and images based on news titles, and sends them to a specified Telegram chat. The project integrates parsing, LLM-based joke generation, image creation, and Telegram bot automation.

## How It Works
1. **News Parsing**: The app parses news articles from specified sources.
2. **Title Check**: It checks the news title in the database (powered by Supabase) to see if it has already been processed.
3. **Joke Generation**: If the news is new, a joke about the title is generated using an LLM.
4. **Image Creation**: An image based on the joke is generated.
5. **Telegram Posting**: The generated text and image are sent to a Telegram chat.

## Prerequisites
This application requires the following:

- A Telegram bot and chat to send the messages.
- Hugging Face tokens for LLM and image generation.
- Supabase for managing the memory database to track processed news titles.

## Environment Variables
To run this application, you must supply the following environment variables:

| Variable                | Description                           |
|-------------------------|---------------------------------------|
| `BOT_TOKEN`            | Your Telegram bot token              |
| `CHAT_ID`              | The ID of the Telegram chat          |
| `HUGGINGFACE_LLM_TOKEN`| Your Hugging Face LLM token          |
| `HUGGINGFACE_IMAGE_TOKEN`| Your Hugging Face image token      |
| `SUPABASE_URL`         | The Supabase URL                     |
| `SUPABASE_KEY`         | The Supabase API key                 |

These variables can be supplied via:
- `-e` flags
- `--env-file`
- `docker-compose.env_file`

## Installation

### Option 1: Install Requirements
1. Clone the repository:
   ```bash
   git clone https://github.com/EduardMalinochka/TGNews2Meme.git
   cd TGNews2Meme
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate # For Linux/Mac
   venv\Scripts\activate   # For Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python app.py
   ```

### Option 2: Run with Docker
1. Build the Docker image:
   ```bash
   docker build -t tgnews2meme .
   ```
2. Run the container:
   ```bash
   docker run -e BOT_TOKEN=<your_bot_token> \
              -e CHAT_ID=<your_chat_id> \
              -e HUGGINGFACE_LLM_TOKEN=<your_huggingface_llm_token> \
              -e HUGGINGFACE_IMAGE_TOKEN=<your_huggingface_image_token> \
              -e SUPABASE_URL=<your_supabase_url> \
              -e SUPABASE_KEY=<your_supabase_key> \
              tgnews2meme
   ```

3. Alternatively, use a Docker Compose file:
   ```bash
   docker-compose up
   ```

## Features
- **News Deduplication**: Ensures no news is processed more than once.
- **LLM Integration**: Generates witty and relevant jokes for news titles.
- **Image Creation**: Visual content based on the generated joke.
- **Telegram Automation**: Seamless posting to Telegram chats.
