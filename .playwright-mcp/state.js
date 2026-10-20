async () => { const w=ms=>new Promise(r=>setTimeout(r,ms)); const out=[]; const f=n=>Math.round(n*10)/10;
const R=(e,label)=>{ if(!e){out.push(label+': none');return;} const r=e.getBoundingClientRect(); const s=getComputedStyle(e); out.push(`${label}: [${f(r.x)},${f(r.y)},${f(r.width)}x${f(r.height)}] op${s.opacity} bg${s.backgroundColor} col${s.color} tf${s.transform} font${s.fontSize}/${s.lineHeight}/${s.letterSpacing}/${s.fontWeight} rad${s.borderRadius} pad${s.padding}`); };
const go=async y=>{ window.scrollTo(0,y); await w(1300); };
await go(1000);
out.push('== header after splash scrollY='+scrollY);
R(document.querySelector('.logoZone .logoCont a'),'logo a'); R(document.querySelector('.headerCont'),'headerCont'); R(document.querySelector('header nav'),'nav');
document.querySelectorAll('header nav a.navlink').forEach((a,i)=>{R(a,'navlink'+i); out.push('  after tf '+getComputedStyle(a,'::after').transform+' h'+getComputedStyle(a,'::after').height+' bottom'+getComputedStyle(a,'::after').bottom+' bg'+getComputedStyle(a,'::after').backgroundColor);});
const cap=document.querySelector('#capabilities'); await go(cap.getBoundingClientRect().top+scrollY);
out.push('== capabilities scrollY='+scrollY);
const dd=[...document.querySelectorAll('.dropdown')];
dd[0].click(); await w(700);
out.push('-- dd0 open'); [0,1,2].forEach(i=>{R(dd[i],'dd'+i); }); R(dd[0].querySelector('.plusPill'),'plusPill'); R(dd[0].querySelector('.otherPill'),'otherPill'); R(dd[0].querySelector('.dropdownContent'),'content'); R(dd[0].querySelector('.dropdownContent p'),'content p'); R(dd[0].querySelector('h3'),'h3'); R(dd[0].querySelector('.plusPill svg'),'plus svg');
dd[1].click(); await w(700);
out.push('-- dd1 clicked'); [0,1,2,3].forEach(i=>{R(dd[i],'dd'+i); out.push('  class '+dd[i].className);});
dd[1].click(); await w(700); out.push('-- dd1 reclick'); [0,1].forEach(i=>out.push('  dd'+i+' class '+dd[i].className+' h'+dd[i].getBoundingClientRect().height));
if(dd[0].classList.contains('open')){dd[0].click(); await w(500);}
const part=document.querySelector('#our-work'); await go(part.getBoundingClientRect().top+scrollY+100);
out.push('== carousel scrollY='+scrollY);
const track=document.querySelector('.carousel__track'); const nx=document.querySelector('.carousel__next'); const pv=document.querySelector('.carousel__prev');
const cs=()=>out.push(`  track tf ${getComputedStyle(track).transform} prev ${pv.className} ${getComputedStyle(pv).opacity} next ${nx.className} ${getComputedStyle(nx).opacity}`);
cs(); for(let i=0;i<6;i++){ nx.click(); await w(800); out.push(' after next #'+(i+1)); cs(); }
for(let i=0;i<6;i++){ pv.click(); await w(800);} out.push(' after 6x prev'); cs();
const sl=document.querySelectorAll('.slide'); R(sl[0],'slide0'); R(sl[0].querySelector('h3'),'slide0 title'); R(sl[0].querySelector('.plusPill'),'s0 plusPill'); R(sl[0].querySelector('.photoLayer'),'s0 photoLayer'); out.push('  photoLayer bgimg '+getComputedStyle(sl[0].querySelector('.photoLayer')).backgroundImage); R(sl[0].querySelector('img'),'s0 img'); R(nx.querySelector('svg'),'next svg');
sl[0].click(); await w(700); out.push('-- slide0 active class '+sl[0].className);
R(sl[0].querySelector('h3'),'slide0 title'); R(sl[0].querySelector('.plusPill'),'s0 plusPill'); R(sl[0].querySelector('.otherPill'),'s0 otherPill'); R(sl[0].querySelector('.descriptionLayer'),'s0 descLayer'); R(sl[0].querySelector('.description'),'s0 desc');
sl[1].click(); await w(700); out.push('-- slide1 clicked: s0 '+sl[0].className+' s1 '+sl[1].className); sl[1].click(); await w(500); out.push('-- slide1 reclicked: s1 '+sl[1].className); if(sl[0].classList.contains('active')){sl[0].click(); await w(400);}
const names=[...document.querySelectorAll('.teamMember > div:first-child')]; const n=names[2]; const nr=n.getBoundingClientRect(); await go(nr.top+scrollY - innerHeight/2 + nr.height/2); await w(1200);
out.push('== team scrollY='+scrollY);
document.querySelectorAll('.teamMember').forEach((t,i)=>{ if(t.className!=='teamMember') out.push('  member'+i+' '+t.className); });
const tm=n.parentElement; R(n,'name2'); R(tm.querySelector('.overlayCont'),'overlay'); R(tm.querySelector('.backgroundCont'),'bgCont'); R(tm.querySelector('.backgroundCont img'),'bg img'); out.push('  bg img fit '+getComputedStyle(tm.querySelector('.backgroundCont img')).objectFit+' '+getComputedStyle(tm.querySelector('.backgroundCont img')).objectPosition+' natural '+tm.querySelector('.backgroundCont img').naturalWidth);
R(tm.querySelector('.portraitCont'),'portrait'); const pi=tm.querySelector('.portraitCont img'); R(pi,'portrait img'); out.push('  pimg fit '+getComputedStyle(pi).objectFit+' '+getComputedStyle(pi).objectPosition+' src '+(pi.currentSrc||'').split('/').pop());
R(tm.querySelector('.role'),'role'); out.push('  role before '+getComputedStyle(tm.querySelector('.role'),'::before').width+' '+getComputedStyle(tm.querySelector('.role'),'::before').top); R(tm.querySelector('a.linkedin, .linkedin'),'linkedin'); R(tm.querySelector('.linkedin span'),'linkedin span'); [...tm.querySelectorAll('.linkedin svg')].forEach((s,i)=>R(s,'li svg'+i));
const cta=document.querySelector('.ctaSection'); await go(cta.getBoundingClientRect().top+scrollY);
out.push('== cta scrollY='+scrollY); R(cta.querySelector('h2'),'cta h2'); cta.querySelectorAll('.buttons a').forEach((a,i)=>{R(a,'btn'+i); R(a.querySelector('span'),' span'+i); R(a.querySelector('svg'),' svg'+i);}); R(cta.querySelector('video'),'cloud video');
const hov=[]; for(const ss of document.styleSheets){ try{ for(const r of ss.cssRules){ const walk=(r)=>{ if(r.cssRules&&!r.selectorText){ for(const c of r.cssRules) walk(c); return;} if(r.selectorText&&r.selectorText.includes(':hover')) hov.push((r.parentRule&&r.parentRule.conditionText?'@'+r.parentRule.conditionText+' ':'')+r.cssText.replace(/\[data-v-[a-z0-9]+\]/g,'')); }; walk(r);} }catch(e){} }
out.push('== hover rules'); out.push(...hov);
return out.join('\n'); }
