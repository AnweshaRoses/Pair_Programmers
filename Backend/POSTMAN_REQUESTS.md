# Postman Collection for Pair Programmer API

## Base URL
```
http://localhost:8000
```

---

## 1. Create Room

**Method:** `POST`  
**Endpoint:** `/rooms`  
**Description:** Creates a new coding room

### Request
```
POST http://localhost:8000/rooms
```

### Response
```json
{
  "roomId": "a1b2c3d4"
}
```

### Example Response
```json
{
  "roomId": "c9122af7"
}
```

---

## 2. Get Room

**Method:** `GET`  
**Endpoint:** `/rooms/{room_id}`  
**Description:** Retrieves room information including current code

### Request
```
GET http://localhost:8000/rooms/c9122af7
```

### Response
```json
{
  "roomId": "c9122af7",
  "code": "def hello():\n    print('Hello, World!')",
  "language": "python"
}
```

---

## 3. Autocomplete

**Method:** `POST`  
**Endpoint:** `/autocomplete`  
**Description:** Get code completion suggestions

### Request
```
POST http://localhost:8000/autocomplete
Content-Type: application/json
```

### Request Body
```json
{
  "code": "def ",
  "cursorPosition": 4,
  "language": "python"
}
```

### Response
```json
{
  "suggestion": "function_name():\n    pass"
}
```

### Example Requests

#### Example 1: Function Definition
```json
{
  "code": "def ",
  "cursorPosition": 4,
  "language": "python"
}
```

#### Example 2: Import Statement
```json
{
  "code": "import ",
  "cursorPosition": 7,
  "language": "python"
}
```

#### Example 3: For Loop
```json
{
  "code": "for ",
  "cursorPosition": 4,
  "language": "python"
}
```

#### Example 4: Class Definition
```json
{
  "code": "class ",
  "cursorPosition": 6,
  "language": "python"
}
```

---

## 4. WebSocket Connection

**Method:** `WebSocket`  
**Endpoint:** `ws://localhost:8000/ws/{room_id}`  
**Description:** Real-time code collaboration

### Connection
```
ws://localhost:8000/ws/c9122af7
```

### Message Protocol

#### Client Messages

##### CODE_UPDATE
Send code changes to the server and broadcast to other users.

```json
{
  "type": "CODE_UPDATE",
  "roomId": "c9122af7",
  "payload": {
    "code": "def hello():\n    print('Hello, World!')",
    "cursor": 22
  }
}
```

##### CURSOR_UPDATE
Share cursor position with other users.

```json
{
  "type": "CURSOR_UPDATE",
  "roomId": "c9122af7",
  "payload": {
    "cursor": 22,
    "selectionStart": 10,
    "selectionEnd": 20
  }
}
```

##### PING
Keep connection alive and check latency.

```json
{
  "type": "PING",
  "roomId": "c9122af7",
  "payload": {}
}
```

#### Server Messages

##### INIT
Received when first connecting to a room.

```json
{
  "type": "INIT",
  "roomId": "c9122af7",
  "payload": {
    "code": "def hello():\n    print('Hello, World!')",
    "cursor": 0
  },
  "connectionCount": 1
}
```

##### CODE_UPDATE
Received when another user updates the code.

```json
{
  "type": "CODE_UPDATE",
  "roomId": "c9122af7",
  "payload": {
    "code": "def hello():\n    print('Hello, World!')",
    "cursor": 22
  },
  "timestamp": "2024-11-29T15:30:45.123456"
}
```

##### CURSOR_UPDATE
Received when another user moves their cursor.

```json
{
  "type": "CURSOR_UPDATE",
  "roomId": "c9122af7",
  "payload": {
    "cursor": 22,
    "selectionStart": 10,
    "selectionEnd": 20
  },
  "userId": "a1b2c3d4"
}
```

##### USER_JOINED
Received when another user joins the room.

```json
{
  "type": "USER_JOINED",
  "roomId": "c9122af7",
  "payload": {
    "userId": "a1b2c3d4"
  },
  "connectionCount": 2
}
```

