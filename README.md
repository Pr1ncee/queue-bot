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

## Understanding Queue-bot architecture

Basically, this bot based on in-memory high performance `Redis` database. Since this database lightweight and dynamic
(in the context of creating data structures) the architecture of Queue-bot built upon `list` data structure.
Therefore, there are several lists created for a queue. For example, we have one queue called **Queue1** with **1111** id and one active chat **123**.
In the database all this info will be stored in 3 queues:

1. `REDIS_ACTIVE_CHATS_LIST` env variable stores all chats where the bot is running right now. It prevents from running the bot twice when the bot has been already running.
2. `REDIS_CHAT_SUPERVISOR_PREFIX` Used to support multi group handling...(**TODO**)
3. `REDIS_QUEUE_PREFIX` variable used to be as a prefix in queues to unique identify active queues.

So the format of a queue is: <queue prefix>:<queue name(based on the subject)>?<message id (it'll be used for deleting this queue when it's outdated)>


## Note

IIS stands for the Integrated Information System for BSUIR (Belarusian State University of Informatics and Radioelectronics).
