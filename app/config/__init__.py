# This is an example, the configuration of your group chat on WhatsApp

GROUP_NAME = "Chat Name"

CREATOR = ""
CREATED_DATE = "01/01/1970"
CREATED_TIME = "00:00:00"
CREATED_PERIOD = "AM"
CREATED_AT = f"{CREATED_DATE} {CREATED_TIME} {CREATED_PERIOD}"
CREATED_DESC = f"Created chat on {CREATED_AT}"

USER = "Someone 001"
DATA_UPLOADER = "\u200eYou"
LEFT_CHAT = ["Someone 002"]
ANOMALIES = ["Someone 003"]
EXCLUDED = [GROUP_NAME, DATA_UPLOADER] + LEFT_CHAT

ADDED_PLACEHOLDER = f"Added by {CREATOR} on or before {CREATED_DATE}"
JOINED_VIA_LINK = "joined using this group's invite link"

ACCOUNT_MAPPING = {
    "Someone 001": ["Someone 001.1", "Someone 001.2"],
    "Someone 002": ["Someone 002.1", "Someone 002.2"],
    "Someone 003": ["Someone 003.1", "Someone 003.2"],
}

REGEX = {
    "CHAT_LINE": r"\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}:\d{2})\s?([APM]*)\] (.*?):",
    "CHAT_USER_ADDED": r"([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*) added ([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)",
    "CHAT_USER_WAS_ADDED": r"([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*) was added",
    "JOINED_VIA_LINK": rf"([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*) {JOINED_VIA_LINK}",
}
