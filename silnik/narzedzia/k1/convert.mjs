// Use the already installed VFM; do not create another Markdown dialect.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
const require = createRequire(path.join(path.dirname(process.execPath), 'global.cjs'));
const cli = require.resolve('@vivliostyle/cli/package.json');
const vfmPath = require.resolve('@vivliostyle/vfm', { paths: [path.dirname(cli)] });
const { stringify } = await import(pathToFileURL(vfmPath).href);
const [source, output] = process.argv.slice(2);
if (!source || !output) throw new Error('Usage: node convert.mjs source.md output.html');
fs.writeFileSync(output, stringify(fs.readFileSync(source, 'utf8'), { footnote: 'dpub', language: 'pl' }));
