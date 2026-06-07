// Finance AI App Logic

// --- Utility helpers ---
const DEFAULT_CATEGORIES = ['General','Food','Transport','Entertainment','Utilities','Shopping','Bills','Health','Education','Travel'];
const RATES = { INR: 1, USD: 0.012, EUR: 0.011 };
let currentUser = null;
let pending2FACode = null;
let summaryChart = null;
let currentMonth = new Date().getMonth();
let currentYear = new Date().getFullYear();

function qs(id){ return document.getElementById(id); }
function escapeHtml(str){ return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[s])); }
function getJSON(key, fallback){ try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } }
function setJSON(key, value){ localStorage.setItem(key, JSON.stringify(value)); }
function getCurrency(){ return getJSON('finance_currency','INR'); }
function symbol(){ const c=getCurrency(); return c==='USD'?'$':c==='EUR'?'€':'₹'; }
function displayAmount(amount){ return symbol() + ((amount || 0) * (RATES[getCurrency()] || 1)).toFixed(2); }

async function hashPassword(password){
  if(window.crypto && crypto.subtle){
    const data = new TextEncoder().encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hashBuffer)).map(b=>b.toString(16).padStart(2,'0')).join('');
  }
  return btoa(password);
}

function userKey(name){ return 'finance_' + (currentUser || 'guest') + '_' + name; }
function getUsers(){ return getJSON('finance_users', []); }
function saveUsers(users){ setJSON('finance_users', users); }
function getTransactions(){ return getJSON(userKey('transactions'), []); }
function saveTransactions(items){ setJSON(userKey('transactions'), items); }
function getCategories(){ const cats = getJSON(userKey('categories'), null); return Array.isArray(cats) && cats.length ? cats : DEFAULT_CATEGORIES.slice(); }
function saveCategories(cats){ setJSON(userKey('categories'), cats); }
function getGoals(){ return getJSON(userKey('goals'), []); }
function saveGoals(goals){ setJSON(userKey('goals'), goals); }
function getBills(){ return getJSON(userKey('bills'), []); }
function saveBills(bills){ setJSON(userKey('bills'), bills); }
function getBudget(){ return Number(localStorage.getItem(userKey('budget')) || 0); }
function saveBudget(value){ localStorage.setItem(userKey('budget'), String(value)); }

// --- Auth ---
async function registerUser(){
  const username = qs('registerUsername').value.trim();
  const password = qs('registerPassword').value;
  const msg = qs('registerMsg');
  msg.className = 'mt-2 text-danger';
  msg.textContent = '';
  if(!username || !password){ msg.textContent='Please enter username and password.'; return; }
  const users = getUsers();
  if(users.some(u=>u.username.toLowerCase()===username.toLowerCase())){ msg.textContent='Username already exists.'; return; }
  users.push({ username, password: await hashPassword(password) });
  saveUsers(users);
  qs('registerUsername').value=''; qs('registerPassword').value='';
  msg.className = 'mt-2 text-success';
  msg.textContent='Registered successfully. You can now log in.';
}

async function loginUser(){
  const username = qs('loginUsername').value.trim();
  const password = qs('loginPassword').value;
  const msg = qs('loginMsg');
  msg.textContent='';
  const user = getUsers().find(u=>u.username.toLowerCase()===username.toLowerCase());
  if(!user || user.password !== await hashPassword(password)){ msg.textContent='Invalid username or password.'; return; }
  currentUser = user.username;
  pending2FACode = String(Math.floor(100000 + Math.random()*900000));
  qs('twoFaCodeInput').value='';
  qs('twoFaMsg').className='mt-2 text-muted';
  qs('twoFaMsg').textContent='Demo code: ' + pending2FACode;
  showModal('twoFaModal');
}

function verify2FA(){
  if(qs('twoFaCodeInput').value.trim() !== pending2FACode){ qs('twoFaMsg').className='mt-2 text-danger'; qs('twoFaMsg').textContent='Incorrect code. Please try again.'; return; }
  hideModal('twoFaModal'); pending2FACode=null; showDashboard();
}
function closeTwoFaModal(){ hideModal('twoFaModal'); pending2FACode=null; currentUser=null; }
function logoutUser(){ currentUser=null; qs('dashboardSection').classList.add('d-none'); qs('authSection').classList.remove('d-none'); qs('logoutBtn').classList.add('d-none'); }
function showModal(id){ const el=qs(id); el.style.display='block'; el.classList.add('show'); }
function hideModal(id){ const el=qs(id); el.style.display='none'; el.classList.remove('show'); }

