// Thahabi robot SVG generator (shared by design.html and index.html)
/* ---------------- robot generator ----------------
   mood: normal | happy | cool | sad | talk ; wave: arm angle */
function robot(theme,mood='normal',opt={}){
  const A=theme==='A';
  const wave=opt.wave??0, mouthOpen=opt.mouth||0, blink=opt.blink||0, bulb=opt.bulb??1, id=opt.id||('r'+Math.random().toString(36).slice(2,7));
  const ink='#16130D', cream='#FFF6EA';
  const sw=A?0:10;                 // outline width
  const stroke=A?'none':ink;
  const gold=A?`url(#${id}g)`:'#FFC93C';
  const gold2=A?`url(#${id}g2)`:'#FFC93C';
  const screen=A?'#0b0906':ink;
  const eye=A?'#FFD970':cream;
  const accent=A?'#FFD970':'#FF5C39';
  const ear=A?`url(#${id}g2)`:'#4361EE';
  const glowEye=A?`filter="url(#${id}glow)"`:'';
  let eyes='';
  if(mood==='normal'||mood==='talk'){const h=Math.max(6,62*(1-blink)),y=-97-h/2;eyes=`<rect x="-78" y="${y}" width="40" height="${h}" rx="${Math.min(20,h/2)}" fill="${eye}" ${glowEye}/><rect x="38" y="${y}" width="40" height="${h}" rx="${Math.min(20,h/2)}" fill="${eye}" ${glowEye}/>`;}
  if(mood==='happy') eyes=`<path d="M-84 -86q26-40 52 0M32 -86q26-40 52 0" stroke="${eye}" stroke-width="14" fill="none" stroke-linecap="round" ${glowEye}/>`;
  if(mood==='sad') eyes=`<path d="M-84 -108L-44 -124M84 -108L44 -124" stroke="${eye}" stroke-width="10" stroke-linecap="round" ${glowEye}/><rect x="-74" y="-100" width="34" height="40" rx="17" fill="${eye}" ${glowEye}/><rect x="40" y="-100" width="34" height="40" rx="17" fill="${eye}" ${glowEye}/><path d="M-50 -58q-8 16 0 22q8-6 0-22" fill="#7cc7ff"/>`;
  if(mood==='cool') eyes=`<g><rect x="-112" y="-122" width="224" height="16" rx="8" fill="${A?'#1a1205':ink}" stroke="${A?'#FFD970':'#FFC93C'}" stroke-width="6"/>
     <path d="M-104 -118h88v34q0 26-30 26h-28q-30 0-30-26z" fill="#000" stroke="${A?'#FFD970':'#FFC93C'}" stroke-width="7"/>
     <path d="M16 -118h88v34q0 26-30 26h-28q-30 0-30-26z" fill="#000" stroke="${A?'#FFD970':'#FFC93C'}" stroke-width="7"/>
     <path d="M-86 -104l20 0M34 -104l20 0" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".8"/></g>`;
  let mouth='';
  if(mood==='normal') mouth=`<path d="M-30 -36q30 26 60 0" stroke="${accent}" stroke-width="12" fill="none" stroke-linecap="round"/>`;
  if(mood==='happy') mouth=`<path d="M-40 -42h80q0 46-40 46t-40-46z" fill="${accent}" ${A?'':'stroke="'+cream+'" stroke-width="0"'}/><path d="M-22 -8q22 12 44 0" fill="${A?'#b8860b':'#c93a1d'}"/>`;
  if(mood==='talk') mouth=`<ellipse cx="0" cy="-26" rx="30" ry="24" fill="${accent}"/><ellipse cx="0" cy="-14" rx="18" ry="9" fill="${A?'#b8860b':'#c93a1d'}"/>`;
  if(mood==='cool') mouth=`<path d="M-26 -34q34 14 56 -10" stroke="${accent}" stroke-width="12" fill="none" stroke-linecap="round"/>`;
  if(mood==='sad') mouth=`<path d="M-30 -22q30 -26 60 0" stroke="${accent}" stroke-width="12" fill="none" stroke-linecap="round"/>`;
  if(mouthOpen>0.06){const ry=Math.min(1,mouthOpen)*(mood==='sad'?16:24)+5;
    mouth=`<ellipse cx="0" cy="${-30+ry*0.3}" rx="${mood==='sad'?24:30}" ry="${ry}" fill="${accent}"/><ellipse cx="0" cy="${-30+ry*0.3+ry*0.45}" rx="${mood==='sad'?14:18}" ry="${ry*0.4}" fill="${A?'#b8860b':'#c93a1d'}"/>`;}
  const cheeks= mood==='sad'?'':`<circle cx="-104" cy="-44" r="15" fill="${A?'#ff9e64':'#FF5C39'}" opacity="${A?.35:.85}"/><circle cx="104" cy="-44" r="15" fill="${A?'#ff9e64':'#FF5C39'}" opacity="${A?.35:.85}"/>`;
  const armR=`<g transform="rotate(${-wave} 140 110)"><rect x="124" y="100" width="36" height="120" rx="18" fill="${gold2}" stroke="${stroke}" stroke-width="${sw*0.8}"/><circle cx="142" cy="224" r="27" fill="${A?'#2a2114':cream}" stroke="${A?'#FFD970':ink}" stroke-width="${A?4:8}"/></g>`;
  const armL=`<g transform="rotate(${opt.waveL||0} -140 110)"><rect x="-160" y="100" width="36" height="120" rx="18" fill="${gold2}" stroke="${stroke}" stroke-width="${sw*0.8}"/><circle cx="-142" cy="224" r="27" fill="${A?'#2a2114':cream}" stroke="${A?'#FFD970':ink}" stroke-width="${A?4:8}"/></g>`;
  return `<svg viewBox="-230 -300 460 600" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;${A?'filter:drop-shadow(0 0 40px rgba(245,197,66,.35)) drop-shadow(0 30px 30px rgba(0,0,0,.6))':'filter:drop-shadow(-14px 14px 0 #16130D)'}">
   <defs>
    <linearGradient id="${id}g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff0b8"/><stop offset=".35" stop-color="#F5C542"/><stop offset=".75" stop-color="#c8900f"/><stop offset="1" stop-color="#8a6410"/></linearGradient>
    <linearGradient id="${id}g2" x1="0" x2="1"><stop offset="0" stop-color="#a8770d"/><stop offset=".5" stop-color="#ffe08a"/><stop offset="1" stop-color="#a8770d"/></linearGradient>
    <filter id="${id}glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
   </defs>
   <!-- antenna -->
   <path d="M0 -205V-250" stroke="${A?'#c8900f':ink}" stroke-width="10" stroke-linecap="round"/>
   <circle cx="0" cy="-262" r="20" opacity="${0.35+0.65*bulb}" fill="${A?'#FFD970':'#FF5C39'}" stroke="${stroke}" stroke-width="${sw*0.8}" ${A?`filter="url(#${id}glow)"`:''}/>
   <!-- legs -->
   <rect x="-78" y="236" width="50" height="46" rx="14" fill="${A?'#2a2114':ink}"/><rect x="28" y="236" width="50" height="46" rx="14" fill="${A?'#2a2114':ink}"/>
   ${armL}
   <!-- body -->
   <rect x="-126" y="70" width="252" height="180" rx="48" fill="${gold}" stroke="${stroke}" stroke-width="${sw}"/>
   <rect x="-68" y="112" width="136" height="80" rx="20" fill="${A?'#0b0906':'#fff'}" stroke="${A?'rgba(255,217,112,.5)':ink}" stroke-width="${A?3:7}"/>
   <text x="0" y="168" text-anchor="middle" font-family="JetBrains Mono" font-weight="700" font-size="46" fill="${A?'#FFD970':ink}">&lt;/&gt;</text>
   ${armR}
   <!-- neck -->
   <rect x="-34" y="44" width="68" height="34" rx="8" fill="${A?'#2a2114':ink}"/>
   <!-- ears -->
   <rect x="-210" y="-128" width="42" height="92" rx="14" fill="${ear}" stroke="${stroke}" stroke-width="${sw*0.8}"/>
   <rect x="168" y="-128" width="42" height="92" rx="14" fill="${ear}" stroke="${stroke}" stroke-width="${sw*0.8}"/>
   <!-- head -->
   <rect x="-180" y="-210" width="360" height="262" rx="66" fill="${gold}" stroke="${stroke}" stroke-width="${sw}"/>
   ${A?'<path d="M-140 -186q60 -18 150 -10" stroke="#fff8dc" stroke-width="10" stroke-linecap="round" opacity=".55" fill="none"/>':''}
   <rect x="-140" y="-172" width="280" height="190" rx="46" fill="${screen}" ${A?'stroke="rgba(255,217,112,.35)" stroke-width="3"':''}/>
   ${cheeks}${eyes}${mouth}
  </svg>`;
}
window.robot=robot;
