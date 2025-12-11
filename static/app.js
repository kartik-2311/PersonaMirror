async function postForm(url, data) {
  const formData = new FormData();
  for (const k in data) {
    const v = data[k];
    if (Array.isArray(v)) v.forEach(x => formData.append(k, x));
    else formData.append(k, v);
  }
  const res = await fetch(url, { method: 'POST', body: formData });
  return res.json();
}

document.getElementById('loadSample').onclick = async () => {
  const subject = document.getElementById('sampleSubject').value || 'sample';
  const r = await postForm('/ingest/sample', { subject_id: subject });
  document.getElementById('sampleStatus').innerText = JSON.stringify(r);
};

document.getElementById('ingestFiles').onclick = async () => {
  const subject = document.getElementById('filesSubject').value || 'me';
  const filesInput = document.getElementById('filesInput');
  const files = filesInput.files;
  const formData = new FormData();
  formData.append('subject_id', subject);
  for (const f of files) formData.append('files', f);
  const res = await fetch('/ingest/files', { method: 'POST', body: formData });
  const r = await res.json();
  document.getElementById('filesStatus').innerText = JSON.stringify(r);
};

document.getElementById('send').onclick = async () => {
  const subject = document.getElementById('chatSubject').value || 'sample';
  const message = document.getElementById('message').value || '';
  const voiceId = document.getElementById('voiceId').value || '';
  const voice = document.getElementById('voiceToggle').checked;
  const res = await fetch('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ subject_id: subject, message, voice, voice_id: voiceId }) });
  const r = await res.json();
  document.getElementById('reply').innerText = r.reply;
  document.getElementById('citations').innerText = JSON.stringify(r.citations);
  const audio = document.getElementById('audio');
  if (r.audio_url) {
    audio.src = r.audio_url;
    audio.style.display = 'block';
  } else {
    audio.removeAttribute('src');
    audio.style.display = 'none';
  }
};

const factsTableBody = () => document.querySelector('#factsTable tbody');
const prefsTableBody = () => document.querySelector('#prefsTable tbody');

function addFactRow(f = { type: '', value: '', confidence: 0.7, source: '' }) {
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td contenteditable="true">${f.type}</td>
    <td contenteditable="true">${f.value}</td>
    <td contenteditable="true">${f.confidence}</td>
    <td contenteditable="true">${f.source}</td>
    <td><button class="del">Delete</button></td>
  `;
  tr.querySelector('.del').onclick = () => tr.remove();
  factsTableBody().appendChild(tr);
}

function addPrefRow(p = { category: '', value: '', confidence: 0.7, source: '' }) {
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td contenteditable="true">${p.category}</td>
    <td contenteditable="true">${p.value}</td>
    <td contenteditable="true">${p.confidence}</td>
    <td contenteditable="true">${p.source}</td>
    <td><button class="del">Delete</button></td>
  `;
  tr.querySelector('.del').onclick = () => tr.remove();
  prefsTableBody().appendChild(tr);
}

function collectTableRows(tbody, keys) {
  const rows = [];
  for (const tr of tbody.querySelectorAll('tr')) {
    const tds = tr.querySelectorAll('td');
    const obj = {};
    for (let i = 0; i < keys.length; i++) obj[keys[i]] = tds[i].innerText.trim();
    if (keys.includes('confidence')) obj['confidence'] = parseFloat(obj['confidence'] || '0.7');
    rows.push(obj);
  }
  return rows;
}

document.getElementById('addFact').onclick = () => addFactRow();
document.getElementById('addPref').onclick = () => addPrefRow();

document.getElementById('loadFacts').onclick = async () => {
  const subject = document.getElementById('factsSubject').value || 'sample';
  const res = await fetch(`/facts/${encodeURIComponent(subject)}`);
  const r = await res.json();
  factsTableBody().innerHTML = '';
  prefsTableBody().innerHTML = '';
  (r.facts || []).forEach(addFactRow);
  (r.preferences || []).forEach(addPrefRow);
  document.getElementById('factsStatus').innerText = `Loaded ${r.facts?.length || 0} facts, ${r.preferences?.length || 0} preferences`;
};

document.getElementById('saveFacts').onclick = async () => {
  const subject = document.getElementById('factsSubject').value || 'sample';
  const facts = collectTableRows(factsTableBody(), ['type', 'value', 'confidence', 'source']);
  const prefs = collectTableRows(prefsTableBody(), ['category', 'value', 'confidence', 'source']);
  const res = await fetch(`/facts/${encodeURIComponent(subject)}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ facts, preferences: prefs }) });
  const r = await res.json();
  document.getElementById('factsStatus').innerText = `Saved. Facts: ${r.facts_count}, Preferences: ${r.preferences_count}`;
};