// --- Dashboard init ---
function showDashboard(){
  qs('authSection').classList.add('d-none');
  qs('dashboardSection').classList.remove('d-none');
  qs('logoutBtn').classList.remove('d-none');
  qs('currentUserDisplay').textContent = currentUser;
  qs('transDate').value = new Date().toISOString().slice(0,10);
  fillCategorySelect();
  updateDashboard();
}

function fillCategorySelect(){
  const select = qs('transCategory');
  if(!select) return;
  select.innerHTML = getCategories().map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
}

function categorize(description){
  const d = description.toLowerCase();
  if(/grocery|food|restaurant|cafe|swiggy|zomato/.test(d)) return 'Food';
  if(/taxi|uber|ola|fuel|petrol|bus|train/.test(d)) return 'Transport';
  if(/movie|netflix|spotify|game/.test(d)) return 'Entertainment';
  if(/electric|water|internet|phone|utility/.test(d)) return 'Utilities';
  if(/doctor|medicine|hospital|pharmacy/.test(d)) return 'Health';
  if(/school|college|course|book/.test(d)) return 'Education';
  if(/rent|bill|loan|emi/.test(d)) return 'Bills';
  return 'General';
}

function saveTransaction(){
  const date = qs('transDate').value || new Date().toISOString().slice(0,10);
  const desc = qs('transDescription').value.trim();
  const amount = Number(qs('transAmount').value);
  const type = qs('transType').value;
  let category = qs('transCategory').value || categorize(desc);
  if(!desc || !amount || amount < 0){ qs('transMsg').className='mt-2 text-danger'; qs('transMsg').textContent='Please enter a valid description and amount.'; return; }
  const items = getTransactions();
  items.push({ id: Date.now(), date, desc, amount, type, category, recurring: qs('recurringCheckbox').checked });
  saveTransactions(items);
  qs('transDescription').value=''; qs('transAmount').value=''; qs('recurringCheckbox').checked=false;
  qs('transMsg').className='mt-2 text-success'; qs('transMsg').textContent='Transaction saved successfully.';
  updateDashboard();
}

function deleteTransaction(id){ saveTransactions(getTransactions().filter(t=>t.id!==id)); updateDashboard(); }
function filterTransactions(){ updateTransactionsTable(); }

function updateDashboard(){ updateSummary(); updateTransactionsTable(); updateBudgetUI(); updateGoalsUI(); updateBillsUI(); updateCalendar(); }

function updateSummary(){
  const transactions = getTransactions();
  const totals = {};
  let income=0, expense=0;
  transactions.forEach(t=>{ if(t.type==='income') income += t.amount; else { expense += t.amount; totals[t.category]=(totals[t.category]||0)+t.amount; } });
  const labels = Object.keys(totals);
  const values = Object.values(totals).map(v => v * (RATES[getCurrency()]||1));
  const ctx = qs('summaryChart').getContext('2d');
  if(summaryChart) summaryChart.destroy();
  summaryChart = new Chart(ctx, { type: 'doughnut', data: { labels, datasets: [{ data: values, backgroundColor: labels.map(()=>randomColor()) }] }, options: { plugins: { legend: { position: 'bottom' } } } });
  const net = income - expense;
  const topCategory = labels.length ? labels[values.indexOf(Math.max(...values))] : 'None';
  qs('summaryText').innerHTML = `<strong>Total Income:</strong> ${displayAmount(income)}<br><strong>Total Expense:</strong> ${displayAmount(expense)}<br><strong>Net:</strong> ${displayAmount(net)}<br><strong>Top Expense Category:</strong> ${escapeHtml(topCategory)}`;
}
function randomColor(){ return `hsl(${Math.floor(Math.random()*360)}, 70%, 55%)`; }

function updateTransactionsTable(){
  const tbody = qs('transactionsBody');
  const search = (qs('searchInput')?.value || '').toLowerCase();
  tbody.innerHTML = '';
  getTransactions().sort((a,b)=>new Date(b.date)-new Date(a.date)).forEach(t=>{
    if(search && !(t.desc.toLowerCase().includes(search)||t.category.toLowerCase().includes(search)||t.type.toLowerCase().includes(search))) return;
    tbody.insertAdjacentHTML('beforeend', `<tr><td>${escapeHtml(t.date)}</td><td>${escapeHtml(t.desc)}</td><td>${escapeHtml(t.type)}</td><td>${escapeHtml(t.category)}</td><td class="text-end">${displayAmount(t.amount)}</td><td><button class="btn btn-sm btn-outline-danger" onclick="deleteTransaction(${t.id})"><i class="fa fa-trash"></i></button></td></tr>`);
  });
}

