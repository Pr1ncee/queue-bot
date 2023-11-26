# QueueBot

QueueBot is a Telegram bot for creating queues in group chats. It is written in Python and utilizes various technologies for smooth operation:

- Built with Python.
- Uses the pyTelegramBotAPI library for Telegram integration.
- Relies on Redis as a database.
- Utilizes Schedule module for making requests to the IIS API.
- Containerized using Docker.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Docker and Docker Compose installed.
- Telegram account to create and run a bot.
- Knowledge of the group name you want to use with the bot.

## Usage

To run the bot, follow these steps:

1. Clone the repository to your local machine:

   ```shell
   git clone https://github.com/yourusername/queuebot.git
   ```

2. Navigate to the project directory:
   ```shell
   cd queue-bot
   ```

3. Create `.env` file in the repo root directory according to the `.env.sample`.

4. Run the following command in your terminal:

    ```shell
    docker compose up --build
    ```
5. To run tests, use the following command:

    ```shell
    make test
    ```

6. To start the bot in your Telegram group:

   - Search for "QueueBot" in Telegram.
   - Add the bot to your group.
   - Type `/start 'group name'` to initialize the bot.
   - Enjoy! QueueBot will automatically fetch and update schedules from IIS and create queues for Practical & Laboratory Classes. It also manages and deletes outdated queues in the chat.

## Note

IIS stands for the Integrated Information System for BSUIR (Belarusian State University of Informatics and Radioelectronics).
