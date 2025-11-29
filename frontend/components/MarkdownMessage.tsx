import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

type MessageRole = "user" | "assistant";

interface MarkdownMessageProps {
  role: MessageRole;
  content: string;
}

export function MarkdownMessage({ role, content }: MarkdownMessageProps) {
  return (
    <div className={`bubble ${role}`}>
      <ReactMarkdown
        className="markdown-content"
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          code({ inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            if (inline) {
              return (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
            return (
              <pre>
                <code className={match ? `language-${match[1]}` : ""} {...props}>
                  {children}
                </code>
              </pre>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