// --- Budgets ---
function editBudget(){ const current=getBudget(); const val=Number(prompt('Monthly budget in INR:', current || '')); if(!isNaN(val) && val>=0){ saveBudget(val); updateBudgetUI(); } }
function updateBudgetUI(){
  const budget = getBudget();
  const spent = getTransactions().filter(t=>t.type==='expense').reduce((s,t)=>s+t.amount,0);
  const pct = budget ? (spent/budget)*100 : 0;
  const cls = pct>100?'over':pct>80?'near':'ok';
  qs('budgetContent').innerHTML = `<p><strong>Budget:</strong> ${displayAmount(budget)}</p><p><strong>Spent:</strong> ${displayAmount(spent)}</p><div class="progress"><div class="progress-bar ${cls}" style="width:${Math.min(pct,100)}%">${pct.toFixed(0)}%</div></div>`;
}

// --- Goals ---
function promptAddGoal(){ const name=prompt('Goal name:'); if(!name) return; const target=Number(prompt('Target amount in INR:')); if(!target||target<=0) return; const goals=getGoals(); goals.push({id:Date.now(), name, target, saved:0}); saveGoals(goals); updateGoalsUI(); }
function addContribution(id){ const goals=getGoals(); const g=goals.find(x=>x.id===id); if(!g) return; const amt=Number(prompt('Contribution amount in INR:')); if(amt>0){ g.saved+=amt; saveGoals(goals); updateGoalsUI(); } }
function deleteGoal(id){ saveGoals(getGoals().filter(g=>g.id!==id)); updateGoalsUI(); }
function updateGoalsUI(){
  const goals = getGoals();
  qs('goalsContent').innerHTML = goals.length ? goals.map(g=>{ const pct=g.target?(g.saved/g.target)*100:0; return `<div class="goal-item"><strong>${escapeHtml(g.name)}</strong><br>${displayAmount(g.saved)} / ${displayAmount(g.target)}<div class="progress my-1"><div class="progress-bar ok" style="width:${Math.min(pct,100)}%"></div></div><button class="btn btn-sm btn-outline-primary" onclick="addContribution(${g.id})">Add</button> <button class="btn btn-sm btn-outline-danger" onclick="deleteGoal(${g.id})"><i class="fa fa-trash"></i></button></div>`; }).join('') : '<p class="text-muted">No goals yet.</p>';
}

// --- Bills ---
function promptAddBill(){ const name=prompt('Bill name:'); if(!name) return; const amount=Number(prompt('Amount in INR:')); if(!amount||amount<=0) return; const due=prompt('Due date (YYYY-MM-DD):'); if(!due) return; const bills=getBills(); bills.push({id:Date.now(), name, amount, due}); saveBills(bills); updateBillsUI(); }
function markBillPaid(id){ const bills=getBills(); const bill=bills.find(b=>b.id===id); if(!bill) return; const tx=getTransactions(); tx.push({id:Date.now(), date:bill.due, desc:bill.name + ' bill', amount:bill.amount, type:'expense', category:'Bills', recurring:false}); saveTransactions(tx); saveBills(bills.filter(b=>b.id!==id)); updateDashboard(); }
function deleteBill(id){ saveBills(getBills().filter(b=>b.id!==id)); updateBillsUI(); }
function updateBillsUI(){
  const bills=getBills().sort((a,b)=>new Date(a.due)-new Date(b.due));
  qs('billsContent').innerHTML = bills.length ? bills.map(b=>`<div class="bill-item"><strong>${escapeHtml(b.name)}</strong><br>${displayAmount(b.amount)} · Due ${escapeHtml(b.due)}<br><button class="btn btn-sm btn-outline-success" onclick="markBillPaid(${b.id})"><i class="fa fa-check"></i></button> <button class="btn btn-sm btn-outline-danger" onclick="deleteBill(${b.id})"><i class="fa fa-trash"></i></button></div>`).join('') : '<p class="text-muted">No bills yet.</p>';
}

