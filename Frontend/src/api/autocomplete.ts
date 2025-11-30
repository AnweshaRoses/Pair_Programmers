import axios from "axios";

// const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_BASE_URL = "http://localhost:8000";

export interface AutocompleteRequest {
  code: string;
  cursorPosition: number;
  language?: string;
}

export interface AutocompleteResponse {
  suggestion: string;
}

export const getAutocomplete = async (
  request: AutocompleteRequest
): Promise<AutocompleteResponse> => {
  const response = await axios.post<AutocompleteResponse>(
    `${API_BASE_URL}/autocomplete`,
    {
      code: request.code,
      cursorPosition: request.cursorPosition,
      language: request.language || "python",
    }
  );
  return response.data;
};

