import {build} from 'esbuild';
import fs from 'node:fs/promises';
const ui=await build({entryPoints:['web/main.mjs'],bundle:true,format:'iife',write:false,platform:'browser',minify:true});
const css=await fs.readFile('web/style.css','utf8');
await fs.writeFile('web/result.html',`<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Startup Jury</title><style>${css}</style></head><body><main id="jury"></main><p id="bridge-status" role="status"></p><script>${ui.outputFiles[0].text.replaceAll('</script','<\\/script')}</script></body></html>`);
await build({entryPoints:['server/main.mjs'],bundle:true,platform:'node',format:'esm',outfile:'server/bundle.mjs',banner:{js:"import { createRequire } from 'node:module'; const require = createRequire(import.meta.url);"}});
console.log('Built Startup Jury MCP bridge and self-contained widget.');