// --- Calendar ---
function updateCalendar(){
  const header=qs('calendarHeader'); const table=qs('calendarTable'); table.innerHTML='';
  const months=['January','February','March','April','May','June','July','August','September','October','November','December'];
  header.textContent=`${months[currentMonth]} ${currentYear}`;
  const first=new Date(currentYear,currentMonth,1).getDay(); const days=new Date(currentYear,currentMonth+1,0).getDate();
  table.innerHTML='<thead><tr>'+['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map(d=>`<th>${d}</th>`).join('')+'</tr></thead>';
  const body=document.createElement('tbody'); let day=1; const tx=getTransactions();
  for(let r=0;r<6;r++){ const tr=document.createElement('tr'); for(let c=0;c<7;c++){ const td=document.createElement('td'); if((r===0&&c<first)||day>days){ td.className='disabled'; } else { const date=`${currentYear}-${String(currentMonth+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`; const daily=tx.filter(t=>t.date===date); td.innerHTML=`<strong>${day}</strong>`; if(daily.length){ td.classList.add('has-transactions'); const total=daily.reduce((s,t)=>s+t.amount,0); td.innerHTML+=`<div class="small">${displayAmount(total)}</div>`; td.onclick=()=>showDayTransactions(date); } day++; } tr.appendChild(td); } body.appendChild(tr); }
  table.appendChild(body);
}
function changeMonth(delta){ currentMonth+=delta; if(currentMonth<0){currentMonth=11;currentYear--;} if(currentMonth>11){currentMonth=0;currentYear++;} updateCalendar(); }
function showDayTransactions(date){ const list=getTransactions().filter(t=>t.date===date); qs('dayModalDate').textContent=date; qs('dayTransactionsContent').innerHTML=list.length?'<ul class="list-group">'+list.map(t=>`<li class="list-group-item"><strong>${escapeHtml(t.desc)}</strong> (${escapeHtml(t.category)}) - ${displayAmount(t.amount)}</li>`).join('')+'</ul>':'<p>No transactions.</p>'; showModal('dayTransactionsModal'); }
function closeDayModal(){ hideModal('dayTransactionsModal'); }

// --- Categories modal ---
function showCategoriesModal(){ updateCategoriesUI(); showModal('categoriesModal'); }
function closeCategoriesModal(){ hideModal('categoriesModal'); }
function updateCategoriesUI(){ qs('categoriesList').innerHTML=getCategories().map((c,i)=>`<li class="list-group-item category-item"><span>${escapeHtml(c)}</span><span><button class="btn btn-sm btn-outline-danger" onclick="deleteCategory(${i})"><i class="fa fa-trash"></i></button></span></li>`).join(''); }
function addCategory(){ const input=qs('newCategoryInput'); const name=input.value.trim(); if(!name) return; const cats=getCategories(); if(!cats.includes(name)){ cats.push(name); saveCategories(cats); fillCategorySelect(); updateCategoriesUI(); input.value=''; } }
function deleteCategory(index){ const cats=getCategories(); cats.splice(index,1); saveCategories(cats); fillCategorySelect(); updateCategoriesUI(); }

// --- CSV and PDF ---
function exportCSV(){ const rows=['date,description,type,category,amount']; getTransactions().forEach(t=>rows.push(`${t.date},${t.desc},${t.type},${t.category},${t.amount}`)); const blob=new Blob([rows.join('\n')],{type:'text/csv'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='transactions.csv'; a.click(); URL.revokeObjectURL(url); }
function importCSV(event){ const file=event.target.files[0]; if(!file) return; const reader=new FileReader(); reader.onload=e=>{ const lines=e.target.result.split(/\r?\n/).slice(1); const tx=getTransactions(); lines.forEach(line=>{ if(!line.trim()) return; const [date,desc,type,category,amount]=line.split(','); tx.push({id:Date.now()+Math.random(), date, desc, type, category, amount:Number(amount), recurring:false}); }); saveTransactions(tx); updateDashboard(); }; reader.readAsText(file); }
function generatePDF(){ const { jsPDF } = window.jspdf; const doc=new jsPDF(); doc.setFontSize(16); doc.text('Finance AI Transaction Report',10,10); doc.setFontSize(10); let y=20; getTransactions().forEach(t=>{ doc.text(`${t.date} | ${t.desc} | ${t.type} | ${t.category} | ₹${Number(t.amount).toFixed(2)}`,10,y); y+=7; if(y>280){doc.addPage();y=10;} }); doc.save('finance-report.pdf'); }

if('serviceWorker' in navigator){ window.addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{})); }
