
import logging
from slackclient import SlackClient

from freespace.config import config
from freespace.errors import SlackClientFailedInit


slack = None


class Slack:
    def __init__(self):
        self._client = None
        self.channels = {}
        self.user_id = ""

    def get_client(self):
        """
        Get a SlackClient object instantiated with the token.

        :return: A SlackClient object instantiated with the token or None
        """
        # Initialize Slack client if it's the first time calling it
        if not self._client:
            logging.info("connecting Slack client")

            try:
                self._client = SlackClient(config.SLACK.TOKEN)
                if self.is_api_working():
                    logging.debug("connected Slack client")
                    logging.info("initializing client")
                    if self._init_client():
                        logging.debug("Slack client was initialized with all "
                                      "ids ")
                else:
                    raise Exception("error while testing the connection: "
                                    "api.test did not return OK")
            except SlackClientFailedInit:
                self._client = None
                logging.exception("failed to initialize Slack client with the "
                                  "resources listed in the config")
            except Exception:
                self._client = None
                logging.exception("failure during the connection of the Slack "
                                  "client to the Slack API")
        return self._client

    def _init_client(self):
        """
        Attempt to fetch ID for the following resource named in config:

            - Bot Slack user ID
            - Channel ID for the default channel

        :return: True if both a user id and channel id have been found matching
            the name of the resources defined in config.BOT.NAME and
            config.CHANNEL.NAME
        """
        # Get user ID
        user = self.get_user(name=config.BOT.NAME)
        if user and user.get('id'):
            self.user_id = user['id']
        else:
            raise SlackClientFailedInit(
                "could not find a Slack user ID for a user named {} "
                "(config.BOT.NAME)".format(config.BOT.NAME))

        # Get channels IDs
        for channel_name in config.CHANNEL.NAMES:
            channel = self.get_channel(name=channel_name)
            if channel and channel.get('id'):
                self.channels[channel_name] = channel['id']
            else:
                raise SlackClientFailedInit(
                    "could not find a Slack channel ID for a channel named {} "
                    "(config.CHANNEL.NAMES)".format(channel_name))
        return True

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
        Attempt to make an API call to Slack. Will retry two times if first
        call fail.

        :param method: A Slack call method. Ref: https://api.slack.com/methods
        :rtype method: str
        :param timeout: A timeout value in seconds before the API call will
            timeout.
        :rtype timeout: int
        :param kwargs: Key arguments to send to the slack API.
        :rtype kwargs: dict

        :return: The resulting payload of the API call or default_return if
            the API call did not execute properly or did not return OK.
        """

        for _ in range(3):
            try:
                slacker = self.get_client()
                result_call = slacker.api_call(method, timeout, **kwargs)

                if result_call.get('ok'):  # Call was successful
                    if result_call.get("warning"):
                        logging.warning(
                            "the following Slack API call returned a warning: "
                            "{}\nwarning message: {}"
                            .format(method, result_call["warning"]))

                    return result_call
                else:  # Call was received by Slack API but did not work
                    logging.warning("the following Slack API call did not "
                                    "return OK: {}.\nerror message: {}"
                                    .format(method, result_call['error']))
            except:  # Call likely never reached Slack API
                logging.exception("failed to make the following Slack API "
                                  "call: {}".format(method))
        else:  # 3 tries to make the API call
            return default_return

    # Channel
    def get_channel(self, channel_id=None, name=None):
        """
        Get information on a specific channel based on its ID or name.

        :param channel_id: A Slack channel ID.
        :rtype channel: str
        :param name: A Slack channel name, case insensitive. All channels in
            Slack are all lowercase.
        :rtype name: str

        :return: A Slack Channel dict if found, an empty dict otherwise.
        """
        if not channel_id and not name:
            return {}

        # Search by ID
        if channel_id:
            result_call = self.make_api_call(
                'channels.info', channel=channel_id) or {}
        # Search by Name
        else:
            result_call = {}
            channels = self.get_channels()
            for channel in channels:
                if channel['name'] == name.lower():
                    return channel

        return result_call.get('channel') or {}

    def get_channels(self):
        """
        Get information on all the channels in a team.

        :return: A list of dict each representing a channel or an empty list if
            something went wrong.
        """
        result_call = self.make_api_call('channels.list') or {}
        return result_call.get('channels') or []

    # User
    def get_user(self, user_id=None, name=None):
        """
        Get information on a specific user based on its ID or name.

        :param user_id: A Slack user ID.
        :param name: A Slack user name.

        :return: A Slack User dict if found, an empty dict otherwise.
        """
        if not user_id and not name:
            return {}

        # Search by ID
        if user_id:
            result_call = self.make_api_call('users.info', user=user_id) or {}
        # Search by Name
        else:
            result_call = {}
            users = self.get_users()
            for user in users:
                # TODO: verify if name is unique, and case sensitive.
                if user['name'] == name:
                    return user

        return result_call.get('user') or {}

    def get_users(self):
        """
        Get information on all the users in a team.

        :return: A list of dict each representing a user or an empty list if
            something went wrong.
        """
        result_call = self.make_api_call('users.list') or {}
        return result_call.get('members') or []

    # Chat
    def send_message(self, text, channel=None,
                     parse=None, link_names=True, attachments=None,
                     unfurl_links=True, unfurl_media=False,
                     username=None, as_user=False, icon_url=None,
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

        # Load defaults
        channel = channel or self.channels[self.channels.keys()[0]]

        if not as_user and not username and config.BOT.NAME:
            username = config.BOT.NAME

        if not as_user and not icon_url and config.BOT.ICON_URL:
            icon_url = config.BOT.ICON_URL

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

    # Real Time Messaging (RTM)
    def start_rtm(self):
        """
        Start a connection to the RTM stream.

        :return: True if the client connected correctly to the RTM stream;
            False otherwise.
        """
        slacker = self.get_client()
        logging.info("connecting to the Slack RTM stream")

        if slacker.rtm_connect():
            logging.debug("connected to the Slack RTM stream")
            return True
        else:
            logging.error("failed to connect to the Slack RTM stream")
            return False

    def read_rtm_stream(self):
        """
        Read events from the RTM stream.

        :return: 0 to * Slack Events
        """
        slacker = self.get_client()
        return slacker.rtm_read()


def start_client():
    global slack
    slack = Slack()
    slack.get_client()
