import fs from 'fs';
import { globSync } from 'glob';
import { marked } from 'marked';
import path from 'path';

/**
 * Converts a markdown file to HTML and writes it to the same directory.
 * @param mdPath - Path to the markdown file
 */
function convertMarkdownToHtml(mdPath: string): void {
  const content = fs.readFileSync(mdPath, 'utf-8');
  const renderer = new marked.Renderer();
  
  renderer.code = function (code) {
    const text = typeof code === 'string' ? code : code.text;
    const lang = typeof code === 'string' ? '' : code.lang;
    
    if (lang === 'mermaid' || text.match(/^sequenceDiagram/) || text.match(/^graph/)) {
      return '<pre class="mermaid">' + text + '</pre>';
    }
    return '<pre><code>' + text + '</code></pre>';
  };

  const bodyHtml = marked(content, { renderer });
  const title = path.basename(mdPath, '.md');
  
  const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({ startOnLoad: true });
  </script>
</head>
<body>
${bodyHtml}
</body>
</html>`;

  const htmlPath = mdPath.replace(/\.md$/, '.html');
  fs.writeFileSync(htmlPath, fullHtml, 'utf-8');
  console.log(`Generated: ${htmlPath}`);
}

/**
 * Main entry point. Accepts a glob pattern to find markdown files.
 */
function main(): void {
  const pattern = process.argv[2];
  
  if (!pattern) {
    console.error('Usage: tsx bin/html/index.ts <pattern>');
    console.error('Example: tsx bin/html/index.ts docs');
    process.exit(1);
  }
  
  const globPattern = pattern.endsWith('.md') ? pattern : `${pattern}/**/*.md`;
  const files = globSync(globPattern, { nodir: true });
  
  if (files.length === 0) {
    console.error(`No markdown files found matching: ${globPattern}`);
    process.exit(1);
  }
  
  files.forEach(convertMarkdownToHtml);
}

main();