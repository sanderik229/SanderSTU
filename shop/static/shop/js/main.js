const storage = {
  setTokens: (access, refresh) => { 
    localStorage.setItem('access', access); 
    localStorage.setItem('refresh', refresh||''); 
    // Сохраняем токен в cookies для веб-запросов
    document.cookie = `access_token=${access}; path=/; max-age=3600; SameSite=Lax`;
  },
  getAccess: () => localStorage.getItem('access'),
  getRefresh: () => localStorage.getItem('refresh'),
  clear: () => { 
    localStorage.removeItem('access'); 
    localStorage.removeItem('refresh'); 
    localStorage.removeItem('userEmail'); 
    localStorage.removeItem('userFullName'); 
    // Очищаем cookies
    document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  },
  setEmail: (email) => localStorage.setItem('userEmail', email),
  getEmail: () => localStorage.getItem('userEmail'),
  setFullName: (fullName) => localStorage.setItem('userFullName', fullName),
  getFullName: () => localStorage.getItem('userFullName'),
};

function getCSRFToken(){
  const name = 'csrftoken=';
  const parts = document.cookie ? document.cookie.split(';') : [];
  for(const part of parts){
    const p = part.trim();
    if(p.startsWith(name)) return decodeURIComponent(p.substring(name.length));
  }
  return '';
}

const authHeaders = () => {
  const h = {'Content-Type':'application/json'};
  const token = storage.getAccess();
  if(token) h['Authorization'] = `Bearer ${token}`;
  const csrf = getCSRFToken();
  if(csrf) h['X-CSRFToken'] = csrf;
  return h;
};

const api = {
  listAds: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetch(`/api/ads/${query ? `?${query}` : ''}`).then(r => r.json());
  },
  // v2 APIs
  listOffers: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetch(`/api/v2/offers/${query ? `?${query}` : ''}`).then(r => r.json());
  },
  listBloggers: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetch(`/api/v2/bloggers/${query ? `?${query}` : ''}`).then(r => r.json());
  },
  order: (payload) => fetch('/api/order/', {method:'POST', headers:authHeaders(), credentials:'same-origin', body:JSON.stringify(payload)}).then(r=>r.json()),
  // v2 auth
  login: (payload) => fetch('/api/v2/auth/login/', {method:'POST', headers:authHeaders(), credentials:'same-origin', body:JSON.stringify(payload)}).then(r=>r.json()),
  register: (payload) => fetch('/api/v2/auth/register/', {method:'POST', headers:authHeaders(), credentials:'same-origin', body:JSON.stringify(payload)}).then(r=>r.json()),
  me: () => fetch('/api/v2/me/', {headers:authHeaders()}).then(r=>r.ok?r.json():null),
  // Refresh token
  refreshToken: () => {
    const refresh = storage.getRefresh();
    if(!refresh) return Promise.reject('No refresh token');
    return fetch('/api/v2/auth/refresh/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({refresh})}).then(r=>r.json());
  },
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
    <img src="${ad.image || '/static/shop/img/banner_main.svg'}" alt="${ad.title}">
    <h3>${ad.title}</h3>
    <p>${ad.description}</p>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px">
      <strong>${ad.price.toLocaleString('ru-RU')} ₽</strong>
      <a class="btn small" href="/order/">Заказать</a>
    </div>
  </div>`
}

function offerCardTemplate(offer){
  console.log('Creating card for offer:', offer);
  return `<div class="card" data-id="${offer.id}">
    <div style="height:160px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-weight:600;font-size:18px">
      ${offer.blogger.social_network.toUpperCase()}
    </div>
    <h3>${offer.title}</h3>
    <p><strong>Блогер:</strong> ${offer.blogger.name}</p>
    <p><strong>Тематика:</strong> ${offer.blogger.topic}</p>
    <p><strong>Аудитория:</strong> ${offer.blogger.audience_size.toLocaleString('ru-RU')} подписчиков</p>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px">
      <strong>${offer.price.toLocaleString('ru-RU')} ₽</strong>
      <button class="btn small" onclick="openPurchaseModal(${offer.id})">Заказать</button>
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
    const searchQuery = input.value.trim();
    if(!searchQuery){ 
      box.style.display='none'; 
      box.innerHTML=''; 
      return; 
    }
    
    // Показываем индикатор загрузки
    box.innerHTML = '<div class="search-item">Поиск...</div>';
    box.style.display = 'block';
    
    api.listAds({search: searchQuery}).then(({results})=>{
      if(results && results.length > 0) {
        const resultsHtml = results.map(r=>`<div class="search-item" onclick="window.location.href='/search/?q=${encodeURIComponent(searchQuery)}'">
          <img src="${r.image || '/static/shop/img/banner_main.svg'}" alt="${r.title}">
          <div>
            <div>${r.title}</div>
            <small>${r.price.toLocaleString('ru-RU')} ₽ · ${r.category}</small>
          </div>
        </div>`).join('');
        
        // Добавляем ссылку "Показать все результаты"
        const showAllLink = `<div class="search-item" style="border-top: 1px solid var(--border); font-weight: 500; color: var(--accent);" onclick="window.location.href='/search/?q=${encodeURIComponent(searchQuery)}'">
          <div style="text-align: center; width: 100%;">Показать все результаты (${results.length})</div>
        </div>`;
        
        box.innerHTML = resultsHtml + showAllLink;
      } else {
        box.innerHTML = '<div class="search-item">Ничего не найдено</div>';
      }
      box.style.display = 'block';
    }).catch(error => {
      console.error('Search error:', error);
      box.innerHTML = '<div class="search-item">Ошибка поиска</div>';
      box.style.display = 'block';
    });
  }
  
  btn.addEventListener('click', () => {
    const searchQuery = input.value.trim();
    if (searchQuery) {
      window.location.href = `/search/?q=${encodeURIComponent(searchQuery)}`;
    } else {
      perform();
    }
  });
  input.addEventListener('input', ()=>{ 
    if(input.value.length>=2){ 
      perform(); 
    } else { 
      box.style.display='none'; 
    } 
  });
  
  // Закрытие результатов при клике вне области поиска
  document.addEventListener('click', (e)=>{ 
    if(!box.contains(e.target) && e.target!==input && e.target!==btn){ 
      box.style.display='none'; 
    } 
  });
  
  // Поиск по Enter
  input.addEventListener('keypress', (e) => {
    if(e.key === 'Enter') {
      perform();
    }
  });
}

