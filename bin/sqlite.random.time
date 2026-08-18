#!/usr/bin/python3
from library.utils import arggroups, argparse_utils, printing, db_utils

GROUP_SQL_TEMPLATES = {
    "hour": "strftime('%Y-%m-%d %H', datetime({column}, 'unixepoch'))",
    "day": "strftime('%Y-%m-%d', datetime({column}, 'unixepoch'))",
    "week": "strftime('%Y-%W', datetime({column}, 'unixepoch'))",
    "month": "strftime('%Y-%m', datetime({column}, 'unixepoch'))",
    "year": "strftime('%Y', datetime({column}, 'unixepoch'))",
}


def main():
    parser = argparse_utils.ArgumentParser(description="Query a SQLite database with grouping options.")
    arggroups.debug(parser)
    arggroups.database(parser)
    parser.add_argument("table_name", help="Name of the table to query.")
    parser.add_argument(
        "column", choices=["time_created", "time_modified", "time_uploaded"], help="Column to group by."
    )
    parser.add_argument(
        "group_by", choices=["hour", "day", "week", "month", "year"], help="Group by hour, day, week, month, or year."
    )
    args = parser.parse_args()
    db = db_utils.connect(args)

    group_sql = GROUP_SQL_TEMPLATES[args.group_by].format(column=args.column)
    query = f"""
    SELECT * FROM {args.table_name}
    WHERE {group_sql} = (
        SELECT {group_sql} FROM {args.table_name}
        ORDER BY RANDOM()
        LIMIT 1
    )
    """
    printing.table(list(db.query(query)))


if __name__ == "__main__":
    main()
