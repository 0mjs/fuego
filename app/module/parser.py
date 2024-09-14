from re import compile
from collections import defaultdict
from datetime import datetime

from app.config import (
    ANOMALIES,
    CREATED_AT,
    CREATED_DESC,
    CREATOR,
    ADDED_PLACEHOLDER,
    USER,
    JOINED_VIA_LINK,
    REGEX,
)


class Parser:
    def __init__(self, content):
        self.lines = self.to_lines(content)
        self.messages = defaultdict(int)
        self.join_dates = defaultdict(list)
        self.log = defaultdict(list, {CREATOR: [CREATED_DESC]})
        self.user_media_counts = defaultdict(lambda: defaultdict(int))
        self.unmatched_line_count = 0
        self.images_sent = 0
        self.videos_sent = 0
        self.gifs_sent = 0
        self.polls_sent = 0
        self.voicenotes_sent = 0
        self.nomad_lines = []
        self.p_message, self.p_user_added, self.p_user_added_alt = self.line_patterns()

    def parse(self):
        self.parse_lines()
        self.add_log_placeholders()
        joined_at = self.get_join_dates()

        return self.messages, self.log, joined_at, self.user_media_counts

    def parse_lines(self):
        buffer = ""
        current_user = None
        for line in self.lines:
            if "image omitted" in line:
                self.images_sent += 1
                if current_user:
                    self.user_media_counts[current_user]["images_sent"] += 1
                continue
            if "video omitted" in line:
                self.videos_sent += 1
                if current_user:
                    self.user_media_counts[current_user]["videos_sent"] += 1
                continue
            if "GIF omitted" in line:
                self.gifs_sent += 1
                if current_user:
                    self.user_media_counts[current_user]["gifs_sent"] += 1
                continue
            if "POLL:" in line:
                self.polls_sent += 1
                if current_user:
                    self.user_media_counts[current_user]["polls_sent"] += 1
                continue
            if "audio omitted" in line:
                self.voicenotes_sent += 1
                if current_user:
                    self.user_media_counts[current_user]["voicenotes_sent"] += 1
                continue

            if match := self.p_message.match(line):
                if buffer:
                    buffer = buffer.strip()
                    self.process_message(buffer, current_user)
                    buffer = ""
                buffer = line
                current_user = match.group(4).split(": ")[-1]
            else:
                buffer += f" {line}"

        if buffer:
            self.process_message(buffer.strip(), current_user)

    def process_message(self, message, current_user):
        match = self.p_message.match(message)
        if match:
            user, date, time = (
                match.group(4).split(": ")[-1],
                match.group(1),
                match.group(2),
            )
            message_text = message[match.end() :].strip()
            dt = datetime.strptime(f"{date} {time}", "%m/%d/%y %H:%M:%S")

            self.parse_user_added(message_text, date, time, dt)
            self.parse_user_link(message_text, date, time, dt)

            self.messages[user] += 1
        else:
            self.unmatched_line_count += 1

    def to_lines(self, content):
        lines = content.decode("utf-8").splitlines()
        return lines

    def line_patterns(self):
        p_message = compile(REGEX["CHAT_LINE"])
        p_user_added = compile(REGEX["CHAT_USER_ADDED"])
        p_user_added_alt = compile(REGEX["CHAT_USER_WAS_ADDED"])

        return p_message, p_user_added, p_user_added_alt

    def parse_user_added(self, message, date, time, dt):
        if added_match := self.p_user_added.search(message):
            adder, addee = added_match.group(1), added_match.group(2)
            self.log[addee].append(
                f"Added by {USER if adder == 'You' else adder} on {date} {time}"
            )
            self.join_dates[addee].append(dt)
        if was_added_match := self.p_user_added_alt.search(message):
            addee = was_added_match.group(1)
            self.log[addee].append(f"Added by {USER} on {date} {time}")
            self.join_dates[addee].append(dt)

    def parse_user_link(self, message, date, time, dt):
        if JOINED_VIA_LINK in message:
            if join_match := compile(REGEX["JOINED_VIA_LINK"]).search(message):
                joined_name = join_match.group(1)
                self.log[joined_name].append(f"Joined via link on {date} {time}")
                self.join_dates[joined_name].append(dt)

    def add_log_placeholders(self):
        for user in self.messages:
            if user not in self.log or any(name in user for name in ANOMALIES):
                self.log[user].insert(0, ADDED_PLACEHOLDER)
                self.join_dates[user].append(
                    datetime.strptime(CREATED_AT, "%m/%d/%Y %I:%M:%S %p")
                )

    def get_join_dates(self):
        return {user: min(dates) for user, dates in self.join_dates.items()}


REGEX = {
    "CHAT_LINE": r"\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}:\d{2})\s?([APM]*)\] (.*?):",
    "CHAT_USER_ADDED": r"([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*) added ([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)",
    "CHAT_USER_WAS_ADDED": r"([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*) was added",
    "JOINED_VIA_LINK": rf"([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*) {JOINED_VIA_LINK}",
}
