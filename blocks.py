"""
Slack block templates for output UI.
"""
from datetime import date

def stat_blocks(date: date, name:str, message_text_1: str, message_text_2: str):
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f":chart_with_upwards_trend: DiversaSpot Stats for {name} :chart_with_upwards_trend:"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "text": f"*{date}*",
                    "type": "mrkdwn"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message_text_1
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message_text_2
            }
        }
    ]


def leaderboard_blocks(date: date, message_text: str, current_semester: str):
    return [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": f":trophy:  DiversaSpot Leaderboard for {current_semester} :trophy:"
			}
		},
		{
			"type": "context",
			"elements": [
				{
					"text": f"*{date}*",
					"type": "mrkdwn"
				}
			]
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": message_text
			}
		},
        {
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": "To see your individual stats, type 'diversabot stats'!"
				}
			]
		}
	]

def diversabot_rules():
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "DiversaSpot Official Rules & Regulations"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "It is everyone’s responsability to hold everyone accountable for following the rules! If you see a post that violates any of the following rules and regulations, you should reply ‘diversabot flag’ in the thread. Please use this command in good faith!"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Rule 1:* The person being spotted must be identifiable. Some ambiguity is allowed (i.e their back is turned but we can tell it’s them, half their face is showing, etc), but total ambiguity is not (i.e the image is completely blurry, they’re too small to discern, their back is turned but they could literally be any asian dude with a black hoodie, etc)."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Rule 2:* Spotting multiple DT members in the same group or vicinity counts a 1 spot. Specifically, you cannot get multiple points from spotting the same group."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Rule 3:* You cannot get multiple points for spotting individuals or groups at the same function. For example, you cannot spot a project team meeting at Moffitt and then spot them again an hour later. As another example, if you’re hanging out with DT member(s), you cannot spot them more than once just because you moved locations. In cognition that this rule is subjective and ambiguous, it is recommended to post a spot anyways if you’re unsure whether it violates this rule."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Rule 4:* In the case of a spotting duel where two (or more) people are attempting to spot one another, the winner is the first person to successfully post their spot in the slack channel, and everyone else’s spots do not count."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Rule 5:* The project team with the most combined DiversaSpot will be rewarded with bountiful prizes."
            }
        }
    ]
