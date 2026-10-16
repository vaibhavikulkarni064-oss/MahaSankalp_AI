"use strict";
const OPTS = {
  subjects: ["Mathematics","Science","Computer Science","English","Economics","Arts","Social Studies"],
  interests: ["Programming","Data & statistics","Artificial intelligence","Security & hacking","Design & creativity","Networks & cloud","Business & strategy","Marketing & social media","Entrepreneurship","Web development"],
  skills: ["Python","JavaScript","SQL","Excel","Communication","Design tools","Networking","Problem solving","Writing","Leadership","Statistics","Linux"],
  industries: ["Technology","Finance","Healthcare","Education","Media","Manufacturing","Government","Startups"]
};
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
let step = 1, busy = false;

function toast(msg, bad) { const d = document.createElement("div"); if (bad) d.className = "e"; d.textContent = msg; $("#toast").append(d); setTimeout(() => d.remove(), 4500); }
const API_BASE = "http://127.0.0.1:8004";
async function api(path, opts = {}) {
  let res;
  try { res = await fetch(`${API_BASE}${path}`, { credentials: "include", headers: { "Content-Type": "application/json" }, ...opts }); }
  catch { throw new Error("Cannot reach the server. Check that it is running and try again."); }
  let body = null; try { body = await res.json(); } catch { /* empty or non-JSON */ }
  if (!res.ok) {
    let m = "Something went wrong. Please try again.";
    if (body && typeof body.detail === "string") m = body.detail;
    else if (body && Array.isArray(body.detail)) m = body.detail.map(e => `${(e.loc || []).slice(-1)[0]}: ${e.msg}`).join("; ");
    const err = new Error(m); err.status = res.status; err.fields = body && Array.isArray(body.detail) ? body.detail : null; throw err;
  }
  if (body === null) throw new Error("The server returned an empty response.");
  return body;
}

// ---------- views ----------
function show(v) {
  $$(".view").forEach(s => s.hidden = s.id !== v);
  $$("nav a").forEach(a => a.classList.toggle("on", a.dataset.v === v));
  $("#links").classList.remove("open"); $("#menu").setAttribute("aria-expanded", "false");
  if (v === "explore") loadCareers(); if (v === "reports") loadHistory();
  window.scrollTo(0, 0);
}
document.addEventListener("click", e => { const a = e.target.closest("[data-v]"); if (a) { e.preventDefault(); show(a.dataset.v); history.replaceState(null, "", "#" + a.dataset.v); } });
$("#menu").onclick = () => { const o = $("#links").classList.toggle("open"); $("#menu").setAttribute("aria-expanded", o); };

// ---------- form ----------
$$(".chips").forEach(c => OPTS[c.dataset.opts].forEach(o => { const l = document.createElement("label"); l.innerHTML = `<input type="checkbox" name="${c.dataset.name}" value="${esc(o)}">${esc(o)}`; c.append(l); }));
const f = $("#form");
function showStep() {
  $$("fieldset", f).forEach(s => s.hidden = +s.dataset.step !== step);
  $("#barfill").style.width = (step * 33.4) + "%"; $("#stepLabel").textContent = `Step ${step} of 3`;
  $("#back").style.visibility = step === 1 ? "hidden" : "visible"; $("#next").hidden = step === 3; $("#submit").hidden = step !== 3;
}
const val = n => (f.elements[n].value || "").trim();
const checked = n => $$(`input[name="${n}"]:checked`, f).map(i => i.value);
function setErr(n, m) { const e = $(`.err[data-for="${n}"]`); if (e) e.textContent = m || ""; const i = f.elements[n]; if (i && i.classList) i.classList.toggle("bad", !!m); }
function validate(s) {
  const rules = { 1: [["name", () => val("name").length >= 2, "Enter your full name (2+ characters)."], ["age_range", () => val("age_range"), "Choose an age range."], ["education_level", () => val("education_level"), "Choose your education level."], ["field_of_study", () => val("field_of_study"), "Enter your stream or field."]],
    2: [["interests", () => checked("interests").length, "Pick at least one interest."]],
    3: [["work_style", () => val("work_style"), "Choose a work style."], ["career_goals", () => val("career_goals").length >= 10, "Describe your goals in at least 10 characters."]] };
  let ok = true; rules[s].forEach(([n, t, m]) => { const good = !!t(); setErr(n, good ? "" : m); if (!good) ok = false; }); return ok;
}
$("#next").onclick = () => { if (validate(step)) { step++; showStep(); } };
$("#back").onclick = () => { step--; showStep(); };
function payload() {
  return { name: val("name"), age_range: val("age_range"), education_level: val("education_level"), field_of_study: val("field_of_study"),
    favourite_subjects: checked("favourite_subjects"), interests: checked("interests"), existing_skills: checked("existing_skills"), desired_skills: checked("desired_skills"),
    work_style: val("work_style"), career_goals: val("career_goals"), industries: checked("industries"), experience: val("experience") || null };
}
f.addEventListener("submit", async e => {
  e.preventDefault(); if (busy) return;
  for (const s of [1, 2, 3]) if (!validate(s)) { step = s; showStep(); return; }
  busy = true; $("#submit").disabled = true; $("#formError").hidden = true; $("#formArea").hidden = true; $("#loading").hidden = false;
  try { const r = await api("/analyze", { method: "POST", body: JSON.stringify(payload()) }); renderReport(r); show("results"); toast("Report saved."); }
  catch (err) {
    $("#formArea").hidden = false; const box = $("#formError"); box.hidden = false; box.textContent = err.message + " Your answers are kept; press Analyze to retry.";
    if (err.fields) err.fields.forEach(d => { const n = (d.loc || []).slice(-1)[0]; setErr(n, d.msg); });
    toast("Could not generate report.", true);
  } finally { busy = false; $("#submit").disabled = false; $("#loading").hidden = true; }
});
showStep();

