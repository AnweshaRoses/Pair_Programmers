import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { getRoom } from "../api/rooms";

interface RoomState {
  roomId: string | null;
  code: string;
  language: string;
  cursor: number;
  loading: boolean;
  error: string | null;
  connectionCount: number;
}

const initialState: RoomState = {
  roomId: null,
  code: "",
  language: "python",
  cursor: 0,
  loading: false,
  error: null,
  connectionCount: 0,
};

export const fetchRoom = createAsyncThunk(
  "room/fetchRoom",
  async (roomId: string, { rejectWithValue }) => {
    try {
      const room = await getRoom(roomId);
      return room;
    } catch (error: any) {
      return rejectWithValue(error.message || "Failed to fetch room");
    }
  }
);

const roomSlice = createSlice({
  name: "room",
  initialState,
  reducers: {
    setRoomId: (state, action: PayloadAction<string>) => {
      state.roomId = action.payload;
    },
    updateCode: (state, action: PayloadAction<string>) => {
      state.code = action.payload;
    },
    setCursor: (state, action: PayloadAction<number>) => {
      state.cursor = action.payload;
    },
    setLanguage: (state, action: PayloadAction<string>) => {
      state.language = action.payload;
    },
    setConnectionCount: (state, action: PayloadAction<number>) => {
      state.connectionCount = action.payload;
    },
    resetRoom: (state) => {
      return initialState;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRoom.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRoom.fulfilled, (state, action) => {
        state.loading = false;
        state.code = action.payload.code;
        state.language = action.payload.language || "python";
        state.roomId = action.payload.roomId;
      })
      .addCase(fetchRoom.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setRoomId,
  updateCode,
  setCursor,
  setLanguage,
  setConnectionCount,
  resetRoom,
} = roomSlice.actions;

export default roomSlice.reducer;

