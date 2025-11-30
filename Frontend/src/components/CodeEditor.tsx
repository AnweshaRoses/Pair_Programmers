import { useRef, useCallback } from "react";
import Editor from "@monaco-editor/react";
import type { Monaco } from "@monaco-editor/react";
import { useAppDispatch, useAppSelector } from "../store";
import { updateCode, setCursor } from "../store/roomSlice";
import { getAutocomplete } from "../api/autocomplete";

export default function CodeEditor() {
  const dispatch = useAppDispatch();
  const { code, language, cursor } = useAppSelector((state) => state.room);

  const editorRef = useRef<any>(null);
  const monacoRef = useRef<Monaco | null>(null);

  const handleEditorChange = useCallback(
    (value: string | undefined) => {
      if (value !== undefined && value !== code) {
        dispatch(updateCode(value));
      }
    },
    [dispatch, code]
  );

  // ---------------------
  // DEBOUNCE + AUTOCOMPLETE (NO more auto-insert)
  // ---------------------
  const debounceTimer = useRef<number | null>(null);

  const registerAutocomplete = useCallback(
    (monaco: Monaco, editor: any) => {
      monaco.languages.registerCompletionItemProvider(language || "python", {
        triggerCharacters: ["(", ".", ":", " "],

        provideCompletionItems: async () => {
          const text = editor.getValue();

          try {
            const res = await getAutocomplete({
              code: text,
              cursorPosition: cursor,
              language: language || "python",
            });

            if (!res.suggestion) return { suggestions: [] };

            return {
              suggestions: [
                {
                  label: res.suggestion,
                  kind: monaco.languages.CompletionItemKind.Snippet,
                  insertText: res.suggestion,
                  documentation: "AI suggestion",
                },
              ],
            };
          } catch (err) {
            console.error("Autocomplete Error", err);
            return { suggestions: [] };
          }
        },
      });
    },
    [cursor, language]
  );

  const handleDebouncedAutocomplete = useCallback(
    (editor: any, monaco: Monaco) => {
      if (debounceTimer.current) window.clearTimeout(debounceTimer.current);

      debounceTimer.current = window.setTimeout(() => {
        // force Monaco to open autocomplete dropdown
        editor.trigger("manual", "editor.action.triggerSuggest", {});
      }, 600);
    },
    []
  );

  const handleEditorDidMount = (editor: any, monaco: Monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    registerAutocomplete(monaco, editor);

    editor.onDidChangeModelContent(() => {
      handleDebouncedAutocomplete(editor, monaco);
    });

    editor.onDidChangeCursorPosition(() => {
      const pos = editor.getPosition();
      const model = editor.getModel();
      if (model && pos) {
        dispatch(setCursor(model.getOffsetAt(pos)));
      }
    });

    editor.updateOptions({
      quickSuggestions: true,
      suggestOnTriggerCharacters: true,
      tabCompletion: "on",            // Accept with TAB
      acceptSuggestionOnEnter: "off",
      snippetSuggestions: "inline", 
    });
  };

  

  return (
    <div className="code-editor-container">
      <Editor
        height="100%"
        width="100%"
        language={language || "python"}
        value={code}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        theme="vs-dark"
        options={{
          minimap: { enabled: true },
          fontSize: 15,
          wordWrap: "on",
          automaticLayout: true,
        }}
      />
    </div>
  );
}



// import { useRef, useCallback } from "react";
// import Editor from "@monaco-editor/react";
// import type { Monaco } from "@monaco-editor/react";
// import { useAppDispatch, useAppSelector } from "../store";
// import { updateCode, setCursor } from "../store/roomSlice";
// import { getAutocomplete } from "../api/autocomplete";

// export default function CodeEditor() {
//   const dispatch = useAppDispatch();
//   const { code, language, cursor } = useAppSelector((state) => state.room);


//   const editorRef = useRef<any>(null);
//   const monacoRef = useRef<Monaco | null>(null);

//   // ---------------------
//   // HANDLE USER INPUT
//   // ---------------------
//   const handleEditorChange = useCallback(
//     (value: string | undefined) => {
//       if (value !== undefined && value !== code) {
//         dispatch(updateCode(value));
//       }
//     },
//     [dispatch, code]
//   );

//   // ---------------------
//   //  Autocomplete (Debounced backend call)
//   // ---------------------
//   const debounceTimer = useRef<number | null>(null);

//   const fetchAutocomplete = useCallback(
//     async (text: string, cursor: number) => {
//       if (!text.trim()) return;

//       try {
//         const res = await getAutocomplete({
//           code: text,
//           cursorPosition: cursor,
//           language: language || "python",
//         });

//         if (editorRef.current && res.suggestion) {
//           const monaco = monacoRef.current!;
//           const position = editorRef.current.getPosition();

//           editorRef.current.trigger("customAutocomplete", "editor.action.insertSnippet", {
//             snippet: res.suggestion,
//           });
//         }
//       } catch (err) {
//         console.error("Autocomplete error:", err);
//       }
//     },
//     [language]
//   );

//   const handleDebouncedAutocomplete = useCallback(
//     (value: string) => {
//       if (debounceTimer.current) {
//         window.clearTimeout(debounceTimer.current);
//       }
//       debounceTimer.current = window.setTimeout(() => {
//         fetchAutocomplete(value, cursor);
//       }, 600);
//     },
//     [cursor, fetchAutocomplete]
//   );

//   // ---------------------
//   //  Editor Mounted
//   // ---------------------
//   const handleEditorDidMount = (editor: any, monaco: Monaco) => {
//     editorRef.current = editor;
//     monacoRef.current = monaco;

//     editor.onDidChangeModelContent(() => {
//       const value = editor.getValue();
//       handleDebouncedAutocomplete(value);
//     });

//     editor.onDidChangeCursorPosition(() => {
//       const position = editor.getPosition();
//       const model = editor.getModel();
//       if (model && position) {
//         const offset = model.getOffsetAt(position);
//         dispatch(setCursor(offset));
//       }
//     });

//     // Optional: turn off Monaco built-in AI-like suggestions
//     editor.updateOptions({
//       quickSuggestions: true,
//       suggestOnTriggerCharacters: true,
//       tabCompletion: "on",
//       acceptSuggestionOnEnter: "on",
//     });
//   };

//   return (
//     <div className="code-editor-container">
//       <Editor
//         height="100%"
//         width="100%"
//         language={language || "python"}
//         value={code}
//         onChange={handleEditorChange}
//         onMount={handleEditorDidMount}
//         theme="vs-dark"
//         options={{
//           minimap: { enabled: true },
//           fontSize: 15,
//           wordWrap: "on",
//           automaticLayout: true,
//           scrollBeyondLastLine: false,
//         }}
//       />
//     </div>
//   );
// }
