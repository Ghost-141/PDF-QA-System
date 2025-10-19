"use client";

import {
  FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { MarkdownMessage } from "@/components/MarkdownMessage";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePickerKey, setFilePickerKey] = useState(() => crypto.randomUUID());
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusVariant, setStatusVariant] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [isReady, setIsReady] = useState(false);
  const [showReadyToast, setShowReadyToast] = useState(false);
  const formRef = useRef<HTMLFormElement | null>(null);
  const ambientBubbles = useMemo(() => Array.from({ length: 6 }), []);

  const disabled = useMemo(
    () => isProcessingFile || isAsking,
    [isProcessingFile, isAsking]
  );

  const resetStatus = useCallback(() => {
    setStatusMessage(null);
    setStatusVariant("idle");
  }, []);

  const handleFileChange = useCallback<
    React.ChangeEventHandler<HTMLInputElement>
  >((event) => {
    const file = event.target.files?.item(0);
    setSelectedFile(file ?? null);
    resetStatus();
    setIsReady(false);
  }, [resetStatus]);

  const handleProcessFile = useCallback(async () => {
    if (!selectedFile) {
      setStatusVariant("error");
      setStatusMessage("Please choose a PDF or text file first.");
      return;
    }

    setIsProcessingFile(true);
    setStatusVariant("loading");
    setStatusMessage("Uploading file...");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const uploadResponse = await fetch(`${API_BASE_URL}/upload-file`, {
        method: "POST",
        body: formData
      });

      if (!uploadResponse.ok) {
        const detail = await safeError(uploadResponse);
        throw new Error(detail);
      }

      const { filename } = (await uploadResponse.json()) as {
        filename: string;
      };

      setStatusMessage("Populating knowledge base...");

      const processResponse = await fetch(
        `${API_BASE_URL}/process-file?filename=${encodeURIComponent(filename)}`,
        { method: "POST" }
      );

      if (!processResponse.ok) {
        const detail = await safeError(processResponse);
        throw new Error(detail);
      }

      const payload = await processResponse.json();
      setStatusMessage(
        `Processed ${payload.num_docs ?? 0} document chunks from "${filename}". Ready for questions!`
      );
      setStatusVariant("success");
      setIsReady(true);
      setShowReadyToast(true);
      setSelectedFile(null);
      setFilePickerKey(crypto.randomUUID());
    } catch (error) {
      setStatusVariant("error");
      setStatusMessage(
        error instanceof Error ? error.message : "File processing failed."
      );
    } finally {
      setIsProcessingFile(false);
    }
  }, [selectedFile]);

  const handleAskQuestion = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const trimmed = question.trim();
      if (!trimmed || !isReady) {
        return;
      }

      setIsAsking(true);
      resetStatus();

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmed
      };

      setMessages((prev) => [...prev, userMessage]);
      setQuestion("");

      try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: trimmed })
        });

        if (!response.ok) {
          const detail = await safeError(response);
          throw new Error(detail);
        }

        const data = await response.json();
        const content =
          typeof data.answer === "string"
            ? data.answer
            : JSON.stringify(data.answer, null, 2);

        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: "assistant", content }
        ]);
      } catch (error) {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content:
              error instanceof Error
                ? `I encountered an error: ${error.message}`
                : "I encountered an unexpected error."
          }
        ]);
      } finally {
        setIsAsking(false);
      }
    },
    [question, resetStatus, isReady]
  );

  useEffect(() => {
    if (!showReadyToast) {
      return;
    }
    const timer = setTimeout(() => setShowReadyToast(false), 3200);
    return () => clearTimeout(timer);
  }, [showReadyToast]);

  const sendDisabled = disabled || !question.trim() || !isReady;

  const handleTextareaKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        if (sendDisabled) {
          return;
        }
        formRef.current?.requestSubmit();
      }
    },
    [sendDisabled]
  );

  return (
    <>
      <div className="background-visual" aria-hidden="true">
        {ambientBubbles.map((_, index) => (
          <span key={index} className={`bubble bubble-${index % 3}`} />
        ))}
      </div>
      <header className="hero">
        <h1 className="hero__title">Document QA Workspace</h1>
        <p className="hero__subtitle">
          Load a PDF or text report and ask focused questions with a clean,
          minimal chat experience.
        </p>
      </header>
      {showReadyToast ? (
        <div className="toast toast--success">Document indexed. Ask away!</div>
      ) : null}
      <main className="container">
        <section className="card">
          <div className="card-header">
            <span className="card-title">Knowledge Base</span>
          <span className={`pill ${isReady ? "ready" : ""}`}>
            {isReady ? "Ready" : "Awaiting file"}
          </span>
        </div>

        <div className="file-input">
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileChange}
            disabled={disabled}
            key={filePickerKey}
          />
          <div className="file-actions">
            <button
              className="button primary"
              onClick={handleProcessFile}
              disabled={disabled || !selectedFile}
              type="button"
            >
              <span className="button-label">
                {isProcessingFile ? "Processing..." : "Upload & Process"}
              </span>
              {isProcessingFile ? <span className="button-spinner" /> : null}
            </button>
            <button
              className="button secondary subtle"
              onClick={() => {
                setSelectedFile(null);
                setFilePickerKey(crypto.randomUUID());
                resetStatus();
                setIsReady(false);
              }}
              type="button"
              disabled={disabled || !selectedFile}
            >
              Clear Selection
            </button>
            {selectedFile ? (
              <span className="status-bar">
                Selected: {selectedFile.name} ({formatBytes(selectedFile.size)})
              </span>
            ) : null}
          </div>
        </div>

        {statusMessage ? (
          <div className={`status-bar ${statusVariant}`} role="status">
            {statusMessage}
          </div>
        ) : null}
      </section>

      <section className="card">
        <div className="card-header">
          <span className="card-title">Conversation</span>
        </div>

        <div className="chat-area">
          {messages.length === 0 ? (
            isReady ? (
              <div className="empty-state ready">
                <span className="glow-dot" />
                <h2>Ready for your questions</h2>
                <p>
                  Your document is indexed. Ask follow-up questions, request
                  tables, equations, or code - responses render beautifully.
                </p>
              </div>
            ) : (
              <div className="empty-state">
                Upload a document to activate the conversation. Rich text,
                equations, and code blocks render just like ChatGPT.
              </div>
            )
          ) : (
            messages.map((message) => (
              <MarkdownMessage
                key={message.id}
                role={message.role}
                content={message.content}
              />
            ))
          )}
        </div>

        <form
          ref={formRef}
          className="chat-input"
          onSubmit={handleAskQuestion}
        >
          <textarea
            placeholder="Ask a question about your documents..."
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            disabled={disabled || !isReady}
            onKeyDown={handleTextareaKeyDown}
            />
        </form>
      </section>
      </main>
    </>
  );
}

async function safeError(response: Response) {
  try {
    const payload = await response.json();
    if (payload?.detail) {
      return typeof payload.detail === "string"
        ? payload.detail
        : JSON.stringify(payload.detail);
    }
  } catch {
    // fall through
  }
  return `${response.status} ${response.statusText}`;
}

function formatBytes(bytes: number) {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const exponent = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1
  );
  const value = bytes / Math.pow(1024, exponent);
  return `${value.toFixed(1)} ${units[exponent]}`;
}







