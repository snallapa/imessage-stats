import sqlite3, sys
from contacts import searchByPhone 
path = sys.argv[1]
conn = sqlite3.connect(path)
c = conn.cursor()
threads = {}
handle_idToid = {0: "+15083530126"}
chats = {}
messageToChat = {}
for row in c.execute('SELECT rowid,id  FROM handle'):
    handle_id, number = row
    handle_idToid[handle_id] = number
    threads[number] = 0
for row in c.execute('SELECT * from chat_handle_join'):
    chat_id, handle_id = row
    chats[chat_id] = chats.get(chat_id, []) + [{'handle_id': handle_id, 'number': handle_idToid[handle_id], 'count': 0}]
for key, value in chats.items():
    value.append({'handle_id': 0, 'number': handle_idToid[0], 'count': 0})
for row in c.execute("SELECT * from chat_message_join"):
    chat_id, message_row, _, = row
    messageToChat[message_row] = chat_id
for row in c.execute("SELECT ROWID, handle_id, is_from_me from message"):
    rowid, handle_id,is_from_me, = row
    threads[handle_idToid[handle_id]] = threads.get(handle_idToid[handle_id], 0) + 1
    if rowid not in messageToChat:
        continue
    chat_id = messageToChat[rowid]
    if is_from_me == 1:
        chats[chat_id][-1]['count'] = chats[chat_id][-1]['count'] + 1
    else:
        for handler in chats[chat_id]:
            if handler['handle_id'] == handle_id:
                handler['count'] = handler['count'] + 1
                break
# for i,value in handle_idToid.items():
#       messageCount, = c.execute('SELECT count(*) FROM message where handle_id=?',(i,)).fetchone()
#       threads[value] = messageCount
import json
nameThreads = {}
handle_idToName = {}
for key, value in threads.items():
    lookup = searchByPhone(key[-4:])
    i = 0
    newLookup = lookup
    while newLookup in nameThreads:
        newLookup = lookup + str(i)
    nameThreads[lookup if lookup else key] = value
    if lookup:
        handle_idToName[key] = lookup

for key, value in chats.items():
    for handler in value:
        if handler['number'] in handle_idToName:
            handler['name'] = handle_idToName[handler['number']]
with open('output.json', 'w') as fp:
    json.dump({"threads": nameThreads, "chats": chats}, fp)