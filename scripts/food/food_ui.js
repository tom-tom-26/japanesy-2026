
  // ---- Food tab ----------------------------------------------------------
  // Data is embedded as JSON (#food-data, built from scripts/food/*.json by gen_html.py).
  // Leaflet + MarkerCluster are loaded lazily the first time the tab opens.
  (function(){
    const dataEl = document.getElementById('food-data');
    if(!dataEl) return;
    const D = JSON.parse(dataEl.textContent);
    const ANCH = D.anchors, VEN = D.venues, TL = D.timeline, DAYS = D.days;
    const $ = id => document.getElementById(id);
    const WK = ['sun','mon','tue','wed','thu','fri','sat'];
    const CAT = {ramen:['🍜','Ramen'],'soba-udon':['🍲','Soba / Udon'],sushi:['🍣','Sushi'],'tonkatsu-fry':['🍤','Tonkatsu / fried'],
      'yakitori-grill':['🍢','Yakitori / grill'],yakiniku:['🥩','Yakiniku'],izakaya:['🍶','Izakaya'],'kaiseki-teishoku':['🍱','Teishoku / kaiseki'],
      'unagi-tempura':['🐟','Unagi / tempura'],'okonomiyaki-monja':['🥞','Okonomiyaki'],curry:['🍛','Curry'],'western-yoshoku':['🍳','Yoshoku'],
      'cafe-kissaten':['☕','Cafe / kissaten'],'bakery-sweets':['🥐','Bakery / sweets'],'street-food-market':['🍡','Street food / market'],bar:['🍸','Bar'],other:['🍽️','Other']};
    const RES = {none:'No reservation',recommended:'Reservation recommended',required:'Reservation required','walk-in-queue':'Walk-in, expect a queue'};
    const MIN_PER_KM = 15.6;           // 4.8 km/h walking + 25% street-layout factor
    const PAGE = 30;

    const st = {date:DAYS[0].date, hour:12, anchor:null, auto:true, radius:20, prices:new Set(), cats:new Set(), noRes:false, closed:false, sort:'score', shown:PAGE};
    let map=null, cluster=null, circle=null, anchorMk=null, mapReady=false, libsState=0, markers={};

    const esc = s => String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    const t2m = s => { const p=s.split(':'); return +p[0]*60 + +p[1]; };
    const m2t = m => { m%=1440; return String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0'); };
    const hourLab = h => m2t(h*60) + (h>=24 ? ' (+1)' : '');
    const dist = (a,b) => { const R=6371, r=Math.PI/180, dp=(b.lat-a.lat)*r, dl=(b.lng-a.lng)*r;
      const x=Math.sin(dp/2)**2+Math.cos(a.lat*r)*Math.cos(b.lat*r)*Math.sin(dl/2)**2; return 2*R*Math.asin(Math.sqrt(x)); };
    const dayObj = () => DAYS.find(d=>d.date===st.date);
    const weekday = () => WK[new Date(st.date+'T00:00:00Z').getUTCDay()];

    function autoAnchor(){
      const steps = TL[st.date] || []; let id = steps.length ? steps[0][1] : Object.keys(ANCH)[0], label = '';
      steps.forEach(s=>{ if(s[0] <= st.hour){ id=s[1]; label=s[2]; } });
      if(!label && steps.length) label = steps[0][2];
      return {id, label};
    }

    // Open status at the chosen hour: returns {open, until} ; "until" = closing time of the interval we're in
    function status(v){
      const t = st.hour*60, iv = (v.hours[weekday()]||[]);
      for(const x of iv){ const a=t2m(x[0]), b=t2m(x[1]); if(t>=a && t<b) return {open:true, until:b, left:b-t}; }
      return {open:false, today:iv};
    }
    function todayHours(v){ const iv=v.hours[weekday()]||[]; return iv.length ? iv.map(x=>m2t(t2m(x[0]))+'–'+m2t(t2m(x[1]))).join(', ') : 'Closed this day'; }

    function results(){
      const a = ANCH[st.anchor], out=[];
      VEN.forEach(v=>{
        const walk = dist(a,v) * MIN_PER_KM;
        if(walk > st.radius) return;
        const s = status(v);
        if(!s.open && !st.closed) return;
        if(st.prices.size && !st.prices.has(v.price)) return;
        if(st.cats.size && !st.cats.has(v.cat)) return;
        if(st.noRes && v.reservation!=='none' && v.reservation!=='walk-in-queue') return;
        out.push({v, walk, s});
      });
      const sc = r => r.v.tabelog ? r.v.tabelog.score : 0;
      out.sort((x,y)=>{
        if(x.s.open!==y.s.open) return x.s.open ? -1 : 1;
        if(st.sort==='dist') return x.walk-y.walk;
        if(st.sort==='price') return x.v.price-y.v.price || sc(y)-sc(x);
        return sc(y)-sc(x) || x.walk-y.walk;
      });
      return out;
    }

    function cardHTML(r){
      const v=r.v, c=CAT[v.cat]||CAT.other, tb=v.tabelog;
      const score = tb ? '<div class="fx-score" title="Tabelog score (Japanese locals)">'+tb.score.toFixed(2)+'<small>'+tb.reviews.toLocaleString()+' reviews</small></div>'
                       : '<div class="fx-score none" title="Not rated on Tabelog — praised elsewhere, see why">no<br>Tabelog</div>';
      let stat;
      if(r.s.open) stat = r.s.left<=60 ? '<span class="fx-pill warn">Closes '+m2t(r.s.until)+'</span>' : '<span class="fx-pill ok">Open · until '+m2t(r.s.until)+'</span>';
      else stat = '<span class="fx-pill shut">Closed at '+m2t(st.hour*60)+'</span>';
      const chk = v.audit==='ok' ? '<span class="fx-pill ok" title="Hours/details confirmed on a non-Tabelog source">✓ cross-checked</span>' : '';
      const res = v.reservation==='none' ? '' : '<span class="fx-pill res">'+esc(RES[v.reservation])+'</span>';
      const links = '<div class="fx-links">'+(tb?'<a href="'+esc(tb.url)+'" target="_blank" rel="noopener" onclick="event.stopPropagation()">Tabelog</a>':'')+
        '<a href="https://www.google.com/maps/search/?api=1&query='+v.lat+','+v.lng+'" target="_blank" rel="noopener" onclick="event.stopPropagation()">Map</a></div>';
      return '<div class="fx-card'+(r.s.open?'':' closed')+'" data-id="'+esc(v.id)+'">'+
        '<div class="fx-top"><div><div class="fx-name">'+c[0]+' '+esc(v.name)+'</div><div class="fx-jp">'+esc(v.jp)+'</div></div>'+score+'</div>'+
        '<div class="fx-meta"><span class="fx-pill price">'+'$'.repeat(v.price)+'</span><span class="fx-pill">'+c[1]+'</span>'+stat+res+chk+
        '<span class="fx-pill">'+Math.max(1,Math.round(r.walk))+' min walk</span></div>'+
        '<div class="fx-why">'+esc(v.why)+'</div>'+
        '<div class="fx-note">'+esc(todayHours(v))+(v.price_note?' · '+esc(v.price_note):'')+'</div>'+
        (v.res_note&&v.reservation!=='none'?'<div class="fx-note">'+esc(v.res_note)+'</div>':'')+
        (v.notes?'<div class="fx-note">'+esc(v.notes)+'</div>':'')+links+'</div>';
    }
    function popupHTML(r){
      const v=r.v, tb=v.tabelog;
      return '<b>'+esc(v.name)+'</b><br>'+esc(v.jp)+'<br>'+'$'.repeat(v.price)+' · '+(CAT[v.cat]||CAT.other)[1]+(tb?' · Tabelog '+tb.score.toFixed(2):'')+
        '<br>'+(r.s.open?'Open until '+m2t(r.s.until):'Closed now')+' · '+Math.max(1,Math.round(r.walk))+' min walk'+
        (v.reservation!=='none'?'<br><i>'+esc(RES[v.reservation])+'</i>':'')+'<br>'+esc(v.why);
    }

    function render(){
      const dObj = dayObj(), a = ANCH[st.anchor];
      const rs = results();
      const open = rs.filter(r=>r.s.open).length;
      $('fxHourLab').textContent = hourLab(st.hour);
      const au = autoAnchor();
      $('fxWhere').textContent = st.auto ? '📍 Itinerary has you here: '+au.label+' — '+a.name : '📍 Custom area: '+a.name;
      $('fxCount').innerHTML = '<b>'+open+'</b> open at '+hourLab(st.hour)+' within a '+st.radius+'-minute walk of '+esc(a.name)+(st.closed&&rs.length>open?' · '+(rs.length-open)+' closed (greyed)':'');
      $('fxList').innerHTML = rs.slice(0, st.shown).map(cardHTML).join('') || '<p class="fx-note">Nothing matches these filters at this hour — try a wider walk, another hour, or clear a filter.</p>';
      $('fxMore').hidden = rs.length <= st.shown;
      drawMap(rs, a);
    }

    // ---- map -------------------------------------------------------------
    function loadLibs(cb){
      if(window.L && L.markerClusterGroup) return cb(true);
      if(libsState===1) return;
      libsState=1;
      const base='https://cdnjs.cloudflare.com/ajax/libs/';
      ['leaflet/1.9.4/leaflet.min.css','leaflet.markercluster/1.5.3/MarkerCluster.min.css','leaflet.markercluster/1.5.3/MarkerCluster.Default.min.css'].forEach(h=>{
        const l=document.createElement('link'); l.rel='stylesheet'; l.href=base+h; document.head.appendChild(l); });
      const s1=document.createElement('script'); s1.src=base+'leaflet/1.9.4/leaflet.min.js';
      s1.onerror=()=>{libsState=2; cb(false);};
      s1.onload=()=>{ const s2=document.createElement('script'); s2.src=base+'leaflet.markercluster/1.5.3/leaflet.markercluster.min.js';
        s2.onerror=()=>{libsState=2; cb(false);}; s2.onload=()=>{libsState=3; cb(true);}; document.head.appendChild(s2); };
      document.head.appendChild(s1);
    }
    function initMap(){
      map = L.map('fxMap',{zoomControl:true}).setView([35.69,139.70],14);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,
        attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
      cluster = L.markerClusterGroup({showCoverageOnHover:false,maxClusterRadius:42,spiderfyOnMaxZoom:true});
      map.addLayer(cluster);
      mapReady = true;
    }
    function drawMap(rs, a){
      if(!mapReady) return;
      cluster.clearLayers(); markers={};
      if(circle) map.removeLayer(circle); if(anchorMk) map.removeLayer(anchorMk);
      rs.forEach(r=>{
        const v=r.v, ic=L.divIcon({className:'',iconSize:[30,30],iconAnchor:[15,15],
          html:'<div class="fm'+(r.s.open?'':' closed')+'" data-p="'+v.price+'">'+(CAT[v.cat]||CAT.other)[0]+'</div>'});
        const m=L.marker([v.lat,v.lng],{icon:ic}).bindPopup(popupHTML(r));
        markers[v.id]=m; cluster.addLayer(m);
      });
      circle = L.circle([a.lat,a.lng],{radius:st.radius/MIN_PER_KM*1000,color:'#ff5a7a',weight:1.5,fillOpacity:.04,dashArray:'6 6',interactive:false}).addTo(map);
      anchorMk = L.marker([a.lat,a.lng],{zIndexOffset:1000,interactive:false,icon:L.divIcon({className:'',iconSize:[34,34],iconAnchor:[17,17],html:'<div class="fm fm-anchor">📍</div>'})}).addTo(map);
      map.fitBounds(circle.getBounds().pad(.05));
    }
    function showMap(){
      if(mapReady){ setTimeout(()=>{map.invalidateSize(); render();},60); return; }
      loadLibs(ok=>{
        if(!ok){ $('fxMapErr').hidden=false; return; }
        initMap(); setTimeout(()=>{map.invalidateSize(); render();},60);
      });
    }

    // ---- controls --------------------------------------------------------
    function buildControls(){
      $('fxDays').innerHTML = DAYS.map(d=>'<button data-d="'+d.date+'">'+d.label.replace(/^(\w+) /,'$1 ')+'<small>'+esc(d.city)+'</small></button>').join('');
      const prices=[1,2,3,4];
      $('fxPrice').innerHTML = prices.map(p=>'<button data-p="'+p+'">'+'$'.repeat(p)+'</button>').join('');
      const cats=[...new Set(VEN.map(v=>v.cat))].sort((x,y)=>CAT[x][1].localeCompare(CAT[y][1]));
      $('fxCat').innerHTML = cats.map(c=>'<button data-c="'+c+'">'+CAT[c][0]+' '+CAT[c][1]+'</button>').join('');
      // anchor dropdown, grouped by timeline order
      const ids=Object.keys(ANCH);
      $('fxAnchor').innerHTML = '<option value="__auto">Where the itinerary has us (auto)</option>'+ids.map(i=>'<option value="'+i+'">'+esc(ANCH[i].name)+'</option>').join('');
    }
    function syncDay(){
      const d=dayObj(), lo=d.hours[0], hi=d.hours[1], h=$('fxHour');
      h.min=lo; h.max=hi;
      st.hour=Math.min(hi,Math.max(lo,st.hour)); h.value=st.hour;
      document.querySelectorAll('#fxDays button').forEach(b=>b.classList.toggle('on', b.dataset.d===st.date));
    }
    function refreshAnchor(){ if(st.auto) st.anchor=autoAnchor().id; $('fxAnchor').value = st.auto ? '__auto' : st.anchor; }
    function update(resetPage){ if(resetPage) st.shown=PAGE; refreshAnchor(); render(); }

    $('fxDays').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; st.date=b.dataset.d; syncDay(); update(true); });
    $('fxHour').addEventListener('input',e=>{ st.hour=+e.target.value; update(true); });
    $('fxAnchor').addEventListener('change',e=>{ if(e.target.value==='__auto'){ st.auto=true; } else { st.auto=false; st.anchor=e.target.value; } update(true); });
    $('fxRadius').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; st.radius=+b.dataset.r;
      document.querySelectorAll('#fxRadius button').forEach(x=>x.classList.toggle('on',x===b)); update(true); });
    $('fxPrice').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; const p=+b.dataset.p;
      st.prices.has(p)?st.prices.delete(p):st.prices.add(p); b.classList.toggle('on'); update(true); });
    $('fxCat').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; const c=b.dataset.c;
      st.cats.has(c)?st.cats.delete(c):st.cats.add(c); b.classList.toggle('on'); update(true); });
    $('fxNoRes').addEventListener('change',e=>{ st.noRes=e.target.checked; update(true); });
    $('fxClosed').addEventListener('change',e=>{ st.closed=e.target.checked; update(true); });
    $('fxSort').addEventListener('change',e=>{ st.sort=e.target.value; update(true); });
    $('fxMore').addEventListener('click',()=>{ st.shown+=PAGE; render(); });
    $('fxList').addEventListener('click',e=>{ const c=e.target.closest('.fx-card'); if(!c||!mapReady||e.target.closest('a')) return;
      const m=markers[c.dataset.id]; if(!m) return;
      document.querySelector('.fx-mapwrap').scrollIntoView({behavior:'smooth',block:'center'});
      cluster.zoomToShowLayer(m,()=>{ map.setView(m.getLatLng(), Math.max(map.getZoom(),17)); m.openPopup(); }); });

    // default to today's date/time when viewed during the trip
    (function(){
      const n=new Date(), ds=n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0');
      if(DAYS.some(d=>d.date===ds)){ st.date=ds; st.hour=n.getHours(); } else { st.date=DAYS[1].date; st.hour=12; }
    })();
    buildControls(); syncDay(); refreshAnchor();
    const fbtn = document.querySelector('.nav button[data-t="food"]');
    if(fbtn) fbtn.addEventListener('click',()=>{ setTimeout(()=>{ render(); showMap(); }, 30); });
    render();
  })();
