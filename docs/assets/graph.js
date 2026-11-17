(()=>{
const $$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function setup(svg){
  const dataEl=document.getElementById(svg.id+'-data');const D=dataEl?JSON.parse(dataEl.textContent):{nodes:{},edges:{}};
  const panel=document.getElementById(svg.id+'-panel');const base=svg.dataset.base||'';
  const edges=$$('.ed',svg),nodes=$$('.nd',svg);
  function light(ids){if(!ids){svg.classList.remove('dim');edges.forEach(x=>x.classList.remove('on'));nodes.forEach(x=>x.classList.remove('on'));return;}
    svg.classList.add('dim');edges.forEach(x=>{const on=x.dataset.ends.split(' ').some(i=>ids.has(i));x.classList.toggle('on',on);});
    const lit=new Set(ids);edges.forEach(x=>{if(x.classList.contains('on'))x.dataset.ends.split(' ').forEach(i=>lit.add(i));});
    nodes.forEach(x=>x.classList.toggle('on',lit.has(x.dataset.id)));}
  function showNode(id){if(!panel)return;const n=D.nodes[id];if(!n)return;
    let h='<h3>'+esc(n.type==='group'?'Group':n.type==='org'?'Organisation':n.type==='site'?'Site':n.type==='party'?'Named in a document':n.type)+'</h3><p><b>'+esc(n.name)+'</b>'+(n.sub?' <span class="m">'+esc(n.sub)+'</span>':'')+'</p>';
    if(n.page)h+='<p><a href="'+esc(base+n.page)+'">Open its page →</a></p>';
    if(n.members)h+='<ul>'+n.members.map(m=>'<li>'+(m[1]?'<a href="'+esc(base+m[1])+'">'+esc(m[0])+'</a>':esc(m[0]))+'</li>').join('')+'</ul>';
    const mine=edges.filter(x=>x.dataset.ends.split(' ').includes(id));h+='<p class="m">'+mine.length+' line'+(mine.length===1?'':'s')+' on this drawing. Select a line to see the document behind it.</p>';
    panel.innerHTML=h;}
  function showEdge(eid){if(!panel)return;const d=D.edges[eid];if(!d)return;
    let h='<h3>'+(d.side==='record'?'Record':'Claim')+' · '+d.items.length+' link'+(d.items.length===1?'':'s')+'</h3><p><b>'+esc(d.a)+'</b> '+esc(d.rel)+' <b>'+esc(d.b)+'</b></p><ul>';
    h+=d.items.slice(0,200).map(it=>'<li>'+(d.items.length>1?'<b>'+esc(it.f)+'</b> → '+esc(it.t)+': ':'')+(it.q?'<blockquote>“'+esc(it.q)+'”</blockquote>':'')
      +'<span class="m">'+(it.dp?'<a href="'+esc(base+it.dp)+'">'+esc(it.doc)+'</a>':esc(it.doc))+(it.u?' · <a href="'+esc(it.u)+'" rel="noopener">source</a>':'')+(it.b?' · '+esc(it.b.replace(/_/g,' ')):'')+(it.p?' · '+esc(it.p):'')+'</span></li>').join('')+'</ul>';
    if(d.items.length>200)h+='<p class="m">and '+(d.items.length-200)+' more in the table below.</p>';panel.innerHTML=h;}
  nodes.forEach(n=>{const id=n.dataset.id;
    n.addEventListener('mouseenter',()=>light(new Set([id])));n.addEventListener('mouseleave',()=>{if(!svg.dataset.follow)light(null);else follow(svg.dataset.follow);});
    n.addEventListener('focus',()=>light(new Set([id])));
    if(n.tagName.toLowerCase()!=='a'){n.addEventListener('click',()=>{showNode(id);light(new Set([id]));});
      n.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();showNode(id);}});}});
  edges.forEach(x=>{x.addEventListener('click',()=>showEdge(x.id));x.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();showEdge(x.id);}});});
  function follow(id){if(!id){delete svg.dataset.follow;light(null);return;}svg.dataset.follow=id;
    // what reaches it (upstream) and what it reaches (downstream), along the way goods, power or water go
    const fw={},bw={};edges.forEach(x=>{const u=x.dataset.up,d=x.dataset.dn;if(!u||!d)return;(fw[u]=fw[u]||[]).push(x);(bw[d]=bw[d]||[]).push(x);});
    const on=new Set(),lit=new Set([id]);
    for(const [adj,next] of [[fw,'dn'],[bw,'up']]){const seen=new Set([id]);const q=[id];
      while(q.length){const a=q.shift();for(const x of (adj[a]||[])){on.add(x);const b=x.dataset[next];lit.add(b);if(!seen.has(b)){seen.add(b);q.push(b);}}}}
    svg.classList.add('dim');edges.forEach(x=>x.classList.toggle('on',on.has(x)));nodes.forEach(x=>x.classList.toggle('on',lit.has(x.dataset.id)));}
  const fsel=document.getElementById(svg.id+'-follow');if(fsel)fsel.addEventListener('change',()=>{follow(fsel.value);if(fsel.value)showNode(fsel.value);else if(panel)panel.innerHTML='';});
  $$('input[data-hide]').filter(i=>i.dataset.for===svg.id).forEach(i=>i.addEventListener('change',()=>svg.classList.toggle('no-'+i.dataset.hide,!i.checked)));
}
$$('svg.lg[id]').forEach(setup);
// one search box for sites, organisations, countries, documents and entries
$$('.gsearch').forEach(box=>{const inp=box.querySelector('input'),ul=box.querySelector('ul'),base=box.dataset.base||'';let IDX=null,sel=-1;
  const T={site:'Site',org:'Organisation',country:'Country',doc:'Document',entry:'Entry'};
  async function load(){if(IDX)return IDX;try{const r=await fetch(base+'data/search.json');IDX=(await r.json()).items;}catch(e){IDX=[];}return IDX;}
  async function run(){const t=inp.value.trim().toLowerCase();if(t.length<2){ul.innerHTML='';return;}const ws=t.split(/\s+/);const idx=await load();
    const hits=[];for(const it of idx){const s=it[4];if(ws.every(w=>s.includes(w))){hits.push(it);if(hits.length>=40)break;}}
    hits.sort((a,b)=>(a[1].toLowerCase().startsWith(t)?0:1)-(b[1].toLowerCase().startsWith(t)?0:1));
    sel=-1;ul.innerHTML=hits.slice(0,14).map(it=>'<li><a href="'+esc(base+it[2])+'">'+esc(it[1])+'<span class="m">'+esc(T[it[0]]||it[0])+(it[3]?' · '+esc(it[3]):'')+'</span></a></li>').join('')
      +(hits.length?'':'<li><span class="m" style="padding:7px 12px;display:block">Nothing found</span></li>');}
  inp.addEventListener('input',run);inp.addEventListener('focus',load);
  inp.addEventListener('keydown',ev=>{const as=[...ul.querySelectorAll('a')];if(!as.length)return;
    if(ev.key==='ArrowDown'){ev.preventDefault();sel=Math.min(as.length-1,sel+1);}else if(ev.key==='ArrowUp'){ev.preventDefault();sel=Math.max(0,sel-1);}
    else if(ev.key==='Enter'&&sel>=0){ev.preventDefault();location.href=as[sel].href;return;}else if(ev.key==='Escape'){ul.innerHTML='';return;}else return;
    as.forEach((a,i)=>a.classList.toggle('sel',i===sel));});
  document.addEventListener('click',ev=>{if(!box.contains(ev.target))ul.innerHTML='';});});
})();
