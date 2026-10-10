import { marked } from 'marked';

// One renderer for every text: body files and the Italian fields alike.
marked.setOptions({ gfm: true, breaks: false });

export function md(source: string | undefined): string {
  if (!source) return '';
  // A line that is only <br> (the old pages use them as extra spacing) would start a raw-HTML block in Markdown, and the lines after it would
  // show their asterisks instead of bold/italic. Turn it into a spacer line inside the text, and drop it at the very start.
  const text = source.replace(/^(?:[ \t]*<br\s*\/?>[ \t]*\n)+/, '').replace(/^[ \t]*<br\s*\/?>[ \t]*$/gm, '&nbsp;  ');
  return marked.parse(text, { async: false }) as string;
}