function setupBuyPage(){
  console.log('Setting up buy page...');
  const results = $('#buyResults');
  if(!results) {
    console.log('buyResults element not found');
    return;
  }
  console.log('Found buyResults element');
  
  const search=$('#buySearch'), social=$('#buySocial'), sort=$('#buySort'), apply=$('#buyApply');
  function load(){
    console.log('Loading offers...');
    const params = {};
    if(search.value.trim()) params.search=search.value.trim();
    if(social.value) params.social_network=social.value;
    if(sort.value) params.ordering=sort.value;
    
    api.listOffers(params).then((data)=>{
      console.log('Offers loaded:', data);
      const offers = data.results || data;
      results.innerHTML = offers.map(offerCardTemplate).join('');
      console.log('Offers rendered, total:', offers.length);
    }).catch((error)=>{
      console.error('Error loading offers:', error);
      // Fallback to old API
      api.listAds({sort:'popularity'}).then(({results:ads})=>{ 
        results.innerHTML = ads.map(cardTemplate).join(''); 
      });
    });
  }
  
  if(apply) {
    apply.addEventListener('click', load);
    console.log('Apply button listener added');
  }
  
  load();
}

function setupOrderForm(){
  const form = $('#orderForm');
  if(!form) return;
  const status = $('#orderStatus');
  
  // Auto-fill user data if logged in
  const userEmail = storage.getEmail();
  const userFullName = storage.getFullName();
  
  if (userEmail) {
    const emailInput = document.querySelector('input[name="email"]');
    if (emailInput) emailInput.value = userEmail;
  }
  
  if (userFullName) {
    const fullNameInput = document.querySelector('input[name="full_name"]');
    if (fullNameInput) fullNameInput.value = userFullName;
  }
  
  // Phone validation
  const phoneInput = document.querySelector('input[name="phone"]');
  if (phoneInput) {
    phoneInput.addEventListener('input', function(e) {
      // Remove all non-digits
      let value = e.target.value.replace(/\D/g, '');
      
      // Limit to 11 digits maximum
      if (value.length > 11) {
        value = value.substring(0, 11);
      }
      
      // Add +7 prefix if it starts with 7 or 8
      if (value.startsWith('7') || value.startsWith('8')) {
        value = '+7' + value.substring(1);
      } else if (!value.startsWith('+7') && value.length > 0) {
        value = '+7' + value;
      }
      
      e.target.value = value;
    });
  }
  
  // Budget validation
  const budgetInput = document.querySelector('input[name="budget"]');
  if (budgetInput) {
    budgetInput.addEventListener('input', function(e) {
      // Remove all non-digits
      e.target.value = e.target.value.replace(/\D/g, '');
    });
  }
  
  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    status.textContent = 'Отправка...';
    
    // Create order data for v2 API
    const orderData = {
      full_name: data.full_name,
      email: data.email,
      phone: data.phone,
      ad_type: data.ad_type,
      budget: parseInt(data.budget),
      description: data.description,
      order_type: 'personal' // Mark as personal order
    };
    
    try {
      // Try to send order
      let response = await fetch('/api/v2/orders/', {method:'POST', headers:authHeaders(), credentials:'same-origin', body:JSON.stringify(orderData)});
      
      // If token expired, try to refresh
      if(response.status === 401) {
        try {
          const refreshResponse = await api.refreshToken();
          if(refreshResponse.access) {
            storage.setTokens(refreshResponse.access, refreshResponse.refresh);
            // Retry with new token
            response = await fetch('/api/v2/orders/', {method:'POST', headers:authHeaders(), credentials:'same-origin', body:JSON.stringify(orderData)});
          }
        } catch(refreshError) {
          console.error('Token refresh failed:', refreshError);
          // If refresh fails, try without auth (for personal orders)
          response = await fetch('/api/v2/orders/', {method:'POST', headers:{'Content-Type':'application/json'}, credentials:'same-origin', body:JSON.stringify(orderData)});
        }
      }
      
      if(response.ok) {
        const result = await response.json();
        console.log('Order created:', result);
        showToast('Заказ успешно отправлен! Ожидайте, пока кто-то его примет.', 'success');
        setTimeout(() => {
          window.location.assign('/my-orders/');
        }, 2000);
      } else {
        const errorText = await response.text();
        throw new Error(errorText || 'Error');
      }
    } catch(error) {
      console.error('Order error:', error);
      status.textContent='Ошибка отправки. Попробуйте позже.'; 
      showToast('Ошибка отправки заказа: ' + error.message, 'error');
    }
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
  const loginStatus = $('#loginStatus');
  if(loginForm){ loginForm.addEventListener('submit', async (e)=>{ e.preventDefault(); const data=Object.fromEntries(new FormData(loginForm).entries());
      const res = await api.login({username:data.email, password:data.password});
      if(res && res.access){
        storage.setTokens(res.access, res.refresh);
        showToast('Вход выполнен', 'success');
        await postLoginFlow();
        hideAll();
      } else { showToast('Ошибка входа', 'error'); }
    }); }
  const registerForm = $('#registerForm');
  const registerStatus = $('#registerStatus');
  if(registerForm){ registerForm.addEventListener('submit', async (e)=>{ e.preventDefault(); const data=Object.fromEntries(new FormData(registerForm).entries());
      // our register takes email,password,full_name,birth_year (birth_year optional here)
      registerStatus.textContent = 'Отправка...';
      const payload = { email: data.email, password: data.password, full_name: data.full_name, birth_year: data.birth_year ? Number(data.birth_year) : null };
      const res = await api.register(payload);
      if(res && res.access){
        storage.setTokens(res.access, res.refresh||'');
        storage.setEmail(res.user && res.user.email ? res.user.email : data.email);
        showToast('Регистрация успешна', 'success');
        await postLoginFlow();
        hideAll();
      } else if(res && res.detail){ showToast(res.detail, 'error'); }
      else { showToast('Ошибка регистрации', 'error'); }
    }); }
}

