from datetime import datetime
from fastapi import UploadFile

from app.module.parser import Parser
from app.module.merger import Merger
from app.util import to_snake, to_percentages


class Analyser:
    def __init__(self, file: UploadFile):
        self.file = file

    async def analyse(self):
        content = await self.file.read()
        data = self.process(content)
        sorted_users = self.sort_users(data)

        for index, (_, item) in enumerate(sorted_users):
            item["leaderboard"] = index + 1

        return {
            "messages": data["total_messages"],
            "images": self.parser.images_sent,
            "videos": self.parser.videos_sent,
            "gifs": self.parser.gifs_sent,
            "polls": self.parser.polls_sent,
            "voice_notes": self.parser.voicenotes_sent,
            "member_count": len(data["users"]),
            "members": dict(sorted_users),
        }

    def process(self, content):
        parser = Parser(content)
        (
            messages,
            log,
            joined_at,
            user_media_counts,
        ) = parser.parse()
        self.parser = parser

        total_messages = sum(
            messages[user] + sum(user_media_counts[user].values()) for user in messages
        )

        print(len(parser.lines))
        print(total_messages)

        merger = Merger(messages, log, joined_at)
        merged_accounts, merged_log, merged_joined = merger.merge()

        percentages = to_percentages(
            {
                user: messages[user] + sum(user_media_counts[user].values())
                for user in messages
            },
            total_messages,
        )
        users = self.get_user_data(
            merged_accounts,
            merged_log,
            merged_joined,
            percentages,
            user_media_counts,
        )

        print(f"Total Lines to Match 🔤: {len(parser.lines)}")
        print(f"Total Lines Matched ✅: {total_messages}")
        print(f"Total Lines NOT Matched ❌: {parser.unmatched_line_count}")

        print(f"Total Images Sent 📷: {parser.images_sent}")
        print(f"Total Videos Sent 🎥: {parser.videos_sent}")
        print(f"Total GIFs Sent 🎞️: {parser.gifs_sent}")
        print(f"Total Polls Sent 📊: {parser.polls_sent}")
        print(f"Total Voicenotes Sent 🎤: {parser.voicenotes_sent}")
        print(
            f"Total Media Sent 🤳🏼: {parser.images_sent + parser.videos_sent + parser.gifs_sent + parser.voicenotes_sent}"
        )

        return {"users": users, "total_messages": total_messages}

    def get_user_data(
        self,
        merged_accounts,
        merged_activity_log,
        merged_joined_at,
        percentages,
        user_media_counts,
    ):
        users = {}

        for name, messages in merged_accounts.items():
            join_date, days_in_chat = self.get_duration_history(
                name, merged_activity_log, merged_joined_at
            )
            messages_per_day = self.get_messages_per_day(messages, days_in_chat)

            total_messages = messages + sum(user_media_counts[name].values())

            user_snake_name = to_snake(name)
            users[user_snake_name] = {
                "messages": total_messages,
                "messages_per_day": round(messages_per_day, 2),
                "percentage_share": percentages.get(name, 0),
                "joined_chat": join_date,
                "days_in_chat": days_in_chat,
                "activity_log": merged_activity_log.get(name, []),
                "left_or_removed": self.get_left_or_removed(
                    merged_activity_log.get(name, [])
                ),
                "images_sent": user_media_counts[name]["images_sent"],
                "videos_sent": user_media_counts[name]["videos_sent"],
                "gifs_sent": user_media_counts[name]["gifs_sent"],
                "polls_sent": user_media_counts[name]["polls_sent"],
                "voicenotes_sent": user_media_counts[name]["voicenotes_sent"],
            }

        return users

    def get_duration_history(self, name, merged_activity_log, merged_joined_at):
        join_date = self.get_joined_date(merged_activity_log.get(name, []))
        if not join_date:
            join_date = merged_joined_at.get(name, "Unknown")

        if isinstance(join_date, datetime):
            days_in_chat = (datetime.now() - join_date).days
            join_date = join_date.strftime("%m/%d/%Y %I:%M:%S %p")
        else:
            days_in_chat = "Unknown"

        return join_date, days_in_chat

    def get_joined_date(self, joined_log):
        if isinstance(joined_log, list):
            for entry in joined_log:
                if "Created chat on" in entry:
                    date_str = entry.split("Created chat on ")[1]
                    return datetime.strptime(date_str, "%m/%d/%Y %I:%M:%S %p")
        elif "Created chat on" in joined_log:
            date_str = joined_log.split("Created chat on ")[1]
            return datetime.strptime(date_str, "%m/%d/%Y %I:%M:%S %p")
        return None

    def get_messages_per_day(self, messages, days_in_chat):
        return (
            messages / days_in_chat
            if isinstance(days_in_chat, int) and days_in_chat > 0
            else 0
        )

    def get_left_or_removed(self, joined_log):
        return len(joined_log) - 1 if isinstance(joined_log, list) else 0

    def sort_users(self, user_data):
        return sorted(
            user_data["users"].items(),
            key=lambda item: item[1]["messages_per_day"],
            reverse=True,
        )
