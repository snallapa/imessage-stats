import sqlite3, sys
from contacts import searchByPhone 
path = sys.argv[1]
conn = sqlite3.connect(path)
c = conn.cursor()
threads = {}
handle_idToid = {0: "+15083530126"}
chats = {}
messageToChat = {}
messageToAttachment = {}
def getHandleIdToNumber():
    for row in c.execute('SELECT rowid,id FROM handle'):
        handle_id, number = row
        handle_idToid[handle_id] = number
        threads[number] = 0
def getChats():
    for row in c.execute('SELECT * from chat_handle_join'):
        chat_id, handle_id = row
        chats[chat_id] = chats.get(chat_id, []) + [{'handle_id': handle_id, 'number': handle_idToid[handle_id], 'count': 0, 'attachments': []}]
    for key, value in chats.items():
        value.append({'handle_id': 0, 'number': handle_idToid[0], 'count': 0, "attachments" : []})
def getMessageToChats():
    for row in c.execute("SELECT * from chat_message_join"):
        chat_id, message_row, _, = row
        messageToChat[message_row] = chat_id
    c2 = conn.cursor()
    for row in c.execute("SELECT * from message_attachment_join"):
        message_id, attachment_id = row
        filename, mime_type, total_bytes = c2.execute("SELECT filename, mime_type, total_bytes from attachment where rowid=?", (attachment_id,)).fetchone()
        messageToAttachment[message_id] = {"filename": filename, "mime_type": mime_type, "total_bytes": total_bytes}
    c2.close()
def getChatStatistics():
    for row in c.execute("SELECT ROWID, handle_id, is_from_me from message"):
        rowid, handle_id,is_from_me, = row
        threads[handle_idToid[handle_id]] = threads.get(handle_idToid[handle_id], 0) + 1
        if rowid not in messageToChat:
            continue
        chat_id = messageToChat[rowid]
        if is_from_me == 1:
            chats[chat_id][-1]['count'] = chats[chat_id][-1]['count'] + 1
            if rowid in messageToAttachment:
                chats[chat_id][-1]["attachments"].append(messageToAttachment[rowid])
        else:
            for handler in chats[chat_id]:
                if handler['handle_id'] == handle_id:
                    handler['count'] = handler['count'] + 1
                    if rowid in messageToAttachment:
                        handler["attachments"].append(messageToAttachment[rowid])
                    break
    c.close()
getHandleIdToNumber()
getChats()
getMessageToChats()
getChatStatistics()
c.close()

import json
def outputWithContacts():
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
outputWithContacts()