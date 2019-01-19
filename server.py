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
    # info = request.form

    # # get uid of the user
    # im_id = slack_client.api_call(
    #   "im.open",
    #   user=info["user_id"]
    # )["channel"]["id"]

    # # send user a response via DM
    # ownerMsg = slack_client.api_call(
    #   "chat.postMessage",
    #   channel=im_id,
    #   text=commander.getMessage()

    print(request.form)

    # send channel a response
    channel_msg = slack_client.api_call(
      "chat.postMessage",
      channel="#" + info["channel_name"],
      # text=commander.getMessage()
      text=request.form.get('text')
    )

    return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
    app.run()
