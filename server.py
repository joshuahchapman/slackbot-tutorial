import os
# import json
from flask import Flask, request, make_response, Response
# from tokens import SLACK_BOT_TOKEN, SLACK_VERIFICATION_TOKEN
from slackclient import SlackClient
# from slashCommand import *

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
slack_client = SlackClient(SLACK_BOT_TOKEN)
app = Flask(__name__)

# commander = Slash("Hey there! It works.")

# TODO: Add checks for all responses from slack api calls


# def verify_slack_token(request_token):
#     if SLACK_VERIFICATION_TOKEN != request_token:
#         print("Error: invalid verification token!")
#         print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
#         return make_response("Request contains invalid Slack verification token", 403)


@app.route("/slack/test", methods=["POST"])
def command():

    msg = request.form

    print(msg)

    channel_name = msg['user_id'] if msg['channel_name'] == 'directmessage' else "#" + msg['channel_name']

    print(channel_name)

    # send channel a message
    channel_msg = slack_client.api_call (
        "chat.postMessage",
        channel="#" + channel_name,
        text=request.form.get('text')
    )

    return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
    app.run()