function showModal(id){ const m=$(`#modal-${id}`); if(m){ m.setAttribute('aria-hidden','false'); }}

function updateAuthUI(){
  const access = storage.getAccess();
  const authActions = $('#authActions');
  const authUser = $('#authUser');
  const nameSpan = $('#userNameDisplay');
  const adminBtn = $('#menuAdmin');
  const managerBtn = $('#menuManager');
  
  if(access){
    authActions.style.display='none';
    authUser.style.display='flex';
    nameSpan.textContent = storage.getEmail() || '';
    
    // Проверяем роль пользователя
    checkAdminStatus().then(roles => {
      if(adminBtn) {
        adminBtn.style.display = roles.isAdmin || roles.isSuperAdmin ? 'block' : 'none';
      }
      if(managerBtn) {
        managerBtn.style.display = roles.isManager ? 'block' : 'none';
      }
    });
  } else {
    authActions.style.display='flex';
    authUser.style.display='none';
    if(nameSpan) nameSpan.textContent = '';
    if(adminBtn) adminBtn.style.display = 'none';
    if(managerBtn) managerBtn.style.display = 'none';
  }
}

async function checkAdminStatus() {
  try {
    const me = await api.me();
    if(me) {
      const role = me.profile && me.profile.role ? me.profile.role : 'user';
      const isAdmin = role === 'admin' || me.is_staff || me.is_superuser;
      const isManager = me.is_staff && !me.is_superuser;
      
      // Возвращаем информацию о роли пользователя
      return {
        isAdmin: isAdmin && !isManager,
        isManager: isManager,
        isSuperAdmin: me.is_superuser
      };
    }
  } catch(e) {
    console.error('Ошибка проверки статуса администратора:', e);
  }
  return { isAdmin: false, isManager: false, isSuperAdmin: false };
}

