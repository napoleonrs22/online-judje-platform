'use client';

import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { cpp } from '@codemirror/lang-cpp';
import { java } from '@codemirror/lang-java';
import { githubLight, githubDark } from '@uiw/codemirror-theme-github';
// import { oneDark } from '@uiw/codemirror-theme-onedark';


interface CodeEditorProps {
  code: string;
  onChange: (value: string) => void;
  language: 'python' | 'cpp' | 'java' | 'javascript';
  theme?: 'light' | 'dark';
}

const languageMap = {
  python: python(),
  javascript: javascript({ jsx: true, typescript: true }),
  cpp: cpp(),
  java: java(),
};

export default function CodeEditorWithMirror({
  code,
  onChange,
  language,
  theme = 'light',
}: CodeEditorProps) {
  const extensions = [languageMap[language]];



  return (
    <CodeMirror
      value={code}
      height="100%"
      theme={theme === 'dark' ? githubDark : githubLight}
      extensions={extensions}
      onChange={(value) => onChange(value)}
      basicSetup={{
        lineNumbers: true,
        highlightActiveLineGutter: true,
        highlightActiveLine: true,
        bracketMatching: true,
        indentOnInput: true,
        tabSize: 4,
      }}
      indentWithTab={true}
      style={{ fontSize: '14px' }}
    />
  );
}