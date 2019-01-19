import os
from flask import Flask, request, make_response, Response
from slackclient import SlackClient
import ebird

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
EBIRD_TOKEN = os.environ["EBIRD_TOKEN"]

slack_client = SlackClient(SLACK_BOT_TOKEN)

app = Flask(__name__)

# TODO: Add checks for all responses from slack api calls


@app.route("/slack/test", methods=["POST"])
def command():

    msg = request.form
    print(msg)

    channel_id = msg['channel_id']

    # send channel a message
    channel_msg = slack_client.api_call (
        "chat.postMessage",
        channel=channel_id,
        text=request.form.get('text')
    )

    return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
    app.run()
