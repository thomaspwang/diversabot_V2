"""
Object mappings for the DB.
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ARRAY

Base = declarative_base()

class DiversaSpot(Base):
    """The DiversaSpot class corresponds to a record to the `diversaspots` table in the DB.
    """
    __tablename__ = 'diversaspots'
    
    # Unique (per-channel) timestamp that Slack assigns to each message.
    timestamp = Column(String, primary_key=True)

    # Unique ID of the poster of the DiversaSpot. Assigned by Slack.
    spotter = Column(String)

    # List of the unique IDs of the tagged users in the DiversaSpot.
    tagged = Column(ARRAY(String))

    # Image URL of the DiversaSpot. Should be of format: <user_id>_<timestamp>.<filetype>
    image_url = Column(String)

    # Denotes whether or an ot this DiversaSpot is flagged
    flagged = Column(Boolean)

    # The semester in which the spot happened
    semester = Column(String)
    
    def __str__(self):
        return f"DiversaSpot(timestamp={self.timestamp}, spotter={self.spotter}, tagged={self.tagged}, image_url={self.image_url}, flagged={self.flagged})"