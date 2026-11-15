import { createRequire } from 'module'; const require=createRequire(import.meta.url);
let pw; try{pw=require('playwright')}catch{pw=require('/opt/node22/lib/node_modules/playwright')}
import path from 'path'; import { fileURLToPath } from 'url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const b=await pw.chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const t of ['A','B']){
  await p.goto('file://'+path.join(dir,'design.html')+'?theme='+t);
  await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
  await p.screenshot({path:path.join(dir,`design-${t}.png`)});
}
await b.close();
