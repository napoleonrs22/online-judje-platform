'use client';

import React, { useRef, useEffect, useState } from 'react';
import { EditorView, basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';

import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { cpp } from '@codemirror/lang-cpp';
import { java } from '@codemirror/lang-java';

import { oneDark } from '@codemirror/theme-one-dark';

import { lineNumbers, highlightActiveLine } from "@codemirror/view";

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  language: 'python' | 'cpp' | 'java' | 'javascript';
}

export default function CodeEditorWithMirror({ code, onChange, language }: CodeEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const [mounted, setMounted] = useState(false);

  const getLanguageExtension = (lang: string) => {
    switch (lang) {
      case 'python': return python();
      case 'cpp': return cpp();
      case 'java': return java();
      case 'javascript': return javascript();
      default: return python();
    }
  };

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!mounted || !editorRef.current) return;

    if (viewRef.current) viewRef.current.destroy();

    const state = EditorState.create({
      doc: code,
      extensions: [
        basicSetup,
        getLanguageExtension(language),
        oneDark,
        lineNumbers(),
        highlightActiveLine(),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            onChange(update.state.doc.toString());
          }
        }),
        EditorView.theme({
          "&": { height: "100%", fontSize: "14px" },
          ".cm-scroller": { overflow: "auto" },
        }),
      ],
    });

    const view = new EditorView({
      state,
      parent: editorRef.current,
    });

    viewRef.current = view;

    return () => view.destroy();
  }, [language, mounted, onChange]);

  if (!mounted) return <div className="w-full h-full bg-[#1e1e1e]" />;

  return (
    <div
      ref={editorRef}
      className="w-full h-full overflow-hidden bg-[#1e1e1e]"
    />
  );
}
