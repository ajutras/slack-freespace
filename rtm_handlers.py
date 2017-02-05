





def handle_unknown_rtm_type(rtm_output):
    for output_key, output_value in rtm_output.items():
        for output_key, output_value in output.items():
            logging.debug("{}: {}".format(output_key, output_value))


types_rtm_output = {
    # 'hello': None,
    'message': handle_message,
}


def handler(rtm_output):
    """
    Depending on the type of the rtm output coming from the Slack firehose,
    redirect the rtm output to the correct handler.

    :param rtm_output: A Slack RTM output from the firehose
        (behave like a dict)

    :return:
    """
    try:
        types_rtm_output[rtm_output['type']](rtm_output)
    except KeyError:
        handle_unknown_rtm_type(rtm_output)





