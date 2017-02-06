
import logging
import time

from freespace.config import config
from freespace.rtm_handlers import handle
from freespace.slack_client import slack



def handle_command(command, channel):
    """
    Receives commands directed at the bot and determines if they are valid
    commands. If so, then acts on the commands. If not, returns back what it
    needs for clarification.

    :param command:
    :param command:

    :return:
    """
    response = ("Not sure what you mean. Use the *do* command with numbers, "
                "delimited by spaces.")

    if command.startswith('do'):
        response = "Sure...write some more code then I can do that!"
    slack_client.api_call("chat.postMessage", channel=channel, text=response,
                          as_user=True)


def handle_message(rtm_output):
    """
    Receives an RTM output of type message and treat it accordingly

    :param rtm_output:

    :return:
    """
    response = ("Not sure what you mean. Use the *do* command with numbers, "
                "delimited by spaces.")

    # if command.startswith('do'):
    #     response = "Sure...write some more code then I can do that!"
    # slack_client.api_call("chat.postMessage", channel=channel, text=response,
    #                       as_user=True)


def handle_slack_output(slack_rtm_output):
    """
    The Slack Real Time Messaging API is an events firehose. this parsing
    function returns None unless a message is directed at the Bot, based on
    its ID.

    :param slack_rtm_output: Slack Real Time Messaging output
    """

    if slack_rtm_output and len(slack_rtm_output) > 0:
        for output in slack_rtm_output:
            if output.get('type'):
                pass
                # if types_rtm_output.get(output['type']):
                #
                # else:
                #     logging.debug('unknown output detected:')


            # if output and output['text'] 'text' in output and AT_BOT in output['text']:
            #     # return text after the @ mention, whitespace removed
            #     return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
    return None, None


def start():
    """
    Start a connection to the RTM event stream and an infinite loop attempting
    to read from the stream and react to events with the handlers function.
    """

    while True:
        # Attempt connection to the Slack RTM event stream
        if slack.start_rtm():
            connected = True
        else:
            connected = False

        # Enter read loop if we are connected
        while connected:
            try:
                logging.info("reading..")
                handle(slack.read_rtm_stream())
                time.sleep(config.SLACK.RTM_READ_DELAY_IN_SECONDS)
            except:
                # Something went wrong, get out of the read loop
                logging.exception("stopping read")
                connected = False

        # Sleep for a while before retrying to connect to the stream
        time.sleep(config.SLACK.RTM_RETRY_DELAY_IN_SECONDS)


def test():

    print(slack.get_users())

    #print(slacker.get_users())
    #print(slacker.get_user(config.BOT.USER_ID))
    #print(slacker.get_channels())
    #print(slacker.get_channel('C4104TVR8'))
    # print(config)
    # print(config.SLACK)
    #slacker.send_message('hello world?')
    print("")
    # result = slacker.get_client()
    # print("")
    # print(slacker.user_id)
    # print(slacker.channels)

    print("")
    #result = slacker.get_channel(name=config.CHANNEL.NAME)
    # print("")
    # print(slacker.user_id)
    # print("")
    # print(slacker.channel_ids)
    # print("")
    # print("----")
    #  print(slacker.get_user_id('arbiter'))
    # print("connecting to slack")
    # if slack_client.rtm_connect():
    #     print("connected to slack")
    #
    #     while True:
    #         handle_slack_output(slack_client.rtm_read())
    #         time.sleep(0.05)  # delay between reading from firehose
    # else:
    #     print("failure to connect to slack")
    """
    rtm_connect
    rtm_read
    rtm_send_message

    """
