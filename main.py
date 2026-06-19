from datetime import datetime
from telebot import types, TeleBot
from typing import Final, cast
from config import settings
from database import db
from decimal import Decimal

bot: Final = TeleBot(settings.BOT_TOKEN)
      





@bot.message_handler(commands=['start', 'help'])                  # Start
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Create the buttons
    btn_balance = types.KeyboardButton("Balance")
    btn_history = types.KeyboardButton("History")
    btn_history_del = types.KeyboardButton("Cleaning History")
    markup.add(btn_balance, btn_history, btn_history_del)
    
    welcome_text = (
        f"  Hello, {message.from_user.first_name}! 👋\n"
        "I'm your finance assistant.\n\n"
        "Use the buttons listed, or if you want to create a transaction, enter:\n    "
        'Transaction type, amount, category\n\n'
        "Calculate the amount of expenses separately for each category - /report"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")
 


@bot.message_handler(commands=['report'])                  
def SendReport(message):
    Report_text = f"Hello, {message.from_user.first_name}! \n"
    
    try:
        user_id = message.from_user.id
        res = db.get_category_report(user_id)
        
        if not res:
            bot.send_message(message.chat.id, "Your expenses are not found.")
            return

        details = ""
        total_sum = Decimal('0')
        for category, amount in res:
            details += f"🔸 {category}: ${amount}\n"
            amount = cast(Decimal, amount)
            total_sum += amount
        final_text = (
            f"{Report_text}"
            f"{details}\n"
            f"💰 Total: ${total_sum:.2f}"
        )
        bot.send_message(message.chat.id, final_text, parse_mode="Markdown")
    except Exception as e:
        print(f'Report_ERROR: {e}')
        bot.send_message(message.chat.id, 'Error occurred ')







@bot.message_handler(func=lambda message: message.text.capitalize() == "Balance")
def show_balance(message):
    try:
        user_id = message.from_user.id
        total = db.get_balance(user_id)
    
        bot.send_message(message.chat.id, f"Your current balance: ${total}.")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Unexpected balance sheet error occurred.")
        print(f"Balance_ERROR: {e}")






@bot.message_handler(func=lambda message: message.text.capitalize() == "History") 
def show_history(message):
    user_id = message.from_user.id
    history = db.get_history(user_id)
    
    if not history:
        bot.send_message(message.chat.id, "Transaction history is now empty.")
        return

    response = "Last 10 transactions:\n\n"
    for category, amount, sign in history:
        icon = "🟢" if sign == "+" else "🔴"
        response += f"{icon} {sign}${amount:.2f} • {category}\n"
    
    bot.send_message(message.chat.id, response)








@bot.message_handler(func=lambda message: message.text.split()[0].lower() in ['expense', 'income'])
def handle_operation(message):
    try:
        parts = message.text.split()
        user_id = message.from_user.id
        op_type = parts[0].capitalize() 
        
        
        if len(parts) < 2:
            bot.reply_to(message, '⚠️ Enter the amount. Example: "expense 500"')
            return

        amount = float(parts[1])
        category = parts[2] if len(parts) > 2 else "None"
        
        db.add_operation(user_id, op_type, category, amount, datetime.now().strftime('%Y-%m-%d %H:%M'))
        bot.send_message(message.chat.id, "✅ Transaction logged!")


        markup = types.InlineKeyboardMarkup()
        undo_btn = types.InlineKeyboardButton("↩️ Cancel the transaction", callback_data="undo_last")
        markup.add(undo_btn)

        bot.send_message(message.chat.id, f"✅ Transaction successfully logged: {op_type} ${amount}", reply_markup=markup)
    
        
    except ValueError:
        bot.reply_to(message, "❌ Error! Please enter a valid number.")
    except Exception as e:
        print(f"Transaction_ERROR: {e}")
        bot.reply_to(message, "❌ Unexpected Error occurred.")


        
        

@bot.callback_query_handler(func=lambda call: call.data == 'undo_last')
def get_undo_callback(call):    
    db.delete_last_operation(call.from_user.id)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id, 
                            text="Transaction canceled.")
        
                           
                         





@bot.message_handler(func=lambda message: message.text == "Cleaning History") #.strip().lower()
def ask_clear_confirmation(message):
    markup =  types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("✅ Clean", callback_data="confirm_clear")
    btn_no =  types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_clear")
    markup.add(btn_yes, btn_no)
    
    bot.send_message(message.chat.id, "⚠️ This action cannot be undone. Are you sure you want to Clean entire history?", reply_markup=markup)    
    
    
    
    
    
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_clear", "cancel_clear"])
def process_clear_callback(call):
    if call.data == "confirm_clear":
        db.clear_history(call.from_user.id)
        bot.edit_message_text(chat_id=call.message.chat.id, 
                              message_id=call.message.message_id, 
                              text="History cleared successfully.")
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, 
                              message_id=call.message.message_id, 
                              text="Cleaning canceled.")    

    
    
    
    
    
    
    
@bot.message_handler(func=lambda message: True)
def unknown_message(message):
    bot.reply_to(message, """Use the buttons listed, 
or if you want to create a transaction, enter: Expense/Income, amount, category.
            Example: 'expense 2000 education' """
    )
    
    
    
    

print("Running... ")
bot.polling()   