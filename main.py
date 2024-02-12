import pandas as pd
import re
import json

from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


with open("telegram_key.json", "r") as file:
    key_data = json.load(file)

TOKEN: Final = key_data["token"]
BOT_USERNAME: Final = key_data["bot"]

# Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(r"Hello Syafiq! You can type '\help' to see what I can do to help You!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"I am your Vistual Assistant, to help calculate your expenses! "
        f"\n\n"
        f"You can type: "
        f"\n- Input: To input the amount of expenses and the items. "
        f"\n- Expenses: To see total current expenses. "
        f"\n- Remaining: To see the total remaining amount of expenditure that has been made. "
        f"\n- Clear Data: To delete all data ever entered. "
    )


def google_api(filename: str, worksheet: str):
    scope = [
        "https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_key.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(filename).worksheet(worksheet)
    return sheet


# Responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

    sheet = google_api("Cash Flow", "Outcome")
    values_list = sheet.col_values(3)
    total_ = sum([int(price.replace("Rp", "").replace(",", "")) for price in values_list[1:]])
    total = "{:,.0f}".format(total_)

    if "input:" in processed:
        cleaned = processed[7:].strip().split("- ")
        cleaned = [cleaned.strip() for cleaned in cleaned if cleaned.strip()]

        output = pd.DataFrame({
            "Date": [datetime.now().strftime("%d-%h-%Y") for i in cleaned],
            "Item": [re.sub("[^A-Za-z]", "", item).title() for item in cleaned],
            "Price": [re.sub(r"\D", "", item) for item in cleaned],
        })
        output["Price"] = output["Price"].astype(int)

        row_number = sheet.col_values(1)
        row_number = len(row_number) - 1
        row = "A2"
        if row_number != 0:
            row = f"A{2 + row_number}"

        sheet.update(row, output.values.tolist())

        values_list = sheet.col_values(3)
        total_ = sum([int(price.replace("Rp", "").replace(",", "")) for price in values_list[1:]])
        total = "{:,.0f}".format(total_)
        
        return "Succees update Google Spreadsheet. Total Expenses: Rp {}.".format(total)

    if "expenses" in processed or "remaining" in processed:
        values_list = sheet.col_values(3)
        total_ = sum([int(price.replace("Rp", "").replace(",", "")) for price in values_list[1:]])
        total = "{:,.0f}".format(total_)

        if "expenses" in processed:
            return "Total Expenses: Rp {}.".format(total)
        else:
            total = "{:,.0f}".format(2000000 - total_)
            return "Total Remaining: Rp {}.".format(total)

    if "clear data" in processed:
        first_row_values = sheet.row_values(1)
        sheet.clear()
        sheet.append_row(first_row_values)
        return "Succees to clear all data."

    return "I do not understand what you wrote!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User {update.message.chat.id} in {message_type}: '{text}'")

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print("Bot:", response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print("Polling...")
    app.run_polling(poll_interval=5)
