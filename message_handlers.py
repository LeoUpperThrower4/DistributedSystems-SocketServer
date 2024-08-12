import psycopg2
import uuid
import json
import time

def connect():
    conn = psycopg2.connect(database="chat-distribuidos", user="admin", password="admin", host="127.0.0.1", port="5433")
    return conn

conn = connect()
cursor = conn.cursor()

def handle_room_join(serialized_message):
    authorId = serialized_message["authorId"]
    roomId = serialized_message["roomId"]
    
    cursor.execute('UPDATE "User" SET "roomId" = %s WHERE "id" = %s;', (roomId, authorId))
    conn.commit()

    all_members_in_room = 'SELECT "name","email","id" FROM "User" WHERE "roomId" = %s;'
    cursor.execute(all_members_in_room, (roomId,))
    members = cursor.fetchall()
    conn.commit()
    serialized_members = []
    
    for member in members:
        serialized_members.append({
            "name": member[0],
            "email": member[1],
            "id": member[2]
        })

  
    members_in_the_room = {
        "type": "members",
        "content": serialized_members}
    

    get_author = 'SELECT "name" FROM "User" WHERE "id" = %s;'
    cursor.execute(get_author, (authorId,))
    author = cursor.fetchone()
    conn.commit()
    createdAt = time.time()

    rndid = str(uuid.uuid4())
    new_join = json.dumps({
        "id": rndid,
        "authorId": authorId,
        "roomId": roomId,
        "content": "",
        "type": "join",
        "createdAt": createdAt,
        "author": {
            "name": author[0]
        }
    })
    


    return  json.dumps(members_in_the_room), new_join

    
def handle_text_message(serialized_message):
    authorId = serialized_message["authorId"]
    roomId = serialized_message["roomId"]
    content = serialized_message["content"]
    msg_type = serialized_message["type"]
    rndid = str(uuid.uuid4())
    createdAt = time.time()

    print(serialized_message)

    cursor.execute('INSERT INTO "Message" ("id", "authorId", "roomId", "content", "type") VALUES (%s, %s, %s, %s, %s);', (rndid, authorId, roomId, content, msg_type))
    get_author = 'SELECT "name" FROM "User" WHERE "id" = %s;'
    cursor.execute(get_author, (authorId,))
    author = cursor.fetchone()
    conn.commit()
    
    message = json.dumps({
        "id": rndid,
        "authorId": authorId,
        "roomId": roomId,
        "content": content,
        "type": "message",
        "createdAt": createdAt,
        "author": {
            "name": author[0]
        }
    })
    return message

def handle_client_leave(authorId, roomId):
    authorId = authorId
    roomId = roomId


    
    cursor.execute('UPDATE "User" SET "roomId" = NULL WHERE "id" = %s;', (authorId,))
    conn.commit()


    all_members_in_room = 'SELECT "name","email","id" FROM "User" WHERE "roomId" = %s;'
    cursor.execute(all_members_in_room, (roomId,))
    members = cursor.fetchall()
    conn.commit()
    serialized_members = []
    
    for member in members:
        serialized_members.append({
            "name": member[0],
            "email": member[1],
            "id": member[2]
        })

    get_author = 'SELECT "name" FROM "User" WHERE "id" = %s;'
    cursor.execute(get_author, (authorId,))
    author = cursor.fetchone()
    conn.commit()
    createdAt = time.time()

    rndid = str(uuid.uuid4())
    new_leave = json.dumps({
        "id": rndid,
        "authorId": authorId,
        "roomId": roomId,
        "content": "",
        "type": "leave",
        "createdAt": createdAt,
        "author": {
            "name": author[0]
        }
    })

    members_in_the_room = {
    "type": "members",
    "content": serialized_members}

    return json.dumps(members_in_the_room), new_leave
