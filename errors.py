
class SlackClientFailedInit(Exception):
    """
    Represent an exception occuring while fetching initial IDs in a
    Slack client and failing to load a specific ID.
    """

    def __init__(self, msg):
        self.msg = msg