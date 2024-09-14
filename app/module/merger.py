from collections import defaultdict
from app.config import ACCOUNT_MAPPING, EXCLUDED


class Merger:
    def __init__(self, messages, activity_log, joined_at):
        self.messages = messages
        self.activity_log = activity_log
        self.joined_at = joined_at
        self.merged_messages = defaultdict(int)
        self.merged_activity_log = defaultdict(list)
        self.merged_joined_at = {}

    def merge(self):
        self.merge_accounts()
        self.merge_members()
        self.exclude_items()

        return self.merged_messages, self.merged_activity_log, self.merged_joined_at

    def merge_accounts(self):
        for name, aliases in ACCOUNT_MAPPING.items():
            self.merge_messages(name, aliases)
            self.merge_activity_logs(name, aliases)
            self.merge_join_dates(name, aliases)

    def merge_messages(self, name, aliases):
        total_messages = self.messages.get(name, 0) + sum(
            self.messages.get(alias, 0) for alias in aliases
        )
        if total_messages > 0:
            self.merged_messages[name] = total_messages

    def merge_activity_logs(self, name, aliases):
        logs = self.get_combined_logs(name, aliases)
        self.merged_activity_log[name] = logs

    def merge_join_dates(self, name, aliases):
        dates = [self.joined_at.get(name)] if name in self.joined_at else []
        for alias in aliases:
            if alias in self.joined_at:
                dates.append(self.joined_at[alias])
        if dates:
            self.merged_joined_at[name] = min(dates)

    def merge_members(self):
        for member in self.messages:
            if member not in ACCOUNT_MAPPING and all(
                member not in aliases for aliases in ACCOUNT_MAPPING.values()
            ):
                self.merged_messages[member] = self.messages[member]
                if member in self.activity_log:
                    self.merged_activity_log[member] = self.get_logs(member)
                if member in self.joined_at:
                    self.merged_joined_at[member] = self.joined_at[member]

    def exclude_items(self):
        for item in EXCLUDED:
            self.merged_messages.pop(item, None)

    def get_combined_logs(self, name, aliases):
        logs = self.get_logs(name)
        for alias in aliases:
            alias_logs = self.get_logs(alias)
            logs += alias_logs
        return logs

    def get_logs(self, name):
        logs = self.activity_log.get(name, [])
        if isinstance(logs, str):
            logs = [logs]
        return logs
