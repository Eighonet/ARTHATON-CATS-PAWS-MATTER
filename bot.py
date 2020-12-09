from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InputFile
import subprocess

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

save_path = r'C:/Users/Public/'
files_paths = dict()

async def evaluate(path_to_current_img):
    p2 = subprocess.Popen("python NN/evaluate.py --checkpoint NN/checkpoint/fns.ckpt --in-path "+ path_to_current_img + " --batch-size 1 --out-path " + path_to_current_img)
    return path_to_current_img


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nОтправь фотографию или несколько и напиши /finish.")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Здесь ты помощи не найдешь, страдай!")


@dp.message_handler(content_types=['photo'])
async def echo_image(msg: types.Message):
    file_id = msg['photo'][-1]['file_id']
    path = save_path + file_id + '.jpg'
    await msg.reply("Файл загружен, добавьте следующий или завершите работу.")
    await msg.photo[-1].download(path)
    path = await evaluate(path)
    if msg.from_user.id in files_paths.keys():
        files_paths[msg.from_user.id].append(path)
    else:
        files_paths[msg.from_user.id] = [path]

    # await bot.send_photo(msg.from_user.id, aaa)


@dp.message_handler(commands=['finish'])
async def finish_uploading(msg: types.Message):
    await msg.reply("Ожидайте обработки.")
    if msg.from_user.id not in files_paths.keys():
        await bot.send_message(msg.from_user.id, "А где изображения?")
    else:
        for path in files_paths[msg.from_user.id]:
            file = InputFile(path)
            await bot.send_photo(msg.from_user.id, file)
        files_paths[msg.from_user.id] = []
        # await bot.send_message(msg.from_user.id, "К сожалению, модель не отвечает. Возможно, сервер не запущен, обратитесь к администратору.")


if __name__ == '__main__':
    executor.start_polling(dp)