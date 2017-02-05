
import logging
from slackclient import SlackClient

from freespace.config import config


class Slack:
    def __init__(self):
        self._client = None

    def get_client(self):
        """
        Get a SlackClient object instantiated with the token.

        :return: A SlackClient object instantiated with the token or None
        """
        # Initialize Slack client if it's the first time calling it
        if not self._client:
            logging.info("initializing Slack client")

            try:
                self._client = SlackClient(config.SLACK.TOKEN)
                if self.is_api_working():
                    logging.debug("initialized Slack client")
                else:
                    raise Exception("api.test did not return OK")
            except:
                logging.exception('failed to initialize Slack client')

        return self._client

    def is_api_working(self):
        """
        Attempt to call the Slack API and request a response. Use this to
        verify that the link to the Slack APIs are working as intended.

        :return: True is the Slack API returned that everything was working,
            False otherwise
        """
        result_call = self.make_api_call('api.test') or False
        return result_call or False

    def make_api_call(self, method, timeout=20, default_return=None, **kwargs):
        """

        :param method:
        :param timeout:
        :param kwargs:
        :return:
        """

        for _ in range(3):
            try:
                slack = self.get_client()
                result_call = slack.api_call(method, timeout, **kwargs)

                if result_call.get('ok'):
                    if result_call.get("warning"):
                        logging.warning(
                            "the following Slack API call returned a warning: "
                            "{}\nwarning message: {}"
                            .format(method, result_call["warning"]))

                    print(result_call)
                    return result_call
                else:
                    logging.warning("the following Slack API call did not "
                                    "return OK: {}.\nerror message: {}"
                                    .format(method, result_call['error']))
            except:
                logging.exception("failed to make the following Slack API "
                                  "call: {}".format(method))
        else:
            return default_return

    # Channel
    def get_channel(self, channel_id):
        result_call = self.make_api_call(
            'channels.info', channel=channel_id) or {}
        return result_call.get('channel') or {}

    def get_channels(self):
        result_call = self.make_api_call('channels.list') or {}
        return result_call.get('channels') or []

    # User
    def get_user(self, user_id):
        result_call = self.make_api_call('users.info', user=user_id) or {}
        return result_call.get('user') or {}

    def get_users(self):
        result_call = self.make_api_call('users.list') or {}
        return result_call.get('members') or []

    # Chat
    def send_message(self, text, channel=config.FREESPACE.CHANNEL_ID,
                     parse=None, link_names=True, attachments=None,
                     unfurl_links=True, unfurl_media=False,
                     username=config.BOT.USERNAME, as_user=False,
                     icon_url=config.BOT.ICON_URL,
                     icon_emoji=None, thread_ts=None, reply_broadcast=False):
        """
        Post a message to a slack public/private channel, private group or
        direct message.

        :param text: The text of the message to be posted.
        :param channel: A Slack public/private channel private group or direct
        message (IM) ID. The name of the channel can also be used instead of
        the ID for a public channel or a private group.
        :param parse: Change how messages are treated
        :param link_names: Find and link channel names and usernames.
        :param attachments: Structured message attachments.
        :rtype attachments: list
        :param unfurl_links: Pass true to enable unfurling of primarily
            text-based content.
        :param unfurl_media: Pass false to disable unfurling of media content.
        :param username: Set your bot's user name. Must be used in conjunction
            with as_user set to false, otherwise ignored.
        :param as_user: Pass true to post the message as the authed user,
            instead of as a bot.
        :param icon_url: URL to an image to use as the icon for this message.
            Must be used in conjunction with as_user set to false, otherwise
            ignored.
        :param icon_emoji: Emoji to use as the icon for this message. Overrides
            icon_url. Must be used in conjunction with as_user set to false,
            otherwise ignored.
        :param thread_ts: Provide another message's ts value to make this
            message a reply. Avoid using a reply's ts value; use its parent
            instead.
        :param reply_broadcast: Used in conjunction with thread_ts and
            indicates whether reply should be made visible to everyone in the
            channel or conversation.

        :return: A dict with information on the result of the message or an
            empty dict in the case of catastrophic failure.
        """

        # Construct message as dict
        message_kwargs = {
            'channel': channel,
            'text': text,
            'parse': parse,
            'link_names': link_names,
            'unfurl_links': unfurl_links,
            'unfurl_media': unfurl_media,
            'as_user': as_user
        }

        if attachments:
            message_kwargs['attachements'] = attachments

        if not as_user and username:
            message_kwargs['username'] = username

        if not as_user and icon_url:
            message_kwargs['icon_url'] = icon_url

        if not as_user and icon_emoji:
            message_kwargs['icon_emoji'] = icon_emoji

        if thread_ts:
            message_kwargs['thread_ts'] = thread_ts

        if thread_ts and reply_broadcast:
            message_kwargs['reply_broadcast'] = reply_broadcast

        # Send message
        result_call = self.make_api_call(
            'chat.postMessage', **message_kwargs) or {}

        return result_call.get('message') or {}
