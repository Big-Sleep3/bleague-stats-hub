/* B.PREMIER STATS HUB: one-page navigation shared by all public tools. */
(function(){
  'use strict';
  var source=document.currentScript;
  if(!source||!source.src)return;
  var base=new URL('.',source.src);
  var routes=[
    {id:'advanced',path:'index.html#advanced',ja:'クラブ詳細',en:'Team Advanced'},
    {id:'basic',path:'index.html#basic',ja:'クラブ基本',en:'Team Basic'},
    {id:'players',path:'index.html#players',ja:'個人成績',en:'Player Stats'},
    {id:'compare',path:'index.html#compare',ja:'クラブ比較',en:'Compare Teams'},
    {id:'defense',path:'defense.html',ja:'守備 DEFENSE',en:'Defense Lab'},
    {id:'lab',path:'advanced-lab.html',ja:'高度 ADVANCED',en:'Advanced Lab'},
    {id:'contracts',path:'contracts/index.html',ja:'契約HUB',en:'Contract Hub'},
    {id:'recruiting',path:'recruiting/index.html',ja:'大学リクルート',en:'College Recruiting'}
  ];
  var quickIds=['advanced','players','defense','lab','contracts','recruiting'];
  var current='advanced';
  var nav=null,select=null,currentText=null;

  function findCurrent(){
    var path=location.pathname;
    var root=base.pathname;
    var relative=path.indexOf(root)===0?path.slice(root.length):path.split('/').slice(-2).join('/');
    if(relative===''||relative==='index.html'){
      var hash=location.hash.slice(1).toLowerCase();
      return ['advanced','basic','players','compare'].indexOf(hash)>=0?hash:'advanced';
    }
    if(relative==='defense.html')return 'defense';
    if(relative==='advanced-lab.html')return 'lab';
    if(relative==='contracts/index.html')return 'contracts';
    if(['recruiting/index.html','recruiting/sources.html','recruiting/staff.html'].includes(relative))return 'recruiting';
    return 'advanced';
  }
  function language(){
    return document.documentElement.lang.toLowerCase().indexOf('en')===0?'en':'ja';
  }
  function textFor(route){return route[language()]}
  function aFor(route,quick){
    var a=document.createElement('a');
    a.className='hub-nav-link';
    a.href=new URL(route.path,base).href;
    a.dataset.hubPage=route.id;
    a.textContent=textFor(route);
    if(quick)a.dataset.hubQuick='true';
    return a;
  }
  function sync(){
    if(!nav)return;
    current=findCurrent();
    var lang=language();
    var chosen=routes.find(function(r){return r.id===current})||routes[0];
    currentText.textContent=lang==='ja'?'ページを移動':'Switch page';
    select.setAttribute('aria-label',lang==='ja'?'移動先ページ':'Choose a page');
    nav.setAttribute('aria-label',lang==='ja'?'STATS HUB ページ切り替え':'STATS HUB page navigation');
    nav.querySelectorAll('[data-hub-page]').forEach(function(a){
      var r=routes.find(function(x){return x.id===a.dataset.hubPage});
      if(!r)return;
      a.textContent=textFor(r);
      if(r.id===current)a.setAttribute('aria-current','page');
      else a.removeAttribute('aria-current');
    });
    Array.from(select.options).forEach(function(option){
      var r=routes.find(function(x){return x.id===option.value});
      if(r)option.textContent=textFor(r);
    });
    select.value=current;
    var caption=nav.querySelector('.hub-nav-brand-desc');
    caption.textContent=lang==='ja'?'データ・スカウティング':'DATA & SCOUTING';
    nav.querySelector('.hub-nav-brand').setAttribute('aria-label',lang==='ja'?'STATS HUB トップへ':'STATS HUB home');
    document.documentElement.style.scrollPaddingTop=(window.innerWidth<=830?'110px':'60px');
  }
  function init(){
    if(document.getElementById('hubGlobalNav'))return;
    nav=document.createElement('nav');
    nav.id='hubGlobalNav';
    nav.setAttribute('aria-label','STATS HUB ページ切り替え');
    var inner=document.createElement('div');inner.className='hub-nav-inner';
    var brand=document.createElement('a');brand.className='hub-nav-brand';
    brand.href=new URL('index.html#advanced',base).href;
    var mark=document.createElement('span');mark.className='hub-nav-mark';mark.textContent='◈';
    var labels=document.createElement('span');
    var name=document.createElement('strong');name.className='hub-nav-brand-name';name.textContent='STATS HUB';
    var caption=document.createElement('small');caption.className='hub-nav-brand-desc';caption.textContent='データ・スカウティング';
    labels.append(name,caption);brand.append(mark,labels);
    inner.appendChild(brand);
    var links=document.createElement('div');links.className='hub-nav-links';
    routes.forEach(function(r){links.appendChild(aFor(r,false))});inner.appendChild(links);
    var mobile=document.createElement('div');mobile.className='hub-nav-mobile';
    currentText=document.createElement('label');currentText.className='hub-nav-mobile-label';
    currentText.htmlFor='hubNavSelect';currentText.textContent='ページを移動';
    select=document.createElement('select');select.className='hub-nav-select';select.id='hubNavSelect';
    routes.forEach(function(r){var o=document.createElement('option');o.value=r.id;o.textContent=textFor(r);select.appendChild(o)});
    select.addEventListener('change',function(){
      var r=routes.find(function(x){return x.id===select.value});
      if(r)location.href=new URL(r.path,base).href;
    });
    mobile.append(currentText,select);inner.appendChild(mobile);
    var quick=document.createElement('div');quick.className='hub-nav-quick';
    quickIds.forEach(function(id){var r=routes.find(function(x){return x.id===id});quick.appendChild(aFor(r,true))});
    inner.appendChild(quick);nav.appendChild(inner);
    document.body.insertBefore(nav,document.body.firstChild);
    window.addEventListener('hashchange',sync);
    window.addEventListener('popstate',sync);
    window.addEventListener('hub-nav-refresh',sync);
    new MutationObserver(sync).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
    sync();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
