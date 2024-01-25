import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
# import cons
# import respons
from telegram.ext import *
from pytube import YouTube
from pytube import exceptions
import gspread
from datetime import datetime

API_KEY = "5393888231:AAGpX_qkYwtQJX8LBYh5JYz4ZQW7jQPVu1Q"
# connecting database
def connect_database(file_name = "test-1",json_file = 'test-1.json') -> gspread.Worksheet:
    profile = gspread.service_account(filename=json_file)

    
    file = profile.open(file_name)
    print("connected to file ("+file_name+")")

    sheet_list = file.worksheets()
    sheet = sheet_list[2]
    print("connected to sheet ("+sheet.title+")")
    return sheet

def start(update: Update,context):
    # global data_sheet
    update.message.reply_text('bot started! Type some commands...')
    buttons = [[InlineKeyboardButton("do first thing", callback_data="first")], [InlineKeyboardButton("do seconed thing", callback_data="seconed")]]
    # save_id(data_sheet,update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="select one thing to do")

def command_buttons(update: Update,context):
    buttons = [[KeyboardButton("/start")], [KeyboardButton("/download")], [KeyboardButton("/help")], [KeyboardButton("/save_id")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to bot! those are our my commands", reply_markup=ReplyKeyboardMarkup(buttons))

def help(update: Update, context: CallbackContext):
    update.message.reply_text("""
/start - start an get wolcoming message
/help - this message
/download - write the link after command to downlod video in this link
    """)
    

def download(update: Update, context: CallbackContext):
    if not context.args :
        update.message.reply_text('enter the video link after command!!!')
        return
    url = context.args[0]
    print(url, type(url))
    try:
        video = YouTube(url)
        fir = video.streams.get_highest_resolution()
        print(fir)
        print("Downloading...")
        update.message.reply_text('Downloading...')
        name = fir.download()
        # update.message.reply_video(video=fir.download(),timeout=60)
        print(name)
        update.message.reply_text('dowloaded! sending right now...')
        update.message.reply_video(video=open(name, 'rb'),timeout=120)
        # context.bot.send_video(chat_id=update.effective_chat.id,video="", text="Welcome to bot! those are our my commands")
        print("Done")
    except exceptions.RegexMatchError as ex:
        update.message.reply_text('invalid link')

def down(context: CallbackContext,id: int, video: YouTube):
    fir = video.streams.get_highest_resolution()
    print(fir)
    print("Downloading...")
    context.bot.send_message(chat_id=int(id), text="Dowloading...")
    name = fir.download()
    # update.message.reply_video(video=fir.download(),timeout=60)
    print(name)
    context.bot.send_message(chat_id=int(id), text="dowloaded! sending right now...")
    context.bot.send_video(chat_id=int(id), video=open(name, 'rb'),timeout=6000)
    # update.message.reply_text('dowloaded! sending right now...')
    # update.message.reply_video(video=open(name, 'rb'),timeout=60)
    print("Done")

def message_handler(update: Update, context):
    # global data_sheet
    # print(dir(update))
    # print(help(update))
    print(update.message.text)
    text = update.message.text
    # add_message_to_sheet(data_sheet,update.effective_chat.id,text)
    try:
        video = YouTube(text)  
    except exceptions.RegexMatchError as ex:
        print("it'sn't a link !!!")
        return
        # update.message.reply_text('invalid link')

    t = threading.Thread(target=down,args=(context,update.effective_chat.id,video))
    t.start()
    # fir = video.streams.get_highest_resolution()
    # print(fir)
    # print("Downloading...")
    # name = fir.download()
    # # update.message.reply_video(video=fir.download(),timeout=60)
    # print(name)
    # update.message.reply_text('dowloaded! sending right now...')
    # update.message.reply_video(video=open(name, 'rb'),timeout=60)
    # print("Done")


def test(update: Update, context: CallbackContext):
    # print(dir(update))
    # print(help(update))
    print("update.message.text")
    text = update.message.text
    context.bot.send_video(chat_id=update.effective_chat.id,video=text)
    pass
    
def stop(update: Update,context):
    update.message.reply_text('goodbye')
    print("stoping")
    
def query_handdler(update: Update,context):
    query = update.callback_query.data
    context.bot.send_message(chat_id=update.effective_chat.id, text=query)


def main():
    # global data_sheet
    # data_sheet = connect_database()
    updater = Updater(API_KEY)
    disp = updater.dispatcher

    disp.add_handler(CommandHandler("start",start))
    disp.add_handler(CommandHandler("commands",command_buttons))
    disp.add_handler(CommandHandler("stop",stop))
    disp.add_handler(CommandHandler("help",help))
    # disp.add_handler(CommandHandler("download", download))
    # disp.add_handler(MessageHandler(Filters.video, download))

    # disp.add_handler(MessageHandler(Filters.text, test))

    disp.add_handler(MessageHandler(Filters.text, message_handler))
    disp.add_handler(CallbackQueryHandler(query_handdler))
    updater.start_polling()
    updater.idle()

def find_id(sheet: gspread.Worksheet,id: str):
    cell = sheet.find(id,in_column=1,case_sensitive=False)
    if cell == None:
        return None, None
    # print(type(cell))
    cell = str(cell)
    # print(cell)
    cell = cell.split(" ")[1]
    # print(cell)
    return cell[1], cell[3]

def find_in_headers(sheet: gspread.Worksheet,header: str) -> int:
    '''return column number where is the header exist\n
    retrun None in case there is no such header'''
    cell = sheet.find(header,in_row=1,case_sensitive=False)
    if cell == None:
        return None, None
    cell = str(cell)
    cell = cell.split(" ")[1]
    # print(cell)
    return int(cell[3])

def save_id(sheet: gspread.Worksheet, id: str):
    # global data_sheet
    # sheet = data_sheet
    cell = find_id(sheet,str(id))
    print(cell)
    if cell[0] == None:
        sheet.append_row([str(id)])
        # appned_id(sheet,id)

def append_to_row(sheet: gspread.Worksheet, row_no: str or int, text: str):
    row = sheet.row_values(row_no)
    col_no = len(row) + 1
    sheet.update_cell(row_no,col_no,text)

def append_to_col(sheet: gspread.Worksheet, col_no: str or int, text: str):
    col = sheet.col_values(col_no)
    row_no = len(col) + 1
    sheet.update_cell(row_no,col_no,text)

def add_message_to_sheet(sheet: gspread.Worksheet,id: str,message: str):
    row_no = find_id(sheet,str(id))[0]
    # row = sheet.row_values(row_no)
    # print(row)
    # col_no = len(row) + 1 #row.index(row[-1]) + 2
    # sheet.update_cell(row_no,col_no,message)
    time = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    # sheet.update_cell(row_no,col_no+1,time)

    append_to_row(sheet,row_no,message)
    append_to_row(sheet,row_no,time)

if __name__ == '__main__':
    main()