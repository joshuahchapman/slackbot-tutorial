import os
from datetime import datetime
from threading import Thread
from flask import Flask, request, make_response
from slackclient import SlackClient
from ebird import EbirdClient

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
EBIRD_TOKEN = os.environ["EBIRD_TOKEN"]

slack_client = SlackClient(SLACK_BOT_TOKEN)
ebird_client = EbirdClient(EBIRD_TOKEN)

app = Flask(__name__)

# list of accepted commands
VALID_COMMANDS = ['recent', 'recent-notable']
RESTRICTED_COMMANDS = {
    'recent': ['directmessage', 'bot-test'],
    'recent-notable': ['directmessage', 'bot-test']
}


def parse_parameters(parameter_list):

    cmd = parameter_list.pop(0)

    if cmd not in VALID_COMMANDS:
        valid = False
        validation_message = 'Sorry, I don''t recognize the command _' + cmd + '_. ' + \
            'These are the commands I know: _' + '_, _'.join(VALID_COMMANDS) + '_.'

    else:
        valid = True
        validation_message = 'Command received. Working on it!'

    return valid, validation_message, cmd, parameter_list


def handle_command(cmd, cmd_params, channel_id):

    print('Handling command...')

    if cmd == 'recent':

        if len(cmd_params) != 2:
            return_message = 'Looks like you have the wrong number of inputs.\n' \
                    + 'Example of the expected format: `/ebird recent 38.9403316 -74.9212611`.'

        else:
            lat = cmd_params[0]
            long = cmd_params[1]

            df = ebird_client.get_recent_observations_by_lat_long(lat, long, distance=8, days_back=3)

            if df.empty or 'errors' in df.columns:
                return_message = 'eBird returned no observations near latitude ' + lat + ', longitude ' + long

            else:
                return_message = ''
                for index, row in df.iterrows():
                    # Format the datetime nicely for display.
                    pretty_dtm = datetime.strptime(row['obsDt'], '%Y-%m-%d %H:%M').strftime(
                        '%-m/%-d at %-I:%M %p')
                    return_message = return_message + '*' + row['comName'] + '*, ' + \
                        row['locName'] + ', on ' + pretty_dtm + '\n'

        # send channel a message
        channel_msg = slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=return_message
        )

        return

    if cmd == 'recent-notable':

        if len(cmd_params) != 2:
            return_message = 'Looks like you have the wrong number of inputs.\n' \
                    + 'The expected format is `/ebird recent-notable 38.9403316 -74.9212611`.'

        else:
            lat = cmd_params[0]
            long = cmd_params[1]

            df = ebird_client.get_recent_notable_observations_by_lat_long(lat, long, distance=8, days_back=3)

            if df.empty or 'errors' in df.columns:
                return 'eBird returned no notable observations near latitude ' + lat + ', longitude ' + long

            else:
                return_message = ''
                for index, row in df.iterrows():
                    # Format the datetime nicely for display.
                    pretty_dtm = datetime.strptime(row['obsDt'], '%Y-%m-%d %H:%M').strftime(
                        '%-m/%-d at %-I:%M %p')
                    return_message = return_message + '*' + row['comName'] + '*, ' + \
                        row['locName'] + ', on ' + pretty_dtm + '\n'

        # send channel a message
        channel_msg = slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=return_message
        )

        return


@app.route("/slack/ebird", methods=["POST"])
def command():

    msg = request.form
    print(msg)

    full_command = msg['text']
    params_valid, validation_message, cmd, cmd_parameters = parse_parameters(full_command.split())

    if not params_valid:
        return make_response(validation_message, 200)

    else:
        channel_id = msg['channel_id']
        channel_name = msg['channel_name']

        if cmd in RESTRICTED_COMMANDS.keys():
            if channel_name not in RESTRICTED_COMMANDS[cmd]:
                return make_response(
                    'Sorry, command _' + cmd + '_ is not allowed in this channel. ' +
                    'Please try it in a direct message (e.g. with yourself).',
                    200)

        thread = Thread(target=handle_command, args=(cmd, cmd_parameters, channel_id))
        thread.start()

        return make_response(validation_message, 200)


# Start the Flask server
if __name__ == "__main__":
    app.run()
