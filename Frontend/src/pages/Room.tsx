import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../store";
import { fetchRoom, setRoomId } from "../store/roomSlice";
import CodeEditor from "../components/CodeEditor";
import { useWebSocket } from "../hooks/useWebSocket";
import { getAutocomplete } from "../api/autocomplete";

export default function Room() {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  const { code, language, loading, error } = useAppSelector(
    (state) => state.room
  );

  // ----------------------------
  // Autocomplete state + debounce
  // ----------------------------
  const [suggestion, setSuggestion] = useState("");
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleCodeChange = (updatedCode: string) => {
    // Clear any existing timer
    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    // Start a new 600ms debounce timer
    debounceTimer.current = setTimeout(async () => {
      try {
        const response = await getAutocomplete({
          code: updatedCode,
          cursorPosition: updatedCode.length,
          language: language || "python",
        });

        setSuggestion(response.suggestion || "");
      } catch (err) {
        console.error("Autocomplete error:", err);
      }
    }, 600);
  };

  // ----------------------------
  // Load room data
  // ----------------------------
  useEffect(() => {
    if (!roomId) {
      navigate("/");
      return;
    }
    dispatch(setRoomId(roomId));
    dispatch(fetchRoom(roomId));
  }, [roomId, navigate, dispatch]);

  // ----------------------------
  // WebSocket connection
  // ----------------------------
  useWebSocket(roomId || "");

  return (
    <div className="room-container">
      <div className="room-header">
        <div className="room-info">
          <h2>Room: {roomId}</h2>
          <span className="room-language">
            Language: {language || "python"}
          </span>
        </div>
        <button onClick={() => navigate("/")} className="leave-button">
          Leave Room
        </button>
      </div>

      {loading && (
        <div className="room-loading">
          <p>Loading room...</p>
        </div>
      )}

      {error && (
        <div className="room-error">
          <p>Error: {error}</p>
          <button onClick={() => navigate("/")}>Go Home</button>
        </div>
      )}

      {!loading && !error && (
        <div className="room-content">
          <CodeEditor
          />
        </div>
      )}
    </div>
  );
}



// import { useEffect } from "react";
// import { useParams, useNavigate } from "react-router-dom";
// import { useAppDispatch, useAppSelector } from "../store";
// import { fetchRoom, setRoomId } from "../store/roomSlice";
// import CodeEditor from "../components/CodeEditor";
// import { useWebSocket } from "../hooks/useWebSocket";
// export default function Room() {
//   const { roomId } = useParams<{ roomId: string }>();
//   const navigate = useNavigate();
//   const dispatch = useAppDispatch();
//   const { code, language, loading, error } = useAppSelector(
//     (state) => state.room
//   );
//   useEffect(() => {
//     if (!roomId) {
//       navigate("/");
//       return;
//     }
//     dispatch(setRoomId(roomId));
//     dispatch(fetchRoom(roomId));
//   }, [roomId, navigate, dispatch]);
//   // Initialize WebSocket connection
//   useWebSocket(roomId || "");
//   return (
//     <div className="room-container">
//       {" "}
//       <div className="room-header">
//         {" "}
//         <div className="room-info">
//           {" "}
//           <h2>Room: {roomId}</h2>{" "}
//           <span className="room-language">
//             Language: {language || "python"}
//           </span>{" "}
//         </div>{" "}
//         <button onClick={() => navigate("/")} className="leave-button">
//           {" "}
//           Leave Room{" "}
//         </button>{" "}
//       </div>{" "}
//       {loading && (
//         <div className="room-loading">
//           {" "}
//           <p>Loading room...</p>{" "}
//         </div>
//       )}{" "}
//       {error && (
//         <div className="room-error">
//           {" "}
//           <p>Error: {error}</p>{" "}
//           <button onClick={() => navigate("/")}>Go Home</button>{" "}
//         </div>
//       )}{" "}
//       {!loading && !error && (
//         <div className="room-content">
//           {" "}
//           <CodeEditor />{" "}
//         </div>
//       )}{" "}
//     </div>
//   );
// }
