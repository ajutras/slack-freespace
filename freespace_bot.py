
from freespace.config import load_config


def freespace_init():
    """
    Initialize the configuration, logging and initialize the Stack client.
    Call the main application loop.
    """
    load_config()

    # Now that the config has been loaded, it's safe to load the adapters
    from freespace.slack_client import start_client
    start_client()  # Initialize global instance of the Slack client

    # Start the bot
    from freespace import bot
    bot.start()  # Start main loop


if __name__ == '__main__':
    freespace_init()
