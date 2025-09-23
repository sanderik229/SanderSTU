const api = {
  listAds: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetch(`/api/ads/${query ? `?${query}` : ''}`).then(r => r.json());
  },
  order: (payload) => fetch('/api/order/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)}).then(r=>r.json()),
  login: (payload) => fetch('/api/auth/login/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)}).then(r=>r.json()),
  register: (payload) => fetch('/api/auth/register/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)}).then(r=>r.json()),
};

function $(sel, root=document){return root.querySelector(sel)}
function $all(sel, root=document){return Array.from(root.querySelectorAll(sel))}

function navigate(where){
  const map = { buy: '/buy/', order: '/order/' };
  const url = map[where];
  if(url){ window.location.assign(url); }
}

function cardTemplate(ad){
  return `<div class="card" data-id="${ad.id}">
    <img src="${ad.image}" alt="${ad.title}">
    <h3>${ad.title}</h3>
    <p>${ad.description}</p>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px">
      <strong>${ad.price.toLocaleString('ru-RU')} ₽</strong>
      <a class="btn small" href="/order/">Заказать</a>
    </div>
  </div>`
}

function renderSampleAds(){
  const container = $('#sampleAds');
  if(!container) return;
  api.listAds({sort:'popularity'}).then(({results})=>{
    container.innerHTML = results.slice(0,3).map(cardTemplate).join('');
  });
}

function setupGlobalSearch(){
  const input = $('#globalSearchInput');
  const btn = $('#globalSearchBtn');
  const box = $('#globalSearchResults');
  if(!input || !btn || !box) return;
  function perform(){
    const q = input.value.trim();
    if(!q){ box.style.display='none'; box.innerHTML=''; return; }
    api.listAds({q}).then(({results})=>{
      box.innerHTML = results.map(r=>`<div class="search-item"><img src="${r.image}"><div><div>${r.title}</div><small>${r.price.toLocaleString('ru-RU')} ₽ · ${r.category}</small></div></div>`).join('');
      box.style.display = results.length ? 'block' : 'none';
    });
  }
  btn.addEventListener('click', perform);
  input.addEventListener('input', ()=>{ if(input.value.length>=2){ perform(); } else { box.style.display='none'; } });
  document.addEventListener('click', (e)=>{ if(!box.contains(e.target) && e.target!==input){ box.style.display='none'; }});
}

function setupBuyPage(){
  const results = $('#buyResults');
  if(!results) return;
  const search=$('#buySearch'), cat=$('#buyCategory'), sort=$('#buySort'), apply=$('#buyApply');
  function load(){
    const params = {};
    if(search.value.trim()) params.q=search.value.trim();
    if(cat.value) params.category=cat.value;
    if(sort.value) params.sort=sort.value;
    api.listAds(params).then(({results:ads})=>{ results.innerHTML = ads.map(cardTemplate).join(''); });
  }
  apply.addEventListener('click', load);
  load();
}

function setupOrderForm(){
  const form = $('#orderForm');
  if(!form) return;
  const status = $('#orderStatus');
  form.addEventListener('submit', (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    status.textContent = 'Отправка...';
    api.order(data).then(()=>{ status.textContent='Запрос отправлен! Менеджер свяжется с вами.'; form.reset(); })
      .catch(()=>{ status.textContent='Ошибка отправки. Попробуйте позже.'; });
  });
}

function setupAuthModals(){
  const openers = $all('[data-modal-open]');
  const closeElems = $all('[data-modal-close]');
  function show(id){ const m=$(`#modal-${id}`); if(m){ m.setAttribute('aria-hidden','false'); }}
  function hideAll(){ $all('.modal').forEach(m=>m.setAttribute('aria-hidden','true')); }
  openers.forEach(b=> b.addEventListener('click', ()=> show(b.dataset.modalOpen)));
  closeElems.forEach(b=> b.addEventListener('click', hideAll));
  $all('.modal-backdrop').forEach(b=> b.addEventListener('click', hideAll));

  const loginForm = $('#loginForm');
  if(loginForm){ loginForm.addEventListener('submit',(e)=>{ e.preventDefault(); const data=Object.fromEntries(new FormData(loginForm).entries()); api.login(data).then(()=>{ hideAll(); alert('Вход выполнен'); }); }); }
  const registerForm = $('#registerForm');
  if(registerForm){ registerForm.addEventListener('submit',(e)=>{ e.preventDefault(); const data=Object.fromEntries(new FormData(registerForm).entries()); api.register(data).then(()=>{ hideAll(); alert('Регистрация выполнена'); }); }); }
}

function setupNav(){
  $all('[data-nav]').forEach(btn=> btn.addEventListener('click', ()=> navigate(btn.dataset.nav)));
}

document.addEventListener('DOMContentLoaded', ()=>{
  renderSampleAds();
  setupGlobalSearch();
  setupBuyPage();
  setupOrderForm();
  setupAuthModals();
  setupNav();
});


