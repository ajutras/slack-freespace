from freespace.config import load_config


if __name__ == '__main__':
    load_config()

    # Now that the config has been loaded, it's safe to load any module
    from freespace import bot

    bot.start()