// ---------- report ----------
const tags = a => (a || []).map(x => `<span class="tag">${esc(x)}</span>`).join("") || '<span class="muted">None identified from your answers.</span>';
function renderReport(r) {
  const R = r.recommended;
  $("#report").innerHTML = `
  <div class="top"><p>Hello, ${esc(r.name)}. Here is your preliminary report (#${esc(r.id)}).</p><h2>${esc(R.career)}</h2><p>${esc(R.explanation)}</p>
   <div class="score"><div class="pill"><b>${esc(R.score)}%</b>Suitability score</div><div class="pill"><b>${esc(r.completeness)}%</b>Profile completeness</div></div></div>
  <p class="muted">${esc(r.score_note)}</p><div class="note">${esc(r.disclaimer)}</div>
  <h3>Other options to explore</h3><div class="grid">${r.alternatives.map(a => `<div class="card"><b>${esc(a.career)}</b><div class="meter"><i style="width:${+a.score}%"></i></div><small>${esc(a.score)}% match</small><p>${esc(a.explanation)}</p></div>`).join("")}</div>
  <div class="grid"><div class="card"><h3>Strengths you already show</h3>${tags(R.strengths)}<h3>Skills to improve</h3>${tags(R.skills_to_improve)}<h3>Education guidance</h3><p>${esc(R.education)}</p></div>
  <div class="card"><h3>Learning topics</h3><ul class="t">${R.topics.map(x => `<li>${esc(x)}</li>`).join("")}</ul><h3>Beginner project ideas</h3><ul class="t">${R.projects.map(x => `<li>${esc(x)}</li>`).join("")}</ul></div></div>
  <h3>Your 30-day roadmap</h3><div class="grid">${r.roadmap.map(w => `<div class="card"><b>${esc(w.week)}</b><p>${esc(w.focus)}</p><ul class="t">${w.tasks.map(t => `<li>${esc(t)}</li>`).join("")}</ul></div>`).join("")}</div>
  <h3>Next steps</h3><ul class="t">${r.next_steps.map(x => `<li>${esc(x)}</li>`).join("")}</ul>
  <div class="row" style="justify-content:flex-start"><button class="btn" data-v="assess">Retake assessment</button><button class="btn ghost" data-v="reports">View previous reports</button></div>`;
}

// ---------- explore / history ----------
async function loadCareers() {
  const box = $("#careerList"); if (box.dataset.done) return;
  try { const list = await api("/careers"); box.innerHTML = list.map(c => `<div class="card"><h3>${esc(c.career_name)}</h3><p>${esc(c.description)}</p><b>Key skills</b><div>${tags(c.required_skills)}</div><b>Learning path</b><ul class="t">${c.recommended_learning_topics.map(t => `<li>${esc(t)}</li>`).join("")}</ul><b>Education</b><p>${esc(c.education_guidance)}</p></div>`).join(""); box.dataset.done = 1; }
  catch (e) { box.innerHTML = `<div class="alert">${esc(e.message)}</div>`; }
}
async function loadHistory() {
  const box = $("#historyList");
  try {
    const list = await api("/assessments");
    if (!list.length) { box.innerHTML = '<p>No saved reports yet.</p><button class="btn" data-v="assess">Start Career Assessment</button>'; return; }
    box.innerHTML = list.map(r => `<div class="card hist"><div><b>${esc(r.recommended_career)}</b> (${esc(r.suitability_score)}%)<br><small class="muted">${esc(r.name)} - ${esc(new Date(r.created_at).toLocaleString())}</small></div><div><button class="btn" data-open="${+r.id}">Open</button> <button class="btn danger" data-del="${+r.id}">Delete</button></div></div>`).join("") + '<button class="btn danger" id="delAll">Delete all my reports</button>';
  } catch (e) { box.innerHTML = `<div class="alert">${esc(e.message)}</div>`; }
}
$("#historyList").addEventListener("click", async e => {
  const o = e.target.closest("[data-open]"), d = e.target.closest("[data-del]"), all = e.target.id === "delAll";
  try {
    if (o) { renderReport(await api("/assessments/" + o.dataset.open)); show("results"); }
    else if (d && confirm("Delete this report permanently?")) { await api("/assessments/" + d.dataset.del, { method: "DELETE" }); toast("Report deleted."); loadHistory(); }
    else if (all && confirm("Delete ALL your reports permanently?")) { await api("/assessments", { method: "DELETE" }); toast("All reports deleted."); loadHistory(); }
  } catch (err) { toast(err.message, true); }
});
show((location.hash || "#home").slice(1) in { home: 1, assess: 1, explore: 1, reports: 1, about: 1 } ? location.hash.slice(1) || "home" : "home");
