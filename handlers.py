import logging
from openai import AsyncOpenAI
from aiogram.filters import (
    CommandStart,
)
from aiogram.types import (
    Message,
    CallbackQuery,
)
from aiogram import (
    F,
    html,
    Router,
)
from aiogram.fsm.context import FSMContext

# ================= КОНФИГУРАЦИЯ =================
from config import OPENAI_API_KEY

# ================= МАШИНА СОСТОЯНИЙ (FSM) =================
from states import TaskStates, DealStates, EditDealStates

# ================= ХРАНИЛИЩЕ ДАННЫХ (In-Memory) =================
from storage import get_user_db

# ================= КЛАВИАТУРЫ =================
from keyboards import get_main_keyboard, get_tasks_keyboard, get_deals_keyboard

# Настройка клиента OpenAI
aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)

router = Router()

# --- /START ---
@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! 🚀\n"
        #f"Привет, **{message.from_user.full_name}**! 🚀\n"
        "Я твой помощник по продажам и маркетингу.\n"
        "Выбери действие ниже:",
        reply_markup=get_main_keyboard()
    )

# --- ДОБАВЛЕНИЕ ЗАДАЧИ ---
@router.message(F.text == "Добавить задачу")
async def start_add_task(message: Message, state: FSMContext):
    await state.set_state(TaskStates.waiting_for_name)
    await message.answer("Введите название задачи (например, 'Подготовить КП'):")

@router.message(TaskStates.waiting_for_name)
async def task_name_chosen(message: Message, state: FSMContext):
    await state.update_data(task_name=message.text)
    await state.set_state(TaskStates.waiting_for_time)
    await message.answer("Введите время выполнения задачи (например, 'Сегодня в 14:00'):")

@router.message(TaskStates.waiting_for_time)
async def task_time_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    db = get_user_db(message.from_user.id)
    
    new_task = {
        "name": user_data['task_name'],
        "time": message.text
    }
    db["tasks"].append(new_task)
    
    await state.clear()
    await message.answer(
        f"✅ Задача <b>{new_task['name']}</b> сохранена!\n"
        f"⏰ Время: {new_task['time']}\n\n"
        "<i>Это твой шанс закрыть сделку!</i> 🔥",
        reply_markup=get_main_keyboard()
    )

# --- ПРОСМОТР И УДАЛЕНИЕ ЗАДАЧ ---
@router.message(F.text == "Просмотреть задачи")
async def view_tasks(message: Message):
    db = get_user_db(message.from_user.id)
    tasks = db["tasks"]
    
    if not tasks:
        await message.answer("Список задач пуст.")
        return

    text_resp = "📋 <b>Ваши задачи:</b>\n\n"
    for i, t in enumerate(tasks):
        text_resp += f"{i+1}. {t['name']} (⏰ {t['time']})\n"
    
    await message.answer(text_resp, reply_markup=get_tasks_keyboard(tasks))

@router.callback_query(F.data.startswith("del_task:"))
async def delete_task_callback(callback: CallbackQuery):
    idx = int(callback.data.split(":")[1])
    db = get_user_db(callback.from_user.id)
    
    if 0 <= idx < len(db["tasks"]):
        removed = db["tasks"].pop(idx)
        await callback.message.edit_text(
            f"❌ Задача '{removed['name']}' удалена.",
            reply_markup=get_tasks_keyboard(db["tasks"]) if db["tasks"] else None
        )
        if not db["tasks"]:
            await callback.message.answer("Список задач теперь пуст.")
    else:
        await callback.answer("Ошибка удаления", show_alert=True)

# --- ДОБАВЛЕНИЕ СДЕЛКИ ---
@router.message(F.text == "Добавить сделку")
async def start_add_deal(message: Message, state: FSMContext):
    await state.set_state(DealStates.waiting_for_name)
    await message.answer("Введите название сделки (например, 'Сделка с ООО Ромашка'):")

@router.message(DealStates.waiting_for_name)
async def deal_name_chosen(message: Message, state: FSMContext):
    await state.update_data(deal_name=message.text)
    await state.set_state(DealStates.waiting_for_amount)
    await message.answer("Введите сумму сделки:")

@router.message(DealStates.waiting_for_amount)
async def deal_amount_chosen(message: Message, state: FSMContext):
    await state.update_data(deal_amount=message.text)
    await state.set_state(DealStates.waiting_for_status)
    await message.answer("Введите статус сделки (например, 'В процессе', 'Закрыта'):")

@router.message(DealStates.waiting_for_status)
async def deal_status_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    db = get_user_db(message.from_user.id)
    
    new_deal = {
        "name": user_data['deal_name'],
        "amount": user_data['deal_amount'],
        "status": message.text
    }
    db["deals"].append(new_deal)
    
    await state.clear()
    await message.answer(
        f"🤝 Сделка <b>{new_deal['name']}</b> сохранена!\n"
        f"💰 Сумма: {new_deal['amount']}\n"
        f"📊 Статус: {new_deal['status']}",
        reply_markup=get_main_keyboard()
    )

# --- ПРОСМОТР И ИЗМЕНЕНИЕ СДЕЛОК ---
@router.message(F.text == "Просмотреть сделки")
async def view_deals(message: Message):
    db = get_user_db(message.from_user.id)
    deals = db["deals"]
    
    if not deals:
        await message.answer("Список сделок пуст.")
        return

    text_resp = "💼 <b>Ваши сделки:</b>\n\n"
    for i, d in enumerate(deals):
        text_resp += f"{i+1}. {d['name']} | 💰 {d['amount']} | 📊 {d['status']}\n"
    
    await message.answer(text_resp, reply_markup=get_deals_keyboard(deals))

@router.callback_query(F.data.startswith("edit_deal:"))
async def edit_deal_callback(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    # Сохраняем индекс редактируемой сделки в состояние
    await state.update_data(edit_deal_index=idx)
    await state.set_state(EditDealStates.waiting_for_new_status)
    
    await callback.message.answer("Введите новый статус для этой сделки:")
    await callback.answer()

@router.message(EditDealStates.waiting_for_new_status)
async def save_new_deal_status(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data.get("edit_deal_index")
    db = get_user_db(message.from_user.id)
    
    if idx is not None and 0 <= idx < len(db["deals"]):
        db["deals"][idx]["status"] = message.text
        await message.answer(f"✅ Статус сделки '{db['deals'][idx]['name']}' обновлен на: {message.text}")
        
        # Показать обновленный список
        await view_deals(message)
    else:
        await message.answer("Ошибка при обновлении сделки.")
    
    await state.clear()

# --- МОТИВАЦИЯ (CHATGPT) ---
@router.message(F.text == "Получить мотивацию")
async def get_motivation(message: Message):
    processing_msg = await message.answer("Генерирую мотивацию... 🧠")
    
    try:
        # Промпт для ChatGPT
        prompt = "Придумай короткую, вдохновляющую фразу для менеджера по продажам, чтобы зарядить его на успех в сделках. Не используй кавычки."
        
        response = await aclient.chat.completions.create(
            model="gpt-3.5-turbo", # Или gpt-4o
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60
        )
        
        motivation_text = response.choices[0].message.content
        await processing_msg.edit_text(f"✨ <b>Мотивация на сегодня:</b>\n\n{motivation_text}")
        
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        # Фолбек, если нет токена или ошибка API
        await processing_msg.edit_text("✨ Каждая сделка — это шаг к успеху! (API недоступен, но ты всё равно молодец!)")
