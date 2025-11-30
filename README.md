
# 🚀 Pair Programmer – Real-Time Collaborative Coding App

## 🧭 Overview

A full-stack real-time pair-programming web application built with FastAPI, WebSockets, PostgreSQL, React, TypeScript, Redux Toolkit, and Monaco Editor.

Two users can join the same coding room, edit code together, and receive AI-style autocomplete suggestions in real time. 


---

## ⚙️ Features

✅ Room Creation & Joining

* Create new coding rooms (POST /rooms)

* Join via URL: http://localhost:3000/room/<roomId>

* No authentication required

✅ Real-Time Collaborative Coding

* Shared Monaco Editor instance

* Live WebSocket sync between users

* Last-write-wins consistency

* In-memory room state with DB fallback

✅ AI Autocomplete (Mocked)

* 600ms debounce before calling backend

* Suggestion shown in Monaco dropdown

* Accept suggestion only via TAB (Enter still creates new line) 

---

## 🏗️ Setup Guide

### Clone the Repository

```bash
git clone https://github.com/yourusername/kube-credential.git
cd kube-credential
```

### ⚙️ Backend Setup (FastAPI + PostgreSQL)

1️⃣ Create virtual environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

3️⃣ Create .env
```bash
DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost:5433/peer_programmers
```

4️⃣ Run database migrations
```bash
alembic upgrade head
```

5️⃣ Start FastAPI
```bash
uvicorn app.main:app --reload
```


Backend URL:
```bash
http://localhost:8000
```


### 🎨 Frontend Setup (React + TypeScript + Vite)
1️⃣ Install dependencies
```bash
cd frontend
npm install
```

2️⃣ Run frontend
```bash
npm run dev
```

Frontend URL:
```bash
http://localhost:3000
```


## 🔌 API Endpoints

All REST API endpoints for this project are documented in Postman:

👉 Full Postman Documentation:
https://documenter.getpostman.com/view/20681399/2sB3dLUXRb

This includes:

POST /rooms – Create a new coding room

GET /rooms/{roomId} – Fetch existing room data

POST /autocomplete – Autocomplete suggestion API

Each endpoint contains:

* Request schema

* Response schema

* Sample requests

*  Example payloads

* Response examples

### 🧲 WebSocket Endpoint (Real-Time Collaboration)

The WebSocket endpoint used for live code sync is:

```bash
ws://localhost:8000/ws/{roomId}
```
Here we are able to see that when peer 2 joins then we get a message
<img width="2022" height="1350" alt="image" src="https://github.com/user-attachments/assets/bc4d03f3-e9c9-4b89-b869-5e95ab8f011f" />

Here is the code edited by peer 2
<img width="993" height="595" alt="Screenshot 2025-11-30 at 1 16 01 PM" src="https://github.com/user-attachments/assets/fc0ff117-7ee4-4557-96d5-54ee8ea67a43" />

We see the same code sent to peer 1 in real time 
<img width="2024" height="1364" alt="image" src="https://github.com/user-attachments/assets/4f9b3d6d-9894-4728-929b-052c32cca776" />



This demonstrates:

Successful WebSocket connection

Real-time message exchange

Code update events

## 🚀 What I Would Improve With More Time
1. Full Database Persistence

* Automatic periodic saving

* Room recovery on refresh

* Per-room version history

2. Authentication & Authorization

* Google/GitHub login

* Role-based controls (host, viewer, editor)

* Invite-only private rooms

* JWT-secured WebSocket connections

3. Better Autocomplete (AI or Language Server Protocol)

* Integrate real AI models

* Provide inline suggestions (ghost text)

4. Presence Indicators

Planned improvements:

* Name tags & color coding

* Real-time “X is typing…” indicators


5. Test Coverage

* Unit tests (backend + frontend)

* WebSocket integration tests


##  ⚠️ Limitations (Current Version)
1. No Database Persistence

2. No Horizontal scaling

3. Non - AI  Autocomplete

4. No Authentication

5. No ghost-text inline preview






