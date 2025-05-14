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
    # 1) Prepare containers for CSVs
    competitions = [{
        'id':   1,
        'name': competition_name,
        'date': competition_date
    }]
    events    = []
    clubs     = {}
    skaters   = {}
    scheduled = []

    # 2) Counters and state
    next_event_pk    = 1
    current_event_pk = None
    skater_order     = 1

    # Extract year from competition_date to avoid ambiguity
    year = int(competition_date.split('-')[0])

    # 3) Read lines from the schedule text file
    with open(file_path, 'r') as f:
        lines = [l.rstrip('\n') for l in f]

    for line in lines:
        if line.startswith('#'):
            # Match headers of the form:
            # #231 - Event Name  [2+ spaces] Rink 2 - L  [2+ spaces] May 17 08:00 AM
            m = re.match(
                r'#(\d+)\s*-\s*(.*?)\s{2,}Rink\s+(\d+)(?:\s*-\s*([LZ]))?\s{2,}(.*)',
                line
            )
            if not m:
                continue

            ev_number = int(m.group(1))
            ev_name   = m.group(2).strip()
            rink      = int(m.group(3).strip())
            suffix    = m.group(4)        # 'L', 'Z', or None
            dt_text   = m.group(5).strip()

            # Strip any weekday prefix, normalize spaces
            if ',' in dt_text:
                dt_text = dt_text.split(',', 1)[1].strip()
            dt_text = re.sub(r'\s+', ' ', dt_text)
            # Parse with appended year
            dt = datetime.strptime(f"{dt_text} {year}", '%B %d %I:%M %p %Y')

            # Map suffix to enterAt
            if suffix == 'L':
                enterAt = 'Lobby'
            elif suffix == 'Z':
                enterAt = 'Zamboni'
            else:
                enterAt = ''

            # Assign unique CSV PK
            event_pk      = next_event_pk
            next_event_pk += 1

            events.append({
                'id':             event_pk,
                'competition_id': 1,
                'eventNumber':    ev_number,
                'name':           ev_name,
                'date':           dt.date(),
                'rink':           rink,
                'time':           dt.time(),
                'enterAt':        enterAt,
            })
            current_event_pk = event_pk
            skater_order     = 1

        else:
            # Skip blank or non-indented lines
            if not line.strip() or current_event_pk is None:
                continue

            # Split skater lines on two or more spaces: "First Last  Club Name"
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) < 2:
                continue

            full_name = parts[0].strip()
            club_name = parts[1].strip()

            # Split full_name into first/last
            name_parts = full_name.rsplit(' ', 1)
            if len(name_parts) == 2:
                first, last = name_parts
            else:
                first = name_parts[0]
                last  = ''

            
            # Register club (extract country if in parentheses)
            key = club_name.lower()
            if key not in clubs:
                # Detect a "(Country)" suffix
                country = ''
                name = club_name
                # match literal parentheses around the country
                m = re.search(r'\(([^)]+)\)\s*$', club_name)
                if m:
                    raw = m.group(1).strip().upper()
                    # Map "CANADA" → "CA", else take first two letters
                    country = 'CA' if raw == 'CANADA' else 'US'
                    # Remove the parentheses part from the name
                    if country == 'CA':
                        name = re.sub(r'\s*\([^)]+\)\s*$', '', club_name).strip()

                clubs[key] = {
                    'id': len(clubs) + 1,
                    'name': name,
                    'country': country
                }

            # Register skater
            sk_key = f"{first.lower()}.{last.lower()}"
            if sk_key not in skaters:
                skaters[sk_key] = {
                    'id':        len(skaters) + 1,
                    'firstName': first,
                    'lastName':  last,
                    'club_id':   clubs[key]['id']
                }

            # Add ScheduledSkater entry
            scheduled.append({
                'event_id':    current_event_pk,
                'skater_id':   skaters[sk_key]['id'],
                'orderNumber': skater_order
            })
            skater_order += 1

    # 4) Build and write DataFrames
    pd.DataFrame(competitions).to_csv("competitions.csv", index=False)
    pd.DataFrame(events).to_csv(
        "events.csv", index=False,
        columns=['id','competition_id','eventNumber','name','date','rink','time','enterAt']
    )

    # Write clubs.csv with the new country column
    pd.DataFrame(list(clubs.values())).to_csv("clubs.csv",index=False,columns=['id','name','country'])
    pd.DataFrame(list(skaters.values())).to_csv("skaters.csv", index=False)
    pd.DataFrame(scheduled).to_csv("scheduled_skaters.csv", index=False)

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
