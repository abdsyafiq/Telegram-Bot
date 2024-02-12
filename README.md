# Telegram Bot for Expense Tracking

This repository contains Python code for creating a Telegram bot that can be used to input and calculate expenses. The expense data is stored in Google Sheets.

## Key Features

- **Input**: Enter the amount of expenses and their items.
- **Expenses**: View the total current expenses.
- **Remaining**: See the total remaining amount of money available for expenditure.
- **Clear Data**: Delete all previously entered data.

## Usage

1. Download or clone this repository into your Python environment.
2. Make sure you have a Telegram bot token and a JSON key file to access Google Sheets.
3. Replace the values of `TOKEN` and `BOT_USERNAME` inside the `main.py` file with the appropriate values.
4. Run the bot by executing the `main.py` file.
5. Start interacting with your Telegram bot to input and manage your expenses.

## Credits

- The Telegram bot is built using the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) framework.
- Interaction with Google Sheets is facilitated by the [gspread](https://github.com/burnash/gspread) library.
