#!/usr/bin/env python3
"""
generate_csv.py

Generate import-ready CSVs from a text schedule.

Usage:
    python generate_csv.py SCHEDULE_FILE COMPETITION_NAME COMPETITION_DATE

Example:
    python generate_csv.py "2025 Program Event List.txt" "May Skate" 2025-05-17
"""

import argparse
import pandas as pd
import re
from datetime import datetime

def parse_schedule(file_path, competition_name, competition_date):
    competitions = [{
        'id':   1,
        'name': competition_name,
        'date': competition_date
    }]
    events    = []
    clubs     = {}
    skaters   = {}
    scheduled = []

    next_event_pk    = 1
    current_event_pk = None
    skater_order     = 1
    year = int(competition_date.split('-')[0])

    with open(file_path, 'r') as f:
        lines = [l.rstrip('\n') for l in f]

    for line in lines:
        if line.startswith('#'):
            # Updated regex allows optional "- X" suffix after the rink number
            m = re.match(
                r'#(\d+)\s*-\s*(.*?)\s{2,}Rink\s+(\d+)(?:\s*-\s*[^ ]+)?\s{2,}(.*)',
                line
            )
            if not m:
                continue

            ev_number = int(m.group(1))
            ev_name   = m.group(2).strip()
            rink      = int(m.group(3).strip())

            dt_text = m.group(4).strip()
            if ',' in dt_text:
                dt_text = dt_text.split(',', 1)[1].strip()
            dt_text = re.sub(r'\s+', ' ', dt_text)
            dt = datetime.strptime(f"{dt_text} {year}", '%B %d %I:%M %p %Y')

            event_pk      = next_event_pk
            next_event_pk += 1

            events.append({
                'id':             event_pk,
                'competition_id': 1,
                'eventNumber':    ev_number,
                'name':           ev_name,
                'date':           dt.date(),
                'rink':           rink,
                'time':           dt.time()
            })
            current_event_pk = event_pk
            skater_order     = 1

        else:
            if not line.strip() or current_event_pk is None:
                continue

            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) < 2:
                continue

            full_name = parts[0].strip()
            club_name = parts[1].strip()

            name_parts = full_name.rsplit(' ', 1)
            if len(name_parts) == 2:
                first, last = name_parts
            else:
                first, last = name_parts[0], ''

            key = club_name.lower()
            if key not in clubs:
                clubs[key] = {'id': len(clubs) + 1, 'name': club_name}

            sk_key = f"{first.lower()}.{last.lower()}"
            if sk_key not in skaters:
                skaters[sk_key] = {
                    'id':        len(skaters) + 1,
                    'firstName': first,
                    'lastName':  last,
                    'club_id':   clubs[key]['id']
                }

            scheduled.append({
                'event_id':    current_event_pk,
                'skater_id':   skaters[sk_key]['id'],
                'orderNumber': skater_order
            })
            skater_order += 1

    # Dump CSVs
    pd.DataFrame(competitions).to_csv("competitions.csv",     index=False)
    pd.DataFrame(events).to_csv("events.csv",                 index=False)
    pd.DataFrame(list(clubs.values())).to_csv("clubs.csv",     index=False)
    pd.DataFrame(list(skaters.values())).to_csv("skaters.csv", index=False)
    pd.DataFrame(scheduled).to_csv("scheduled_skaters.csv",   index=False)

    print("Generated CSVs: competitions.csv, events.csv, clubs.csv, skaters.csv, scheduled_skaters.csv")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("schedule_file",    help="Path to the text schedule file.")
    parser.add_argument("competition_name", help="Name of the competition (string).")
    parser.add_argument("competition_date", help="Competition date in YYYY-MM-DD format.")
    args = parser.parse_args()
    parse_schedule(args.schedule_file, args.competition_name, args.competition_date)

if __name__ == "__main__":
    main()
