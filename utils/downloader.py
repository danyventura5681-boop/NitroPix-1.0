async def get_telegram_file_url(bot, file_id):

    file = await bot.get_file(file_id)
    return file.file_path