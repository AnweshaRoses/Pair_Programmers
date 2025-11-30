import axios from "axios";

// const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_BASE_URL = "http://localhost:8000";

export interface Room {
  roomId: string;
  code: string;
  language: string;
}

export interface CreateRoomResponse {
  roomId: string;
}

export const createRoom = async (): Promise<CreateRoomResponse> => {
  const response = await axios.post<CreateRoomResponse>(`${API_BASE_URL}/rooms`);
  return response.data;
};

export const getRoom = async (roomId: string): Promise<Room> => {
  const response = await axios.get<Room>(`${API_BASE_URL}/rooms/${roomId}`);
  return response.data;
};

