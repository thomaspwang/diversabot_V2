"""
Miscellaneous utility functions.
"""

import random
import re
import requests
import os
from typing import Iterator

import boto3
from slack_bolt import App
import sqlalchemy
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from models import DiversaSpot

def get_num_spots_for_user_id(
    user_id: str,
    curr_semester: str,
    engine: sqlalchemy.Engine,
) -> int:
    """Returns the number of spots a user has"""
    with Session(engine) as session:
        return session.query(DiversaSpot) \
            .filter_by(spotter=user_id, semester=curr_semester, flagged=False) \
            .count()
    
def iter_leaderboard(
    curr_semester: str,
    engine: sqlalchemy.Engine,
    *,
    limit=None
) -> Iterator[tuple[int, str, int]]:
    """Returns an ordered iterator that yields the form (rank, user_id, num_spots)
    
    Ordered by num_spots (and trivially rank) in descending order. Only returns the top `limit` users.

    If limit=None, returns all users.
    """
    leaderboard: list[tuple[str, int]]
    with Session(engine) as session:
        leaderboard = session.query(DiversaSpot.spotter, sqlalchemy.func.count(DiversaSpot.spotter)) \
                        .filter(DiversaSpot.semester == curr_semester) \
                        .filter(DiversaSpot.flagged != True) \
                        .group_by(DiversaSpot.spotter) \
                        .order_by(sqlalchemy.func.count(DiversaSpot.spotter).desc()) \
                        .all()
    rank = 1
    for user_id, num_spots in leaderboard:
        yield (rank, user_id, num_spots)
        rank += 1
        if limit and rank > limit:
            return

def find_rank_by_user_id(user_id: str, curr_semester: str, engine: sqlalchemy.Engine) -> int:
    """Returns the rank of a user by their user_id"""
    for rank, user_id_, _ in iter_leaderboard(curr_semester, engine):
        if user_id == user_id_:
            return rank

def find_all_mentions(msg: str) -> list[str]:
    """Returns all user_ids mentioned in msg"""
    member_ids = re.findall(r'<@([\w]+)>', msg, re.MULTILINE)
    return member_ids

def get_name_from_user_id(user_id : str, slack_app: App):
    """ Gets name from user id."""
    return slack_app.client.users_info(user=user_id)['user']['real_name']


def random_excited_greeting() -> str:
    """Returns a random excited greeting"""
    greetings = [
        "Hey",
        "Hi",
        "What's schlaying",
        "What's poppin'",
        "Greetings",
        "DiversaHi",
        "Attention",
        "DiversaSLAY",
        "Howdy"
    ]
    return random.choice(greetings)

def random_disappointed_greeting() -> str:
    """Returns a random disappointed greeting"""
    greetings = [
        "Oh no",
        "Whoops",
        "Stupid",
    ]
    return random.choice(greetings)
