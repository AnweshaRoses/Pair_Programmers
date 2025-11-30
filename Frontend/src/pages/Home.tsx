import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createRoom } from "../api/rooms";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [joinRoomId, setJoinRoomId] = useState("");
  const [joinLoading, setJoinLoading] = useState(false);
  const navigate = useNavigate();

  const handleCreateRoom = async () => {
    setLoading(true);
    try {
      const room = await createRoom();
      navigate(`/room/${room.roomId}`);
    } catch (error) {
      console.error("Failed to create room:", error);
      alert("Failed to create room. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!joinRoomId.trim()) {
      alert("Please enter a room ID");
      return;
    }

    setJoinLoading(true);
    try {
      // Navigate directly - the Room page will validate the room exists
      navigate(`/room/${joinRoomId.trim()}`);
    } catch (error) {
      console.error("Failed to join room:", error);
      alert("Failed to join room. Please check the room ID and try again.");
    } finally {
      setJoinLoading(false);
    }
  };

  return (
    <div className="home-container">
      <h1>Pair Programmer</h1>
      <p>Collaborative code editing made easy</p>
      
      <div className="home-actions">
        <div className="create-room-section">
          <h2>Create New Room</h2>
          <button 
            onClick={handleCreateRoom} 
            disabled={loading}
            className="primary-button"
          >
            {loading ? "Creating..." : "Create New Room"}
          </button>
        </div>

        <div className="divider">
          <span>OR</span>
        </div>

        <div className="join-room-section">
          <h2>Join Existing Room</h2>
          <form onSubmit={handleJoinRoom} className="join-room-form">
            <input
              type="text"
              placeholder="Enter Room ID"
              value={joinRoomId}
              onChange={(e) => setJoinRoomId(e.target.value)}
              disabled={joinLoading}
              className="room-id-input"
            />
            <button 
              type="submit" 
              disabled={joinLoading || !joinRoomId.trim()}
              className="primary-button"
            >
              {joinLoading ? "Joining..." : "Join Room"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