async function postLoginFlow(){
  // Fetch user profile to determine role and email
  try{
    const me = await api.me();
    if(me){
      const fullName = me.profile && me.profile.full_name ? me.profile.full_name : (me.email || me.username || '');
      storage.setEmail(fullName);
      updateAuthUI();
      
      // Проверяем, есть ли у пользователя профиль менеджера
      let isManager = false;
      try {
        const managerResponse = await fetch('/manager/api/managers/profile/', {
          headers: {
            'Authorization': `Bearer ${storage.getAccess()}`,
            'Content-Type': 'application/json'
          }
        });
        isManager = managerResponse.ok;
      } catch(e) {
        console.log('Пользователь не является менеджером');
      }
      
      const role = me.profile && me.profile.role ? me.profile.role : 'user';
      const isAdmin = role === 'admin' || me.is_superuser;
      
      if(isManager){
        // Менеджер - перенаправляем в панель менеджера
        console.log('Перенаправляем менеджера в панель менеджера');
        window.location.assign('/manager/');
      } else if(isAdmin){
        // Супер-админ или админ - перенаправляем в админ-панель
        console.log('Перенаправляем админа в админ-панель');
        window.location.assign('/admin-panel/');
      } else {
        // Обычный пользователь - остаемся на главной странице
        console.log('Обычный пользователь, остаемся на главной');
      }
    } else {
      updateAuthUI();
    }
  } catch(e){ 
    console.error('Ошибка в postLoginFlow:', e);
    updateAuthUI(); 
  }
}

function showToast(message, type='info'){
  const el = document.getElementById('toast');
  if(!el) return;
  el.className = `toast ${type}`;
  el.textContent = message;
  requestAnimationFrame(()=>{
    el.classList.add('show');
    setTimeout(()=>{ el.classList.remove('show'); }, 2200);
  });
}

function setupNav(){
  $all('[data-nav]').forEach(btn=> btn.addEventListener('click', ()=> navigate(btn.dataset.nav)));
}

function setupProfilePage(){
  const profileForm = $('#profileForm');
  const profileStatus = $('#profileStatus');
  const profileFullName = $('#profileFullName');
  const profileEmail = $('#profileEmail');
  const profileOrdersList = $('#profileOrdersList');
  const logoutProfileBtn = $('#logoutProfileBtn');
  
  if(!profileForm) return;
  
  // Load user profile data
  async function loadProfile(){
    try {
      const response = await fetch('/api/v2/me/', {headers:authHeaders()});
      if(response.ok) {
        const userData = await response.json();
        console.log('Profile loaded:', userData);
        
        if(profileFullName) {
          profileFullName.value = userData.profile?.full_name || userData.full_name || '';
        }
        if(profileEmail) {
          profileEmail.value = userData.email || userData.username || '';
        }
      } else {
        console.error('Failed to load profile');
      }
    } catch(error) {
      console.error('Error loading profile:', error);
    }
  }
  
  // Load recent orders
  async function loadRecentOrders(){
    try {
      const response = await fetch('/api/v2/orders/', {headers:authHeaders()});
      if(response.ok) {
        const data = await response.json();
        const orders = data.results || data;
        const recentOrders = orders.slice(0, 3); // Show only last 3 orders
        
        if(profileOrdersList) {
          if(recentOrders.length === 0) {
            profileOrdersList.innerHTML = '<p style="text-align:center;color:var(--muted);padding:20px">У вас пока нет заказов</p>';
          } else {
            profileOrdersList.innerHTML = recentOrders.map(orderTemplate).join('');
          }
        }
      }
    } catch(error) {
      console.error('Error loading recent orders:', error);
      if(profileOrdersList) {
        profileOrdersList.innerHTML = '<p style="text-align:center;color:var(--muted);padding:20px">Ошибка загрузки заказов</p>';
      }
    }
  }
  
  // Handle profile form submission
  if(profileForm) {
    profileForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const fullName = profileFullName.value.trim();
      
      if(!fullName) {
        profileStatus.textContent = 'ФИО не может быть пустым';
        return;
      }
      
      profileStatus.textContent = 'Сохранение...';
      
      try {
        console.log('Sending profile update request to /api/v2/me/update_profile/');
        console.log('Full name:', fullName);
        console.log('Auth headers:', authHeaders());
        
        const response = await fetch('/api/v2/me/update_profile/', {
          method: 'POST',
          headers: authHeaders(),
          credentials: 'same-origin',
          body: JSON.stringify({full_name: fullName})
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if(response.ok) {
          // Update localStorage
          storage.setFullName(fullName);
          profileStatus.textContent = 'Профиль успешно обновлен';
          showToast('Профиль обновлен', 'success');
          
          // Update header
          updateAuthUI();
        } else {
          const errorData = await response.json();
          profileStatus.textContent = 'Ошибка сохранения: ' + (errorData.detail || 'Неизвестная ошибка');
          showToast('Ошибка сохранения профиля', 'error');
        }
      } catch(error) {
        console.error('Profile update error:', error);
        profileStatus.textContent = 'Ошибка сохранения';
        showToast('Ошибка сохранения профиля', 'error');
      }
    });
  }
  
  // Handle logout
  if(logoutProfileBtn) {
    logoutProfileBtn.addEventListener('click', ()=>{
      storage.clear();
      updateAuthUI();
      showToast('Вы вышли из аккаунта', 'info');
      window.location.assign('/');
    });
  }
  
  // Load data
  loadProfile();
  loadRecentOrders();
}

