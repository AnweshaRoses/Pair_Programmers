import { useEffect, useRef } from "react";
import { useAppDispatch, useAppSelector } from "../store";
import { updateCode, setCursor, setConnectionCount } from "../store/roomSlice";

const WS_BASE_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

interface WebSocketMessage {
  type: string;
  roomId: string;
  payload?: any;
  connectionCount?: number;
  timestamp?: string;
  userId?: string;
  message?: string;
  code?: string;
}

export const useWebSocket = (roomId: string) => {
  const dispatch = useAppDispatch();
  const { code, cursor } = useAppSelector((state) => state.room);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const isLocalUpdateRef = useRef(false);
  const lastSentCodeRef = useRef<string>("");
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!roomId) return;

    const connect = () => {
      try {
        const ws = new WebSocket(`${WS_BASE_URL}/ws/${roomId}`);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log("WebSocket connected");
          reconnectAttempts.current = 0;
        };

        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);

            switch (message.type) {
              case "INIT":
                if (message.payload?.code !== undefined) {
                  dispatch(updateCode(message.payload.code));
                }
                if (message.connectionCount !== undefined) {
                  dispatch(setConnectionCount(message.connectionCount));
                }
                break;

              case "CODE_UPDATE":
                // Only update if this is not from our own local update
                if (!isLocalUpdateRef.current && message.payload?.code !== undefined) {
                  dispatch(updateCode(message.payload.code));
                }
                // Reset the flag after processing
                isLocalUpdateRef.current = false;
                if (message.connectionCount !== undefined) {
                  dispatch(setConnectionCount(message.connectionCount));
                }
                break;

              case "CURSOR_UPDATE":
                if (message.payload?.cursor !== undefined) {
                  // Update cursor from other users (optional - you might want to show their cursors)
                  console.log("Cursor update from user:", message.userId, message.payload.cursor);
                }
                break;

              case "USER_JOINED":
                if (message.connectionCount !== undefined) {
                  dispatch(setConnectionCount(message.connectionCount));
                }
                console.log("User joined:", message.payload?.userId);
                break;

              case "USER_LEFT":
                if (message.connectionCount !== undefined) {
                  dispatch(setConnectionCount(message.connectionCount));
                }
                console.log("User left:", message.payload?.userId);
                break;

              case "ERROR":
                console.error("WebSocket error:", message.message, message.code);
                break;

              case "PONG":
                // Handle pong response
                break;

              default:
                console.warn("Unknown message type:", message.type);
            }
          } catch (error) {
            console.error("Failed to parse WebSocket message:", error);
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket error:", error);
        };

        ws.onclose = () => {
          console.log("WebSocket disconnected");
          wsRef.current = null;

          // Attempt to reconnect
          if (reconnectAttempts.current < maxReconnectAttempts) {
            reconnectAttempts.current++;
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
            console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current})`);
            reconnectTimeoutRef.current = setTimeout(connect, delay);
          } else {
            console.error("Max reconnection attempts reached");
          }
        };
      } catch (error) {
        console.error("Failed to create WebSocket connection:", error);
      }
    };

    connect();

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [roomId, dispatch]);

  // Send code updates when code changes (debounced) - separate effect
  useEffect(() => {
    if (!roomId || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    // Don't send if code hasn't actually changed
    if (code === lastSentCodeRef.current) {
      return;
    }

    // Clear existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    // Debounce code updates (send after 500ms of no changes)
    debounceTimeoutRef.current = setTimeout(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN && roomId && code !== lastSentCodeRef.current) {
        isLocalUpdateRef.current = true;
        lastSentCodeRef.current = code;
        
        const message = {
          type: "CODE_UPDATE",
          roomId: roomId,
          payload: {
            code: code,
            cursor: cursor,
          },
        };
        wsRef.current.send(JSON.stringify(message));
      }
    }, 500);

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [roomId, code, cursor]);

  // Send cursor updates
  useEffect(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN && roomId) {
      const message = {
        type: "CURSOR_UPDATE",
        roomId: roomId,
        payload: {
          cursor: cursor,
        },
      };
      wsRef.current.send(JSON.stringify(message));
    }
  }, [cursor, roomId]);
};

