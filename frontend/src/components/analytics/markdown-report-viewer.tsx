"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

export function MarkdownReportViewer({ markdown }: { markdown: string }) {
  return (
    <article className="prose-report print-surface rounded-3xl border border-border bg-card p-6 shadow-soft md:p-10">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            return match ? (
              <SyntaxHighlighter PreTag="div" language={match[1]} style={oneDark} customStyle={{ borderRadius: 18, margin: 0 }}>
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>{children}</code>
            );
          }
        }}
      >
        {markdown}
      </ReactMarkdown>
    </article>
  );
}
