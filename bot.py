import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# ================= КОНФИГУРАЦИЯ =================
from config import TELEGRAM_TOKEN

# ================= РОУТЕР И ОБРАБОТЧИКИ =================
import handlers

# ================= Настройка логирования =================
logging.basicConfig(
    # Устанавливаем уровень INFO, чтобы записывать уровни логирования: INFO, WARNING, ERROR, CRITICAL
    level=logging.INFO,
    # Формат сообщения, включающий временную метку, имя логгера, уровень логирования и само сообщение
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),  # Запись логов в файл "bot.log" для дальнейшего анализа
        logging.StreamHandler(stream=sys.stdout) # Вывод логов в STDOUT консоль (без параметра stream по умолчанию выводит в STDERR)
    ]
)  # Вывод логов в консоль для отслеживания работы в реальном времени

# ================= ЗАПУСК БОТА =================
async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(handlers.router)
    
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        # default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")