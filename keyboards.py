from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Добавить задачу"),
                KeyboardButton(text="Добавить сделку")
            ],
            [
                KeyboardButton(text="Просмотреть задачи"),
                KeyboardButton(text="Просмотреть сделки")
            ],
            [
                KeyboardButton(text="Получить мотивацию")
            ]
        ],
        resize_keyboard=True
    )

def get_tasks_keyboard(tasks: list):
    builder = []
    for index, task in enumerate(tasks):
        # Callback data format: action:index
        btn = InlineKeyboardButton(
            text=f"🗑 Удалить: {task['name']}", 
            callback_data=f"del_task:{index}"
        )
        builder.append([btn])
    return InlineKeyboardMarkup(inline_keyboard=builder)

def get_deals_keyboard(deals: list):
    builder = []
    for index, deal in enumerate(deals):
        btn = InlineKeyboardButton(
            text=f"✏️ Статус: {deal['name']}", 
            callback_data=f"edit_deal:{index}"
        )
        builder.append([btn])
    return InlineKeyboardMarkup(inline_keyboard=builder)