function setupMyOrdersPage(){
  const ordersList = $('#ordersList');
  if(!ordersList) return;
  
  async function loadOrders(){
    console.log('Loading orders...');
    try {
      let response = await fetch('/api/v2/orders/', {headers:authHeaders()});
      console.log('Orders response status:', response.status);
      
      // If token expired, try to refresh
      if(response.status === 401) {
        try {
          const refreshResponse = await api.refreshToken();
          if(refreshResponse.access) {
            storage.setTokens(refreshResponse.access, refreshResponse.refresh);
            response = await fetch('/api/v2/orders/', {headers:authHeaders()});
          }
        } catch(refreshError) {
          console.error('Token refresh failed:', refreshError);
          // If refresh fails, try without auth
          response = await fetch('/api/v2/orders/', {headers:{'Content-Type':'application/json'}});
        }
      }
      
      if(!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Orders loaded:', data);
      const orders = data.results || data;
      if(orders.length === 0){
        ordersList.innerHTML = '<p style="text-align:center;color:var(--muted);padding:40px">У вас пока нет заказов</p>';
        return;
      }
      ordersList.innerHTML = orders.map(orderTemplate).join('');
      
      // Добавляем обработчики событий для кнопок оплаты
      const paymentButtons = ordersList.querySelectorAll('.payment-btn');
      paymentButtons.forEach(button => {
        button.addEventListener('click', function() {
          const orderId = this.getAttribute('data-order-id');
          const amount = this.getAttribute('data-amount');
          if (typeof showPaymentModal === 'function') {
            showPaymentModal(orderId, amount);
          } else {
            console.error('showPaymentModal function not available');
          }
        });
      });
    } catch(error) {
      console.error('Error loading orders:', error);
      ordersList.innerHTML = '<p style="text-align:center;color:var(--muted);padding:40px">Ошибка загрузки заказов: ' + error.message + '</p>';
    }
  }
  
  loadOrders();
}

// Purchase modal functions - make it global
window.openPurchaseModal = function(offerId) {
  console.log('Opening purchase modal for offer:', offerId);
  const modal = $('#modal-purchase');
  const offerDetails = $('#offerDetails');
  const selectedOfferId = $('#selectedOfferId');
  
  if (!modal || !offerDetails || !selectedOfferId) {
    console.error('Modal elements not found:', {modal, offerDetails, selectedOfferId});
    return;
  }
  
  // Store offer ID
  selectedOfferId.value = offerId;
  
  // Find offer data from current offers
  const offerCard = document.querySelector(`[data-id="${offerId}"]`);
  if (offerCard) {
    const title = offerCard.querySelector('h3').textContent;
    const blogger = offerCard.querySelector('p').textContent.replace('Блогер: ', '');
    const topic = offerCard.querySelectorAll('p')[1].textContent.replace('Тематика: ', '');
    const audience = offerCard.querySelectorAll('p')[2].textContent.replace('Аудитория: ', '');
    const price = offerCard.querySelector('strong').textContent;
    
    offerDetails.innerHTML = `
      <h4>${title}</h4>
      <p><strong>Блогер:</strong> ${blogger}</p>
      <p><strong>Тематика:</strong> ${topic}</p>
      <p><strong>Аудитория:</strong> ${audience}</p>
      <div class="offer-price">Цена: ${price}</div>
    `;
  }
  
  // Auto-fill user data if logged in
  const userEmail = storage.getEmail();
  const userFullName = storage.getFullName();
  
  if (userEmail) {
    const emailInput = modal.querySelector('input[name="email"]');
    if (emailInput) emailInput.value = userEmail;
  }
  
  if (userFullName) {
    const fullNameInput = modal.querySelector('input[name="full_name"]');
    if (fullNameInput) fullNameInput.value = userFullName;
  }
  
  // Show modal
  modal.setAttribute('aria-hidden', 'false');
  console.log('Modal should be visible now');
};

function setupPurchaseForm(){
  const form = $('#purchaseForm');
  if(!form) return;
  const status = $('#purchaseStatus');
  
  // Phone validation for purchase form
  const phoneInput = form.querySelector('input[name="phone"]');
  if (phoneInput) {
    phoneInput.addEventListener('input', function(e) {
      // Remove all non-digits
      let value = e.target.value.replace(/\D/g, '');
      
      // Limit to 11 digits maximum
      if (value.length > 11) {
        value = value.substring(0, 11);
      }
      
      // Add +7 prefix if it starts with 7 or 8
      if (value.startsWith('7') || value.startsWith('8')) {
        value = '+7' + value.substring(1);
      } else if (!value.startsWith('+7') && value.length > 0) {
        value = '+7' + value;
      }
      
      e.target.value = value;
    });
  }
  
  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    const offerId = $('#selectedOfferId').value;
    
    status.textContent = 'Отправка...';
    
    // Create order data
    const orderData = {
      offer_id: parseInt(offerId),
      full_name: data.full_name,
      email: data.email,
      phone: data.phone,
      description: data.description,
      order_type: 'offer'
    };
    
    try {
      // Try to send order
      let response = await fetch('/api/v2/orders/', {method:'POST', headers:authHeaders(), credentials:'same-origin', body:JSON.stringify(orderData)});
      
      // If token expired, try to refresh
      if(response.status === 401) {
        try {
          const refreshResponse = await api.refreshToken();
          if(refreshResponse.access) {
            storage.setTokens(refreshResponse.access, refreshResponse.refresh);
            response = await fetch('/api/v2/orders/', {method:'POST', headers:authHeaders(), credentials:'same-origin', body:JSON.stringify(orderData)});
          }
        } catch(refreshError) {
          console.error('Token refresh failed:', refreshError);
          response = await fetch('/api/v2/orders/', {method:'POST', headers:{'Content-Type':'application/json'}, credentials:'same-origin', body:JSON.stringify(orderData)});
        }
      }
      
      if(response.ok) {
        const result = await response.json();
        console.log('Purchase order created:', result);
        showToast('Заказ успешно оформлен! Ожидайте подтверждения от блогера.', 'success');
        
        // Close modal
        $('#modal-purchase').setAttribute('aria-hidden', 'true');
        form.reset();
        
        setTimeout(() => {
          window.location.assign('/my-orders/');
        }, 2000);
      } else {
        const errorText = await response.text();
        throw new Error(errorText || 'Error');
      }
    } catch(error) {
      console.error('Purchase order error:', error);
      status.textContent='Ошибка отправки. Попробуйте позже.'; 
      showToast('Ошибка оформления заказа: ' + error.message, 'error');
    }
  });
}

