import { createRequire } from 'module'; const require=createRequire(import.meta.url);
let pw; try{pw=require('playwright')}catch{pw=require('/opt/node22/lib/node_modules/playwright')}
import path from 'path'; import { fileURLToPath } from 'url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const b=await pw.chromium.launch({args:['--allow-file-access-from-files']});
const p=await b.newPage({viewport:{width:1640,height:624},deviceScaleFactor:2});
await p.goto('file://'+path.join(dir,'cover.html')); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
await p.screenshot({path:path.join(dir,'cover.png')});
// mobile safe-area preview (center 1110px)
await p.screenshot({path:path.join(dir,'cover-mobile-preview.png'),clip:{x:265,y:0,width:1110,height:624}});
await b.close();
