"""
List of interesting events type:


"""


import logging


def handle_unknown(event):
    logging.warning("RTM event of type {} received, this event type is not "
                    "part of the list of known events".format(event['type']))
    logging.debug("event received:")
    for event_key, event_value in event.items():
        logging.debug("{}: {}".format(event_key, event_value))


def handle_not_implemented(event):
    logging.debug("RTM output of type {} received, no function implemented to "
                  "handle this type of event.".format(event['type']))

def handle_message(event):
    logging.info("received message event")
    logging.debug(event)


type_events = {
    'message': handle_message
}


def handle(events):
    """
    Depending on the type of the rtm output coming from the Slack firehose,
    redirect the rtm output to the correct handler.

    :param events: A list of Slack RTM event from the firehose,
    :rtype events: list<dict>
    """
    for event in events:
        try:
            # Launch handler function associated with the event
            type_events[event['type']](event)
        except KeyError:
            # No handler function for this event type
            handle_unknown(event)