function orderTemplate(order){
  const statusMap = {
    'new': {text: 'Новый', class: 'new'},
    'paid': {text: 'Оплачен', class: 'paid'},
    'in_progress': {text: 'В работе', class: 'in_progress'},
    'done': {text: 'Выполнен', class: 'done'},
    'cancelled': {text: 'Отменен', class: 'cancelled'}
  };
  const status = statusMap[order.status] || {text: order.status, class: 'new'};
  const createdDate = new Date(order.created_at).toLocaleDateString('ru-RU');
  
  // Get offer info if available
  const offerInfo = order.offer && order.offer.blogger ? `
    <p><strong>Предложение:</strong> ${order.offer.title}</p>
    <p><strong>Блогер:</strong> ${order.offer.blogger.name}</p>
    <p><strong>Цена:</strong> ${order.offer.price.toLocaleString('ru-RU')} ₽</p>
  ` : '';
  
  // Payment status and button
  const paymentStatusMap = {
    'pending': {text: 'Не оплачено', class: 'pending'},
    'paid': {text: 'Оплачено', class: 'paid'},
    'failed': {text: 'Ошибка оплаты', class: 'failed'}
  };
  const paymentStatus = paymentStatusMap[order.payment_status] || {text: 'Неизвестно', class: 'pending'};
  
  const paymentButton = order.payment_status === 'pending' ? `
    <div class="payment-section">
      <div class="payment-status pending">
        <span class="payment-icon">⚠</span>
        <span>Не оплачено</span>
      </div>
      <button class="btn accent payment-btn" data-order-id="${order.id}" data-amount="${order.payment_amount || order.budget || 15000}">
        💳 Оплатить заказ
      </button>
    </div>
  ` : order.payment_status === 'paid' ? `
    <div class="payment-status paid">
      <span class="payment-icon">✓</span>
      <span>Оплачено</span>
    </div>
  ` : order.payment_status === 'failed' ? `
    <div class="payment-status failed">
      <span class="payment-icon">❌</span>
      <span>Ошибка оплаты</span>
    </div>
  ` : '';
  
  return `
    <div class="order-card">
      <div class="order-header">
        <span class="order-id">Заказ #${order.id}</span>
        <span class="order-status ${status.class}">${status.text}</span>
      </div>
      <div class="order-details">
        <p><strong>ФИО:</strong> ${order.full_name || 'Не указано'}</p>
        <p><strong>Email:</strong> ${order.email || 'Не указано'}</p>
        <p><strong>Телефон:</strong> ${order.phone || 'Не указано'}</p>
        ${offerInfo}
        <p><strong>Описание:</strong> ${order.description || 'Не указано'}</p>
        <p><strong>Дата создания:</strong> ${createdDate}</p>
        <p><strong>Статус оплаты:</strong> ${paymentStatus.text}</p>
        ${order.order_type === 'personal' ? '<span class="order-type">Персональный заказ</span>' : '<span class="order-type">Заказ по предложению</span>'}
        ${paymentButton}
      </div>
    </div>
  `;
}

