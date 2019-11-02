import datetime
import re

from typing import List, Tuple
from atudomain.git.Commit import Commit


class GitLogParser:
    @staticmethod
    def _process_date_line(
            date_line: str
    ) -> Tuple[str, str, datetime.datetime]:
        name = re.search(r'(.*)\s<', date_line).group(1)
        email = re.search(r'<(.*)>', date_line).group(1)
        date_source = re.search(r'>\s(.*)', date_line).group(1)
        timestamp, timezone = date_source.split(' ')
        date = datetime.datetime.fromtimestamp(
            int(timestamp),
            tz=datetime.timezone.utc
        )
        return name, email, date

    def parse_commits(
            self,
            raw_log_string: str
    ) -> List[Commit]:
        commits = list()
        for commit_string in re.split(
                r'\n(?=commit\s)',
                raw_log_string
        ):
            commit_id = re.findall(
                r'(?:^|\n)commit (\w+)',
                commit_string
            )[0]

            tree = re.findall(
                r'\ntree (\w+)',
                commit_string
            )[0]

            parents = list(
                re.findall(
                    r'\nparent (\w+)',
                    commit_string
                )
            )

            is_merge = True if len(parents) > 1 else False

            author_line = re.findall(
                r'\nauthor (.*)',
                commit_string
            )[0]

            author, author_email, author_date = self._process_date_line(
                date_line=author_line
            )

            committer_line = re.findall(
                r'\ncommitter (.*)',
                commit_string
            )[0]

            committer, committer_email, committer_date = self._process_date_line(
                date_line=committer_line
            )

            message_lines = [re.sub(r'^\s{4}', '', x) for x in commit_string.split('\n') if re.search(r'^\s{4}', x)]
            message = '\n'.join(message_lines)
            message = message.strip()

            message_subject, message_body = [x.lstrip() for x in message.split('\n', 1)]

            commit = Commit(
                is_merge=is_merge,
                commit_id=commit_id,
                tree=tree,
                parents=parents,
                author=author,
                author_email=author_email,
                author_date=author_date,
                committer=committer,
                committer_email=committer_email,
                committer_date=committer_date,
                message=message,
                message_subject=message_subject,
                message_body=message_body
            )
            commits.append(commit)
        return commits
