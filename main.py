from numpy.ma import mean
from datetime import datetime
from config import day_start, day_end
from pyrogram import Client
import pandas as pd


app = Client("my_account")

yesterday = int(datetime.today().timestamp()) - 86400
answer_in_work_time = []
answer_not_in_work_time = []
manager_msg_date = 0
user_msg_date = 0

with app:
    start = datetime.strptime(day_start, "%H:%M:%S").time()
    end = datetime.strptime(day_end, "%H:%M:%S").time()
    data = []

    for dialog in app.iter_dialogs():
        if dialog.chat.type == "private":
            all_messages = app.iter_history(dialog.chat.id)

            for msg in reversed(all_messages):
                if msg.from_user.id == msg.chat.id:
                    if not user_msg_date:
                        user_msg_date = msg.date
                else:
                    if user_msg_date:
                        if end > datetime.fromtimestamp(msg.date).time() >= start:
                            answer_in_work_time.append(msg.date - user_msg_date)
                        else:
                            answer_not_in_work_time.append(msg.date - user_msg_date)

                        user_msg_date = 0

            username = f"@{msg.chat.username}" if msg.chat.username else msg.chat.first_name
            data.append({
                'юзернейм': f"@{msg.chat.username}" if msg.chat.username else msg.chat.first_name,
                'дата': datetime.fromtimestamp(msg.date),
                'avg раб. время': round(mean(answer_in_work_time)) if len(answer_in_work_time) == 1 else None,
                'avg не раб. время': round(mean(answer_not_in_work_time)) if len(answer_not_in_work_time) else None,
                'макс. раб. время': max(answer_in_work_time) if len(answer_in_work_time) == 1 else None,
                'макс. не раб. время': max(answer_not_in_work_time) if len(answer_not_in_work_time) == 1 else None,
                'кол-во сообщений': len(all_messages)
            })

df = pd.DataFrame(data)
df.to_excel('./message_report.xlsx')