# Used to migrate aliases from prior to v1.16.0
# usage: $ python3 migration/v01.16.00-aliases.py ~/.bitbot/bot.db

import argparse
parser = argparse.ArgumentParser(description="Migrate pre-v1.16.0 aliases")
parser.add_argument("database")
args = parser.parse_args()

import json, sqlite3
database = sqlite3.connect(args.database)

cursor = database.cursor()
<<<<<<< HEAD
cursor.execute("""SELECT server_id, value FROM server_settings
=======
cursor.execute(
    """SELECT server_id, value FROM server_settings
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
       WHERE setting='command-aliases'""")
results = cursor.fetchall()

cursor.execute("SELECT server_id, alias FROM servers")
servers = dict(cursor.fetchall())

for server_id, value in results:
    aliases = json.loads(value)
    for alias, command in aliases.items():
<<<<<<< HEAD
        print("[%s] Migrating '%s' ('%s')" % (servers[server_id], alias, command))
        cursor.execute("INSERT INTO server_settings VALUES (?, ?, ?)",
                       [server_id,
                        "command-alias-%s" % alias,
                        json.dumps(command)])
=======
        print("[%s] Migrating '%s' ('%s')" %
            (servers[server_id], alias, command))
        cursor.execute("INSERT INTO server_settings VALUES (?, ?, ?)",
            [server_id, "command-alias-%s" % alias, json.dumps(command)])
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
database.commit()
database.close()

print()
print("Migration successful!")
