import os
from flask import Flask, request, make_response, Response
from slackclient import SlackClient
from ebird import EbirdClient

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
EBIRD_TOKEN = os.environ["EBIRD_TOKEN"]

slack_client = SlackClient(SLACK_BOT_TOKEN)
ebird_client = EbirdClient(EBIRD_TOKEN)

app = Flask(__name__)

# TODO: Add checks for all responses from slack api calls


@app.route("/slack/test", methods=["POST"])
def command():

    msg = request.form
    print(msg)

    channel_id = msg['channel_id']

    msg_words = msg['text'].split()

    region_code = msg_words[0]

    df = ebird_client.get_recent_notable_observations_for_region(region_code, days_back=3)
    print(df)

    # send channel a message
    channel_msg = slack_client.api_call(
        "chat.postMessage",
        channel=channel_id,
        text=df['comName'][0]
    )

    return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
    app.run()
