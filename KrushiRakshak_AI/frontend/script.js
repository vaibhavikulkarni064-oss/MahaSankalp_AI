const API_BASE = window.KRUSHIRAKSHAK_API || 'https://krushirakshak-ai-api.onrender.com';
const $ = (selector, scope=document) => scope.querySelector(selector);
const $$ = (selector, scope=document) => [...scope.querySelectorAll(selector)];
let language = 'en';

function escapeHTML(value) { return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function showToast(message, isError=false) { const toast=$('#toast'); toast.textContent=message; toast.classList.toggle('error',isError); toast.classList.add('show'); window.setTimeout(()=>toast.classList.remove('show'),3500); }
function setStatus(id, message, isError=false) { const el=$('#'+id); el.textContent=message; el.classList.toggle('error',isError); }
function t(en,mr) { return language==='mr' ? mr : en; }
function translatePage(next) {
  language=next; document.documentElement.lang=next;
  $$('[data-'+next+']').forEach(el=>{ const value=el.getAttribute('data-'+next); if(value!==null) el.innerHTML=value; });
  const hidden=$('input[name="preferred_language"]'); if(hidden) hidden.value=next;
  $('#advisorySearch').placeholder=t('Search field notes… / सल्ले शोधा','सल्ले शोधा…');
}
async function api(path, options={}) {
  let response;
  try { response=await fetch(API_BASE+path,{credentials:'include',...options,headers:{...(options.body?{'Content-Type':'application/json'}:{}),...(options.headers||{})}}); }
  catch { throw new Error(t('Could not connect to the backend. Start FastAPI in the terminal, then retry.','बॅकएंडशी संपर्क झाला नाही. टर्मिनलमध्ये FastAPI सुरू करून पुन्हा प्रयत्न करा.')); }
  const payload=await response.json().catch(()=>({detail:'The server returned an unreadable response.'}));
  if(!response.ok) { const detail=payload.detail; throw new Error(Array.isArray(detail)?detail.map(x=>x.msg).join(', '):(detail||`Request failed (${response.status})`)); }
  return payload;
}
function formObject(form) { return Object.fromEntries(new FormData(form).entries()); }
function busy(form,on) { form.classList.toggle('loading',on); $$('button[type="submit"]',form).forEach(b=>{b.disabled=on;if(!b.dataset.originalText)b.dataset.originalText=b.textContent;b.textContent=on?t('Working…','प्रक्रिया सुरू आहे…'):b.dataset.originalText;}); }
function resultList(items) { return `<ul class="result-list">${items.map(item=>`<li>${escapeHTML(item)}</li>`).join('')}</ul>`; }
function showResult(title, body, reportId) {
  const detail=$('#reportDetail'); detail.hidden=false;
  detail.innerHTML=`<h3>${escapeHTML(title)}</h3>${body}<div class="result-notice">${escapeHTML(t('Saved to your current browser session. You can find it in Saved Reports below.','सध्याच्या ब्राउझर सत्रात जतन केले. खाली जतन केलेल्या अहवालांमध्ये ते पाहू शकता.'))} · #${escapeHTML(reportId)}</div>`;
  detail.scrollIntoView({behavior:'smooth',block:'nearest'});
}
$('#cropForm').addEventListener('submit', async event=>{
  event.preventDefault(); const form=event.currentTarget;
  if(!form.reportValidity()) return;
  const data=formObject(form); data.land_area=Number(data.land_area); data.crop_preference=data.crop_preference||null; data.constraints=data.constraints||null;
  busy(form,true); setStatus('cropStatus',t('Checking your details and saving the report…','माहिती तपासून अहवाल जतन करत आहोत…'));
  try {
    const response=await api('/crop-recommendations',{method:'POST',body:JSON.stringify(data)}); const result=response.result;
    const candidates=result.candidates.length?result.candidates.map(c=>`<div class="result-item"><b>${escapeHTML(c.crop)}</b><p>${escapeHTML(c.reasons.join('; '))}</p><p>${escapeHTML(c.consideration)}</p></div>`).join(''):`<p>${escapeHTML(t('No sample crop matched these rules. Try reviewing your inputs with an agriculture officer.','या नमुना नियमांनुसार पीक पर्याय मिळाला नाही. कृषी अधिकाऱ्यांसोबत माहिती तपासा.'))}</p>`;
    showResult(t('Your crop options','तुमचे पीक पर्याय'),`${candidates}<p>${escapeHTML(result.explanation)}</p><div class="result-notice">${escapeHTML(result.limitations)}</div>`,response.report_id);
    setStatus('cropStatus',t('Report saved successfully.','अहवाल यशस्वीरीत्या जतन झाला.')); showToast(t('Crop report saved','पीक अहवाल जतन झाला')); await loadReports();
  } catch(error) { setStatus('cropStatus',error.message,true); showToast(error.message,true); }
  finally { busy(form,false); }
});
$('#problemForm').addEventListener('submit', async event=>{
  event.preventDefault(); const form=event.currentTarget; if(!form.reportValidity())return;
  const data=formObject(form); data.symptoms=$$('input[name="symptoms"]:checked',form).map(x=>x.value);
  if(!data.symptoms.length){setStatus('problemStatus',t('Select at least one symptom.','किमान एक लक्षण निवडा.'),true);return;}
  busy(form,true);setStatus('problemStatus',t('Reviewing observations and saving…','निरीक्षणे तपासून जतन करत आहोत…'));
  try { const response=await api('/crop-problems',{method:'POST',body:JSON.stringify(data)});const r=response.result;
    showResult(t('Observation guidance','निरीक्षण मार्गदर्शन'),`<b>${escapeHTML(t('Possible causes to consider','विचारात घेण्यासारखी संभाव्य कारणे'))}</b>${resultList(r.possible_causes)}<b>${escapeHTML(t('What to check','काय तपासावे'))}</b>${resultList(r.observable_checks)}<b>${escapeHTML(t('Safe next steps','सुरक्षित पुढील पावले'))}</b>${resultList(r.guidance)}<div class="result-notice">${escapeHTML(r.notice)}</div>`,response.report_id);
    setStatus('problemStatus',t('Observation report saved.','निरीक्षण अहवाल जतन झाला.'));showToast(t('Problem report saved','समस्या अहवाल जतन झाला'));await loadReports();
  }catch(error){setStatus('problemStatus',error.message,true);showToast(error.message,true);}finally{busy(form,false);}
});
$('#irrigationForm').addEventListener('submit',async event=>{
  event.preventDefault();const form=event.currentTarget;if(!form.reportValidity())return;const data=formObject(form);busy(form,true);setStatus('irrigationStatus',t('Preparing guidance and saving…','सूचना तयार करून जतन करत आहोत…'));
  try{const response=await api('/irrigation-guidance',{method:'POST',body:JSON.stringify(data)});const r=response.result;
    showResult(t('Water-management considerations','पाणी व्यवस्थापन सूचना'),resultList(r.guidance)+`<div class="result-notice">${escapeHTML(r.notice)}</div>`,response.report_id);setStatus('irrigationStatus',t('Irrigation report saved.','सिंचन अहवाल जतन झाला.'));showToast(t('Irrigation report saved','सिंचन अहवाल जतन झाला'));await loadReports();
  }catch(error){setStatus('irrigationStatus',error.message,true);showToast(error.message,true);}finally{busy(form,false);}
});
function typeName(type){return ({crop:t('Crop guidance','पीक मार्गदर्शन'),problem:t('Crop problem','पीक समस्या'),irrigation:t('Irrigation','सिंचन')})[type]||type;}
function typeIcon(type){return ({crop:'🌱',problem:'🍃',irrigation:'💧'})[type]||'📄';}
async function loadReports(){const list=$('#reportsList');list.innerHTML=`<div class="loading-line">${escapeHTML(t('Loading saved reports…','जतन केलेले अहवाल लोड होत आहेत…'))}</div>`;
  try{const response=await api('/reports');$('#reportTotal').textContent=response.total;
    if(!response.items.length){list.innerHTML=`<div class="empty-state"><b>${escapeHTML(t('Your notebook is ready.','तुमची नोंदवही तयार आहे.'))}</b>${escapeHTML(t('No saved reports yet. Submit one of the tools above to see it here.','अजून अहवाल नाहीत. वरील साधनांपैकी एक वापरा; अहवाल येथे दिसेल.'))}</div>`;return;}
    list.innerHTML=response.items.map(item=>`<div class="report-row"><div class="report-main"><span class="report-icon">${typeIcon(item.type)}</span><div><b>${escapeHTML(item.title||typeName(item.type))}</b><small>${escapeHTML(typeName(item.type))} · #${escapeHTML(item.id)}</small></div></div><span>${escapeHTML(new Date(item.created_at).toLocaleString())}</span><span>${escapeHTML(t('Saved','जतन केले'))}</span><div class="report-actions"><button class="small-btn" data-open="${escapeHTML(item.id)}" data-type="${escapeHTML(item.type)}">${escapeHTML(t('Open','उघडा'))}</button><button class="small-btn delete" data-delete="${escapeHTML(item.id)}" data-type="${escapeHTML(item.type)}" aria-label="Delete report ${escapeHTML(item.id)}">${escapeHTML(t('Delete','हटवा'))}</button></div></div>`).join('');
  }catch(error){list.innerHTML=`<div class="empty-state"><b>${escapeHTML(t('Reports could not load','अहवाल लोड झाले नाहीत'))}</b>${escapeHTML(error.message)}<br><button class="small-btn" id="retryReports">${escapeHTML(t('Retry','पुन्हा प्रयत्न'))}</button></div>`;$('#retryReports')?.addEventListener('click',loadReports);$('#reportTotal').textContent='—';}}
$('#reportsList').addEventListener('click',async event=>{const open=event.target.closest('[data-open]');const del=event.target.closest('[data-delete]');if(open){try{const r=await api('/reports/'+encodeURIComponent(open.dataset.open));let body='';if(r.type==='crop'){const d=r.data;body=`<p><b>${escapeHTML(t('District','जिल्हा'))}:</b> ${escapeHTML(d.district)} · ${escapeHTML(d.soil_type)} · ${escapeHTML(d.season)}</p><b>${escapeHTML(t('Candidate crops','पीक पर्याय'))}</b>${resultList(JSON.parse(d.recommended_crops).map(c=>c.crop))}<p>${escapeHTML(d.explanation)}</p><div class="result-notice">${escapeHTML(d.limitations)}</div>`;}else if(r.type==='problem'){const d=r.data;body=`<p><b>${escapeHTML(d.crop_name)}</b> · ${escapeHTML(d.growth_stage)}</p><b>${escapeHTML(t('Symptoms','लक्षणे'))}</b>${resultList(JSON.parse(d.symptoms))}<b>${escapeHTML(t('Guidance','मार्गदर्शन'))}</b><pre>${escapeHTML(JSON.stringify(JSON.parse(d.guidance),null,2))}</pre>`;}else{const d=r.data;body=`<p><b>${escapeHTML(d.crop_name)}</b> · ${escapeHTML(d.soil_type)}</p><pre>${escapeHTML(JSON.stringify(JSON.parse(d.guidance),null,2))}</pre>`;}showResult(typeName(r.type),body,r.id);}catch(error){setStatus('reportsStatus',error.message,true);}}
  if(del){if(!confirm(t('Delete this saved report? This cannot be undone.','हा अहवाल हटवायचा आहे का? ही कृती पूर्ववत करता येणार नाही.')))return;try{await api('/reports/'+encodeURIComponent(del.dataset.delete),{method:'DELETE'});setStatus('reportsStatus',t('Report deleted.','अहवाल हटवला.'));$('#reportDetail').hidden=true;await loadReports();}catch(error){setStatus('reportsStatus',error.message,true);}}});
$('#refreshReports').addEventListener('click',loadReports);
$('#languageSelect').addEventListener('change',event=>translatePage(event.target.value));
$('#menuToggle').addEventListener('click',()=>$('#mainNav').classList.toggle('open'));
$$('#mainNav a').forEach(a=>a.addEventListener('click',()=>$('#mainNav').classList.remove('open')));
$('#advisorySearch').addEventListener('input',event=>{const query=event.target.value.toLowerCase().trim();let visible=0;$$('.advisory-card').forEach(card=>{const match=(card.dataset.search+' '+card.innerText).toLowerCase().includes(query);card.hidden=!match;if(match)visible++;});let no=$('#noAdvisories');if(!visible){if(!no){no=document.createElement('p');no.id='noAdvisories';no.className='no-results';$('#advisoryGrid').append(no);}no.textContent=t('No matching field notes found.','जुळणारे सल्ले आढळले नाहीत.');}else no?.remove();});
$('#privacyLink').addEventListener('click',()=>showToast(t('Privacy note: reports are scoped to a signed guest session. This prototype is not a production account system.','गोपनीयता: अहवाल साइन केलेल्या अतिथी सत्रापुरते मर्यादित आहेत. हे उत्पादन-स्तरावरील खाते प्रणाली नाही.')));
translatePage('en');loadReports();
