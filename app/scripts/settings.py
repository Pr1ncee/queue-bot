import dotenv


config = dotenv.dotenv_values('/home/andrey/PycharmProjects/pythonProject/bots/telegram_bots/queue_bot/app/.env')

TELEGRAM_BOT_TOKEN = config["TELEGRAM_BOT_TOKEN"]

DB_LINK = config['POSTGRES_LINK']
QUEUE_NAME = config['POSTGRES_QUEUE_NAME']

ROOT_USERNAME = config['root_username']
ROOT_PASS = config['root_pass']
COMMANDS = ['close']
