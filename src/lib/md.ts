import { marked } from 'marked';
import { isTallImage } from './imgsize';

// One renderer for every text: body files and the Italian fields alike.
marked.setOptions({ gfm: true, breaks: false });

export function md(source: string | undefined): string {
  if (!source) return '';
  // A line that is only <br> (the old pages use them as extra spacing) would start a raw-HTML block in Markdown, and the lines after it would
  // show their asterisks instead of bold/italic. Turn it into a spacer line inside the text, and drop it at the very start.
  const text = source.replace(/^(?:[ \t]*<br\s*\/?>[ \t]*\n)+/, '').replace(/^[ \t]*<br\s*\/?>[ \t]*$/gm, '&nbsp;  ');
  const html = marked.parse(text, { async: false }) as string;
  // portrait and near-square pictures get class "tall", which the portrait rule in global.css scales down (designer, 261010)
  return html.replace(/<img\b([^>]*?)(\/?)>/g, (all, attrs: string, slash: string) => {
    const src = /\bsrc="(\/[^"]+)"/.exec(attrs)?.[1];
    if (!src || /\.cover\.?_?\.|\/flag\./.test(src) || !isTallImage(src)) return all;
    return /\bclass="/.test(attrs) ? `<img${attrs.replace(/\bclass="/, 'class="tall ')}${slash}>` : `<img class="tall"${attrs}${slash}>`;
  });
}
