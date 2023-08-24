"""
Entry point executable for the Slack bot.

Before running:
    1. a .env file must be created in the root directory of the project
    and must contain the correct credentials.

    2. run ./setup.sh to set up the virtual environment, install requirements, 
    and set up the database. You only need to do this once.

To run:
    python app.py (with the virtual environment activated)

    diversavenv/bin/python app.py (without the virtual environment activated)
"""

from __future__ import annotations

import logging
from datetime import date
import os
import requests

import boto3
from dotenv import load_dotenv
from slack_bolt import App, BoltResponse
from slack_bolt.error import BoltUnhandledRequestError
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from urllib.parse import urlparse

from models import DiversaSpot
from blocks import (
    leaderboard_blocks,
    diversabot_rules,
    stat_blocks
)
from utils import (
    find_all_mentions, 
    random_excited_greeting, 
    random_disappointed_greeting,
    get_num_spots_for_user_id,
    get_name_from_user_id,
    iter_leaderboard,
    find_rank_by_user_id
)

S3_BUCKET_URL = "https://diversaspots.s3.us-west-1.amazonaws.com/"
DIVERSABOT_SLACK_ID = "U05GDL7EXJ7"
CURRENT_SEMESTER = "Fall 2023"

logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv('.env')

# Slack client initialization
app = App(
    token=os.environ.get('SLACK_BOT_TOKEN'),
    signing_secret=os.environ.get('SLACK_SIGNING_SECRET'),
    raise_error_for_unhandled_request=True,
)

# DB initialization
engine = sqlalchemy.create_engine(os.environ.get('DATABASE_URL').replace("postgresql://", "cockroachdb://"))

# Initialize S3 Bucket
s3_client = boto3.client('s3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')
)

@app.message("ping")
def message_pong(message, client):
    """ Ping. Pong. """
    channel_id = message['channel']
    client.chat_postMessage(channel=channel_id, text="pong")


# @app.error
# def handle_errors(error, body, logger):
#     """ Handles errors that occur during request servicing. """
#     if isinstance(error, BoltUnhandledRequestError):
#         logger.info(f"Unhandled request for {body}")
#         return BoltResponse(status=200, body="")
#     else:
#         logger.error(f"Error: {error}")
#         raise error

