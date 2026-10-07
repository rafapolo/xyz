// bun dataviz/eleicoes/build.ts  ->  index.html (CSS inline minificado) + app.min.js (JS minificado, hash no nome da query)
import { mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';

const root = dirname(new URL(import.meta.url).pathname);
const tmp = join(root, '.build');
rmSync(tmp, { recursive: true, force: true });
mkdirSync(tmp, { recursive: true });

let html = readFileSync(join(root, 'src/index.html'), 'utf8');

const css = /<style>([\s\S]*?)<\/style>/.exec(html);
const js = /<script>\n([\s\S]*?)<\/script>\n<\/body>/.exec(html);
if (!css || !js) throw new Error('não achei o <style> ou o <script> principal em src/index.html');

async function minify(entry: string, ext: string): Promise<string> {
  const out = await Bun.build({ entrypoints: [entry], minify: true, target: 'browser', format: 'iife' });
  if (!out.success) throw new Error(out.logs.join('\n'));
  return await out.outputs[0].text();
}

writeFileSync(join(tmp, 'a.css'), css[1]);
writeFileSync(join(tmp, 'app.js'), js[1]);
const cssMin = (await minify(join(tmp, 'a.css'), 'css')).trim();
const jsMin = (await minify(join(tmp, 'app.js'), 'js')).trim();
const hash = createHash('sha1').update(jsMin).digest('hex').slice(0, 8);

writeFileSync(join(root, 'app.min.js'), jsMin + '\n');
html = html.replace(css[0], () => `<style>${cssMin}</style>`);
html = html.replace(js[0], () => '</body>');
html = html.replace('<script defer src="https://cloud.umami.is', () => `<script defer src="app.min.js?v=${hash}"></script>\n<script defer src="https://cloud.umami.is`);
// enxuga o HTML: comentários e espaço entre tags (fora de <script>/<style>/<pre>)
html = html.replace(/<!--[\s\S]*?-->/g, '').replace(/>\s*\n\s*</g, '><').replace(/\n\s+/g, ' ');
writeFileSync(join(root, 'index.html'), html);

rmSync(tmp, { recursive: true, force: true });
const kb = (n: number) => (n / 1024).toFixed(1) + ' KB';
console.log(`index.html ${kb(html.length)} · app.min.js ${kb(jsMin.length)} (fonte ${kb(js[1].length)}) · css ${kb(cssMin.length)} (fonte ${kb(css[1].length)}) · v=${hash}`);