console.log('Main.js loaded successfully');

document.addEventListener('DOMContentLoaded', ()=>{
  console.log('DOM loaded, starting setup...');
  renderSampleAds();
  setupGlobalSearch();
  setupBuyPage();
  setupOrderForm();
  setupAuthModals();
  setupPurchaseForm();
  setupNav();
  setupMyOrdersPage();
  setupProfilePage();
  updateAuthUI();
  const logoutBtn = $('#logoutBtn');
  if(logoutBtn){ logoutBtn.addEventListener('click', ()=>{ storage.clear(); updateAuthUI(); }); }
  // Dropdown menu handlers
  const userNameBtn = $('#userNameBtn');
  const userMenu = $('#userMenu');
  const menuProfile = $('#menuProfile');
  const menuOrders = $('#menuOrders');
  const menuAdmin = $('#menuAdmin');
  const menuManager = $('#menuManager');
  if(userNameBtn && userMenu){
    userNameBtn.addEventListener('click', (e)=>{ e.stopPropagation(); const open = userMenu.style.display==='block'; userMenu.style.display = open ? 'none' : 'block'; userNameBtn.setAttribute('aria-expanded', (!open).toString()); });
    document.addEventListener('click', ()=>{ userMenu.style.display='none'; userNameBtn.setAttribute('aria-expanded','false'); });
  }
  if(menuProfile){ menuProfile.addEventListener('click', ()=>{ userMenu.style.display='none'; window.location.assign('/profile/'); }); }
  if(menuOrders){ menuOrders.addEventListener('click', ()=>{ userMenu.style.display='none'; window.location.assign('/my-orders/'); }); }
  if(menuAdmin){ menuAdmin.addEventListener('click', ()=>{ userMenu.style.display='none'; window.location.assign('/admin-panel/'); }); }
  if(menuManager){ menuManager.addEventListener('click', ()=>{ userMenu.style.display='none'; window.location.assign('/manager/'); }); }
  console.log('All setup functions completed');
});

// Package details functionality
const packageData = {
  start: {
    name: 'Старт',
    price: '15 000 ₽',
    description: 'Идеальный пакет для начинающих предпринимателей и малого бизнеса. Помогает проверить гипотезы и найти эффективные каналы продвижения.',
    features: [
      'Анализ целевой аудитории',
      'Настройка рекламы в 2-3 каналах',
      'Базовые креативы и тексты',
      'Еженедельная отчетность',
      'Поддержка менеджера',
      'Срок выполнения: 7-10 дней'
    ]
  },
  growth: {
    name: 'Рост',
    price: '35 000 ₽',
    description: 'Для бизнеса, который хочет масштабировать успешные каналы и оптимизировать рекламные кампании для максимальной эффективности.',
    features: [
      'Все из пакета "Старт"',
      'Настройка рекламы в 5-7 каналах',
      'A/B тестирование креативов',
      'Оптимизация по конверсиям',
      'Еженедельная аналитика и корректировки',
      'Персональные рекомендации',
      'Срок выполнения: 14-21 день'
    ]
  },
  leader: {
    name: 'Лидер',
    price: '75 000 ₽',
    description: 'Максимальный охват и бренд-перформанс для крупного бизнеса. Комплексное продвижение с фокусом на узнаваемость бренда.',
    features: [
      'Все из пакета "Рост"',
      'Настройка рекламы в 10+ каналах',
      'Видео-креативы и брендинг',
      'Интеграция с CRM и аналитикой',
      'Ежедневный мониторинг и корректировки',
      'Персональный менеджер 24/7',
      'Месячная стратегия развития',
      'Срок выполнения: 21-30 дней'
    ]
  }
};

function showPackageModal(packageType) {
  const modal = $('#packageModal');
  const content = $('#packageContent');
  const data = packageData[packageType];
  
  if (!data) return;
  
  content.innerHTML = `
    <div class="package-details">
      <h2>${data.name}</h2>
      <div class="price">${data.price}</div>
      <p class="package-description">${data.description}</p>
      <ul class="package-features">
        ${data.features.map(feature => `<li>${feature}</li>`).join('')}
      </ul>
      <button class="package-order-btn" onclick="orderPackage('${packageType}')">
        Заказать пакет "${data.name}"
      </button>
    </div>
  `;
  
  modal.style.display = 'block';
}

function orderPackage(packageType) {
  // Закрываем модальное окно пакета
  $('#packageModal').style.display = 'none';
  
  // Открываем форму заказа с предзаполненными данными
  const data = packageData[packageType];
  if (data) {
    // Переходим на страницу заказа с параметрами пакета
    window.location.href = `/order/?package=${packageType}&name=${encodeURIComponent(data.name)}&price=${encodeURIComponent(data.price)}`;
  }
}

