import os
from datetime import datetime
from threading import Thread
import requests
from flask import Flask, request, make_response, Response
from slackclient import SlackClient
from ebird import EbirdClient

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
EBIRD_TOKEN = os.environ["EBIRD_TOKEN"]

slack_client = SlackClient(SLACK_BOT_TOKEN)
ebird_client = EbirdClient(EBIRD_TOKEN)

app = Flask(__name__)

# list of accepted commands
VALID_COMMANDS = ['recent', 'recent-notable']


def parse_parameters(parameter_list):

    cmd = parameter_list.pop(0)

    if cmd not in VALID_COMMANDS:
        valid = False
        validation_message = 'Sorry, I don''t recognize the command ' + cmd + '. ' + \
            'These are the commands I know: ' + ", ".join(VALID_COMMANDS)

    else:
        valid = True
        validation_message = 'Valid command.'

    return valid, validation_message, cmd, parameter_list


def handle_command(cmd, cmd_params, response_url):

    if cmd == 'recent':

        if len(cmd_params) != 2:
            return 'Looks like you have the wrong number of inputs.\n' \
                    + 'The expected format is `/slashtest recent [latitude] [longitude]`.\n' \
                    + 'For example: `/slashtest recent 38.9403316 -74.9212611`'

        lat = cmd_params[0]
        long = cmd_params[1]

        df = ebird_client.get_recent_observations_by_lat_long(lat, long, distance=8, days_back=3)

        if df.empty or 'errors' in df.columns:
            return 'eBird returned no observations near latitude ' + lat + ', longitude ' + long

        return_message = ''
        for index, row in df.iterrows():
            # Format the datetime nicely for display.
            pretty_dtm = datetime.strptime(row['obsDt'], '%Y-%m-%d %H:%M').strftime(
                '%-m/%-d at %-I:%M %p')
            return_message = return_message + '*' + row['comName'] + '*, ' + \
                row['locName'] + ', on ' + pretty_dtm + '\n'

        api_params = {
            "token": SLACK_BOT_TOKEN,
            "text": return_message
        }

        requests.post(url=response_url, params=api_params)
        return

    if cmd == 'recent-notable':

        if len(cmd_params) != 2:
            return 'Looks like you have the wrong number of inputs.\n' \
                    + 'The expected format is `/slashtest recent-notable [latitude] [longitude]`.\n' \
                    + 'For example: `/slashtest recent-notable 38.9403316 -74.9212611`'

        lat = cmd_params[0]
        long = cmd_params[1]

        # TO DO: validate coordinates?

        df = ebird_client.get_recent_notable_observations_by_lat_long(lat, long, distance=8, days_back=3)

        if df.empty or 'errors' in df.columns:
            return 'eBird returned no notable observations near latitude ' + lat + ', longitude ' + long

        return_message = ''
        for index, row in df.iterrows():
            # Format the datetime nicely for display.
            pretty_dtm = datetime.strptime(row['obsDt'], '%Y-%m-%d %H:%M').strftime(
                '%-m/%-d at %-I:%M %p')
            return_message = return_message + '*' + row['comName'] + '*, ' + \
                row['locName'] + ', on ' + pretty_dtm + '\n'

        return return_message


@app.route("/slack/test", methods=["POST"])
def command():

    msg = request.form
    print(msg)

    full_command = msg['text']
    params_valid, validation_message, cmd, cmd_parameters = parse_parameters(full_command.split())

# Thread stuff
    response_url = msg['response_url']
    thread = Thread(target=handle_command, args=(cmd, cmd_parameters, response_url))
    thread.start()
    return make_response(validation_message, 200)


# Start the Flask server
if __name__ == "__main__":
    app.run()