##### USER_LEFT
Received when another user leaves the room.

```json
{
  "type": "USER_LEFT",
  "roomId": "c9122af7",
  "payload": {
    "userId": "a1b2c3d4"
  },
  "connectionCount": 1
}
```

##### ERROR
Received when an error occurs.

```json
{
  "type": "ERROR",
  "roomId": "c9122af7",
  "payload": {},
  "message": "Invalid message format",
  "code": "INVALID_MESSAGE"
}
```

##### PONG
Response to PING message.

```json
{
  "type": "PONG",
  "roomId": "c9122af7",
  "payload": {}
}
```

---

## Postman Setup Instructions

### 1. HTTP Requests

1. Create a new collection named "Pair Programmer API"
2. Add the following requests:
   - `POST /rooms` - Create Room
   - `GET /rooms/{room_id}` - Get Room
   - `POST /autocomplete` - Autocomplete

### 2. WebSocket Connection

1. In Postman, create a new WebSocket request
2. URL: `ws://localhost:8000/ws/c9122af7` (replace with actual room ID)
3. Click "Connect"

### 3. Testing WebSocket Messages

#### Test 1: Initial Connection
1. Connect to WebSocket
2. You should receive an `INIT` message with the current code

#### Test 2: Code Update
Send:
```json
{
  "type": "CODE_UPDATE",
  "roomId": "c9122af7",
  "payload": {
    "code": "print('Hello, World!')",
    "cursor": 20
  }
}
```

Expected: Other connected clients receive `CODE_UPDATE` message

#### Test 3: Cursor Update
Send:
```json
{
  "type": "CURSOR_UPDATE",
  "roomId": "c9122af7",
  "payload": {
    "cursor": 10,
    "selectionStart": 5,
    "selectionEnd": 15
  }
}
```

Expected: Other connected clients receive `CURSOR_UPDATE` message

#### Test 4: Ping/Pong
Send:
```json
{
  "type": "PING",
  "roomId": "c9122af7",
  "payload": {}
}
```

Expected: Receive `PONG` message

#### Test 5: Multi-User
1. Open two WebSocket connections to the same room
2. Send `CODE_UPDATE` from one connection
3. Verify the other connection receives the update

#### Test 6: Error Handling
Send invalid message:
```json
{
  "type": "INVALID_TYPE",
  "roomId": "c9122af7",
  "payload": {}
}
```

Expected: Receive `ERROR` message

---

## Complete Test Flow

### Step 1: Create a Room
```
POST http://localhost:8000/rooms
```
Save the `roomId` from response

### Step 2: Connect WebSocket
```
ws://localhost:8000/ws/{roomId}
```

### Step 3: Receive INIT
You should receive an INIT message with empty code

### Step 4: Send Code Update
```json
{
  "type": "CODE_UPDATE",
  "roomId": "{roomId}",
  "payload": {
    "code": "def hello():\n    print('Hello!')",
    "cursor": 30
  }
}
```

### Step 5: Verify Room State
```
GET http://localhost:8000/rooms/{roomId}
```
Should return the updated code

### Step 6: Test Autocomplete
```json
{
  "code": "def ",
  "cursorPosition": 4,
  "language": "python"
}
```

### Step 7: Multi-User Test
1. Open second WebSocket connection
2. Send CODE_UPDATE from first connection
3. Verify second connection receives update
4. Disconnect first connection
5. Verify second connection receives USER_LEFT message

---

## Error Codes

- `INVALID_JSON` - Message is not valid JSON
- `INVALID_MESSAGE` - Message structure is invalid
- `ROOM_ID_MISMATCH` - Room ID in message doesn't match connection
- `UNKNOWN_MESSAGE_TYPE` - Message type is not recognized
- `UNKNOWN_ERROR` - Unexpected error occurred

---

## Notes

- All WebSocket messages must be valid JSON
- Room ID in message must match the room ID in the WebSocket URL
- Code is automatically persisted to database when last user disconnects
- Maximum 2 users per room (enforced by WebSocket manager)
- All timestamps are in ISO 8601 format (UTC)