function closePackageModal() {
  $('#packageModal').style.display = 'none';
}

// Payment functionality
function showPaymentModal(orderId, amount) {
  const modal = document.createElement('div');
  modal.className = 'modal';
  modal.style.display = 'block';
  modal.innerHTML = `
    <div class="modal-content">
      <span class="close" onclick="closePaymentModal()">&times;</span>
      <div class="payment-form">
        <h3>Оплата заказа #${orderId}</h3>
        <p>Сумма к оплате: <strong>${amount} ₽</strong></p>
        
        <div class="form-group">
          <label for="cardNumber">Номер карты</label>
          <input type="text" id="cardNumber" placeholder="1234 5678 9012 3456" maxlength="19">
        </div>
        
        <div class="payment-row">
          <div class="form-group">
            <label for="expiryDate">Срок действия</label>
            <input type="text" id="expiryDate" placeholder="MM/YY" maxlength="5">
          </div>
          <div class="form-group">
            <label for="cvv">CVV</label>
            <input type="text" id="cvv" placeholder="123" maxlength="3">
          </div>
        </div>
        
        <div class="form-group">
          <label for="cardholderName">Имя держателя карты</label>
          <input type="text" id="cardholderName" placeholder="IVAN IVANOV">
        </div>
        
        <button class="pay-btn" onclick="processPayment(${orderId})">
          Оплатить ${amount} ₽
        </button>
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // Добавляем обработчики для форматирования
  const cardNumber = modal.querySelector('#cardNumber');
  const expiryDate = modal.querySelector('#expiryDate');
  
  cardNumber.addEventListener('input', function(e) {
    let value = e.target.value.replace(/\s/g, '').replace(/[^0-9]/gi, '');
    let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
    e.target.value = formattedValue;
  });
  
  expiryDate.addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length >= 2) {
      value = value.substring(0, 2) + '/' + value.substring(2, 4);
    }
    e.target.value = value;
  });
}

function closePaymentModal() {
  const modal = document.querySelector('.modal');
  if (modal) {
    modal.remove();
  }
}

function processPayment(orderId) {
  const cardNumber = $('#cardNumber').value.replace(/\s/g, '');
  const expiryDate = $('#expiryDate').value;
  const cvv = $('#cvv').value;
  const cardholderName = $('#cardholderName').value;
  
  // Простая валидация
  if (!cardNumber || cardNumber.length < 16) {
    showToast('Введите корректный номер карты', 'error');
    return;
  }
  
  if (!expiryDate || expiryDate.length < 5) {
    showToast('Введите корректную дату истечения', 'error');
    return;
  }
  
  if (!cvv || cvv.length < 3) {
    showToast('Введите корректный CVV код', 'error');
    return;
  }
  
  if (!cardholderName) {
    showToast('Введите имя держателя карты', 'error');
    return;
  }
  
  // Отключаем кнопку
  const payBtn = document.querySelector('.pay-btn');
  payBtn.disabled = true;
  payBtn.textContent = 'Обработка...';
  
  // Имитируем обработку платежа
  setTimeout(() => {
    // Отправляем запрос на сервер для обновления статуса заказа
    fetch(`/api/v2/orders/${orderId}/pay/`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        payment_method: 'card',
        card_number: cardNumber.substring(0, 4) + '****' + cardNumber.substring(cardNumber.length - 4),
        amount: document.querySelector('.payment-form p strong').textContent.replace(/[^\d]/g, '')
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showToast('Платеж успешно обработан!', 'success');
        closePaymentModal();
        // Обновляем список заказов
        if (typeof loadOrders === 'function') {
          loadOrders();
        }
      } else {
        showToast('Ошибка при обработке платежа', 'error');
        payBtn.disabled = false;
        payBtn.textContent = 'Оплатить';
      }
    })
    .catch(error => {
      console.error('Payment error:', error);
      showToast('Ошибка при обработке платежа', 'error');
      payBtn.disabled = false;
      payBtn.textContent = 'Оплатить';
    });
  }, 2000);
}

// Инициализация обработчиков пакетов
document.addEventListener('DOMContentLoaded', function() {
  // Обработчики для кнопок "Подробнее"
  document.querySelectorAll('.package-details-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const packageType = this.getAttribute('data-package');
      showPackageModal(packageType);
    });
  });
  
  // Обработчик для закрытия модального окна пакета
  const packageModal = $('#packageModal');
  if (packageModal) {
    const closeBtn = packageModal.querySelector('.close');
    if (closeBtn) {
      closeBtn.addEventListener('click', closePackageModal);
    }
    
    // Закрытие по клику вне модального окна
    packageModal.addEventListener('click', function(e) {
      if (e.target === packageModal) {
        closePackageModal();
      }
    });
  }
});