@app.event({
    "type" : "message",
    "subtype" : "file_share"
})
def record_spot(message, client, logger):
    """ Records a DiversaSpot. """
    user = message["user"]
    message_ts = message["ts"]
    channel_id = message["channel"]
    text: str = message["text"]
    tagged_users: list[str] = find_all_mentions(text)
    
    if len(tagged_users) == 0:
        logger.info(f"User {user} did not tag anyone in their DiversaSpot.")
        reply = f"{random_disappointed_greeting()} <@{user}>, this DiversaSpot doesn't count " + \
                "because you didn't mention anyone! Delete and try again."
        
    elif (filetype := message['files'][0]['filetype']) != 'jpg' and filetype != 'png' and filetype != 'heic':
        logger.info(f"User {user} did not attach a JPG, HEIC, or a PNG file.")
        reply = f"{random_disappointed_greeting()} <@{user}>, This DiversaSpot doesn't count because you " + \
                "didn't attach a JPG, HEIC, or a PNG file! Delete and try again."
        
    else:
        logger.info(f"Recording DiversaSpot from user {user} at timestamp {message_ts}.")

        # Creating new image file name for S3 bucket.
        # Format: <user_id>_<timestamp>.<filetype>
        image_url = message['files'][0]['url_private']
        path = urlparse(image_url).path
        image_ext = os.path.splitext(path)[1] # e.g .jpg
        new_s3_file_name = f"{user}_{message_ts}{image_ext}"

        # Extracting image data from Slack URL and uploading it into S3 bucket.
        resp = requests.get(image_url, headers={"Authorization" : f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"})
        s3_client.put_object(Bucket='diversaspots', Body=resp.content, Key=new_s3_file_name)
        s3_image_url = S3_BUCKET_URL + new_s3_file_name

        # Inserting DiversaSpot into DB.    
        with Session(engine) as session:
            new_diversaspot = DiversaSpot(
                timestamp=message_ts,
                spotter=user,
                tagged=tagged_users,
                image_url=s3_image_url,
                flagged=False,
            )
            with session.begin():
                session.add(new_diversaspot)

        # Sending confirmation message.
        num_spots = get_num_spots_for_user_id(user, engine)
        reply = f"{random_excited_greeting()} <@{user}>, you now have {num_spots} DiversaSpots!"

    client.chat_postMessage(
        channel=channel_id,
        thread_ts=message_ts,
        text=reply
    )

@app.message("diversabot leaderboard")
def post_leaderboard(message, client):
    """ Outputs leaderboard for the current semester."""
    channel_id = message["channel"]

    message_text = ""
    for rank, user_id, num_spots in iter_leaderboard(engine, limit=10):
        name = get_name_from_user_id(user_id, app)
        message_text += f"*#{rank}: {name}* with {num_spots} spots \n"

    blocks = leaderboard_blocks(date.today(), message_text, CURRENT_SEMESTER)

    client.chat_postMessage(
        channel=channel_id,
        blocks=blocks,
        text="Displaying leaderboard information."

    )

@app.message("diversabot flag")
def flag_spot(message, client, logger):
    flagger = message['user']
    channel_id = message["channel"]
    reply: str

    if 'thread_ts' not in message:
        logger.info(f"User {flagger} attempted to flag a spot without replying in a thread.")
        reply = f"{random_disappointed_greeting()} <@{flagger}>, to flag a spot, " + \
            "you have to reply 'diversaspot flag' in the thread of the spot that you'd like to flag."
        message_ts = message['ts']

    # User is flagging a thread
    else:
        message_ts = message['thread_ts'] # Should be threaded under the original DiversaSpot.

        with Session(engine) as session:
            try:
                diversaspot = session.query(DiversaSpot).filter_by(timestamp=message_ts).one()
            except NoResultFound:
                logger.info(*f"User {flagger} attempted to flag a spot that doesn't exist.")
                reply = f"{random_disappointed_greeting()} <@{flagger}>, this is not a valid DiversaSpot to flag!"
            except MultipleResultsFound:
                logger.error(f"Multiple DiversaSpots found with timestamp {message_ts}.")
                reply = "Critical error occured. Muiltiple DiversaSpots found with the same timestamp. " + \
                        "Please contact the DiversaBot team."

            if diversaspot.flagged == True:
                logger.info(f"User {flagger} attempted to flag a spot that was already flagged.")
                reply = f"{random_disappointed_greeting()} <@{flagger}>, this DiversaSpot has already been flagged!"
            else:
                # Valid diversaspot to flag. Commit the operation.
                diversaspot.flagged = True
                session.commit()

            reply = f"{random_disappointed_greeting()} <@{diversaspot.spotter}>, this spot has been flagged by <@{flagger}> as they believe it is in violation of the official DiversaSpotting rules and regulations. If you would like to review the official DiversaSpotting rules and regulations, you can type 'diversabot rules'. If you would like to dispute this flag, please @ Thomas Wang or Clara Tu in this thread with a relevant explanation."


    client.chat_postMessage(
        channel=channel_id,
        thread_ts=message_ts,
        text=reply
    )

@app.message("diversabot rules")
def post_rules(message, client):
    """"""
    channel_id = message["channel"]
    blocks = diversabot_rules()
    client.chat_postMessage(
        channel=channel_id,
        blocks=blocks
    )

@app.message("diversabot stats")
def post_stats(message, client):
    user_id = message["user"]
    channel_id = message["channel"]

    message_text_1: str
    message_text_2: str

    if (num_spots := get_num_spots_for_user_id(user_id, engine)) == 0:
        message_text_1 = f"You have not spotted anyone yet :( Go get out there!"
    else:
        rank = find_rank_by_user_id(user_id, engine)
        message_text_1 = f"You have spotted {num_spots} people and are currently ranked #{rank} on the leaderboard!"

    with Session(engine) as session:
        times_spotted = session.query(DiversaSpot) \
                       .filter(DiversaSpot.tagged.any(user_id), DiversaSpot.flagged==False) \
                       .count()
        
        if times_spotted == 0:
             message_text_2 = ":camera_with_flash: No one has spotted you yet ... so sneaky of you!"
        else:
            top_spotter_id, top_spotter_num_spots = session.query(
                            DiversaSpot.spotter, 
                            sqlalchemy.func.count(DiversaSpot.spotter).label('spot_count')
                        ) \
                        .filter(DiversaSpot.tagged.any(user_id), DiversaSpot.flagged==False) \
                        .group_by(DiversaSpot.spotter) \
                        .order_by(sqlalchemy.desc('spot_count')) \
                        .first()
            message_text_2 = f":camera_with_flash: You've been spotted a total of {num_spots} " + \
            f"times!\n\n:heart_eyes: *{get_name_from_user_id(top_spotter_id, app)}* has spotted you " + \
            f"the most with {top_spotter_num_spots} spots."
    
    blocks = stat_blocks(date.today(), get_name_from_user_id(user_id, app), message_text_1, message_text_2)
    
    client.chat_postMessage(
        channel=channel_id,
        blocks=blocks,
        text="Posting personal stat information."
    )

# TODO: diversabot team leaderboard
# TODO: diversabot miss
# TODO: diversabot help (can copy and paste technically)
# TODO: diversabot recap (automatic and not an action) — recap with who spotted the most that week, who was the most spotted, and like 3-5 pics of most reacted to spots (need to implement a count reacts)
# TODO: diversabot unflag (only allowed by me or tommy)
# TODO: diversabot chum - for the chumming channel to count into diversaspots?


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))