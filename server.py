import os
from flask import Flask, request, make_response, Response
from slackclient import SlackClient
from ebird import EbirdClient

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
EBIRD_TOKEN = os.environ["EBIRD_TOKEN"]

slack_client = SlackClient(SLACK_BOT_TOKEN)
ebird_client = EbirdClient(EBIRD_TOKEN)

app = Flask(__name__)

# list of accepted commands
VALID_COMMANDS = ['recent']


def parse_parameters(parameter_list):

    cmd = parameter_list.pop(0)

    if cmd not in VALID_COMMANDS:
        valid = False
        validation_message = 'Sorry, I don''t recognize the command ' + cmd + '. ' + \
            'These are the commands I know: ' + ", ".join(VALID_COMMANDS)

    else:

        # TO DO: Add logic for each valid command, to validate the rest of the inputs

        valid = True
        validation_message = 'Valid command.'

    return valid, validation_message, cmd, parameter_list


def handle_command(cmd, cmd_params):

    if cmd == 'recent':

        lat = cmd_params[0]
        long = cmd_params[1]

        # TO DO: validate coordinates?

        df = ebird_client.get_recent_observations_by_lat_long(lat, long, distance=8, days_back=3)

        if df.empty or 'errors' in df.columns:
            return 'eBird returned no observations near latitude ' + lat + ', longitude ' + long

        return_message = ''
        for index, row in df.iterrows():
            return_message = return_message + row['comName'] + ' ' + row['obsDt'] + '\n'

        return return_message


@app.route("/slack/test", methods=["POST"])
def command():

    msg = request.form
    print(msg)

    channel_id = msg['channel_id']
    full_command = msg['text']

    params_valid, validation_message, cmd, cmd_parameters = parse_parameters(full_command.split())

    if params_valid is False:
        # send channel a message
        channel_msg = slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=validation_message
        )
        return make_response("", 200)

    else:
        return_message = handle_command(cmd, cmd_parameters)

        # send channel a message
        channel_msg = slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=return_message
        )

    return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
    app.run()
