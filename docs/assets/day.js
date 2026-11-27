/* Daily page behaviour. Reads the lesson JSON embedded in <script id="data">. */
(function(){
  const D = JSON.parse(document.getElementById('data').textContent);
  const $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

  /* ---------- speech ---------- */
  const synth = window.speechSynthesis;
  let voice = null;
  function pickVoice(){
    if(!synth) return;
    const vs = synth.getVoices().filter(v => /^en[-_]/i.test(v.lang));
    voice = vs.find(v => /en[-_]US/i.test(v.lang) && /Google|Samantha|Aria|Jenny|Natural/i.test(v.name))
         || vs.find(v => /en[-_]US/i.test(v.lang)) || vs[0] || null;
  }
  if(synth){ pickVoice(); synth.onvoiceschanged = pickVoice; }
  function speak(text, rate){
    if(!synth){ alert('這個瀏覽器不支援語音播放'); return; }
    synth.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US'; if(voice) u.voice = voice; u.rate = rate || 0.9;
    synth.speak(u);
  }
  document.addEventListener('click', e => {
    const b = e.target.closest('[data-say]');
    if(b){ e.stopPropagation(); speak(b.dataset.say, parseFloat(b.dataset.rate||'0.9')); }
  });
  if(!synth){ $('readAll').style.display='none'; $('stopAll').style.display='none'; }
  $('readAll').onclick = () => speak(D.title + '. ' + D.article.map(p => p.replace(/\{\d+\|([^}]+)\}/g,'$1')).join(' '), 0.95);
  $('stopAll').onclick = () => synth && synth.cancel();

  /* ---------- header & article ---------- */
  $('meta').textContent = D.date_zh + '｜' + D.topic + '｜改寫自 ' + D.source.outlet;
  $('title').textContent = D.title;
  const zh = D.article_zh || [];
  $('article').innerHTML = D.article.map((p,k) =>
    '<p>' + esc(p).replace(/\{(\d+)\|([^}]+)\}/g, (m,i,w) =>
      `<span class="vw" tabindex="0" data-i="${i}">${w}<sup>${i}</sup></span>`) + '</p>' +
    (zh[k] ? `<details class="tr"><summary>中文翻譯</summary><div class="tr-body">${esc(zh[k])}</div></details>` : '')).join('');
  $('summary').textContent = D.summary_zh;
  $('srcline').innerHTML = '原始新聞：' + esc(D.source.outlet) + '〈' + esc(D.source.headline) + '〉' +
    esc(D.source.author) + '，' + esc(D.source.date) + '<br><a href="' + esc(D.source.url) + '" target="_blank" rel="noopener">' + esc(D.source.url) + '</a>';

  /* ---------- cards ---------- */
  function mark(sentence, word){
    const parts = word.split(/\s+/).map(w => w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'));
    const re = new RegExp('\\b(' + parts[0] + '\\w*' + parts.slice(1).map(p => '\\s+' + p).join('') + ')', 'i');
    return esc(sentence).replace(re, '<b>$1</b>');
  }
  $('cards').innerHTML = D.words.map((w,k) => `
    <div class="card" id="w${k+1}">
      <div class="word"><span class="n">${k+1}</span><span class="w en">${esc(w.word)}</span>
        <button class="say" title="發音" aria-label="播放發音" data-say="${esc(w.word)}">🔊</button>
        <button class="say" title="慢速" aria-label="慢速發音" data-say="${esc(w.word)}" data-rate="0.55">🐢</button>
        <span class="r">${esc(w.kk)}</span><span class="pos">${esc(w.pos)}</span><span class="m">${esc(w.zh)}</span></div>
      <div class="row"><span class="k">英文解釋</span><span class="en">${esc(w.def)}</span></div>
      <div class="row"><span class="k">文章句</span><span class="en">${mark(w.sentence, w.word)}</span></div>
      <div class="row"><span class="k">常見搭配</span><span class="en">${w.collocations.map(esc).join(' ／ ')}</span></div>
      <div class="row"><span class="k">真實例句</span><span><span class="en">${mark(w.example, w.word)}</span><button class="say sm" aria-label="播放例句" data-say="${esc(w.example)}">🔊</button><br><span class="src">出處：${esc(w.example_src)}</span></span></div>
      <div class="row"><span class="k">近義・詞形</span><span class="en">${esc(w.related)}</span></div>
    </div>`).join('');

  /* ---------- popover ---------- */
  const pop = $('pop'); let cur = null, hideT = null;
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  function show(el){
    clearTimeout(hideT);
    const i = +el.dataset.i, w = D.words[i-1];
    pop.innerHTML = `<div class="h"><span class="pw en">${esc(w.word)}</span>
        <button class="say" aria-label="播放發音" data-say="${esc(w.word)}">🔊</button>
        <span class="pk">${esc(w.kk)}</span><span class="pos">${esc(w.pos)}</span></div>
      <div class="pz">${esc(w.zh)}</div><div class="pd en">${esc(w.def)}</div>
      <a class="more" href="#w${i}" data-go="${i}">看單字卡 ↓</a>`;
    if(cur) cur.classList.remove('on'); cur = el; el.classList.add('on');
    pop.classList.add('show');
    const r = el.getBoundingClientRect(), pw = pop.offsetWidth, ph = pop.offsetHeight;
    let left = r.left + window.scrollX + r.width/2 - pw/2;
    left = Math.max(window.scrollX + 12, Math.min(left, window.scrollX + document.documentElement.clientWidth - pw - 12));
    let top = r.bottom + window.scrollY + 8;
    if(r.bottom + ph + 16 > window.innerHeight && r.top > ph + 16) top = r.top + window.scrollY - ph - 8;
    pop.style.left = left + 'px'; pop.style.top = top + 'px';
  }
  function hide(){ pop.classList.remove('show'); if(cur){ cur.classList.remove('on'); cur = null; } }
  function hideLater(){ hideT = setTimeout(hide, 250); }
  document.querySelectorAll('.vw').forEach(el => {
    if(fine){ el.addEventListener('mouseenter', () => show(el)); el.addEventListener('mouseleave', hideLater); }
    el.addEventListener('click', e => { e.stopPropagation(); (cur === el && !fine) ? hide() : show(el); });
    el.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' '){ e.preventDefault(); show(el); } if(e.key==='Escape') hide(); });
  });
  pop.addEventListener('mouseenter', () => clearTimeout(hideT));
  pop.addEventListener('mouseleave', () => fine && hideLater());
  pop.addEventListener('click', e => {
    e.stopPropagation();
    const s = e.target.closest('[data-say]');
    if(s){ speak(s.dataset.say, parseFloat(s.dataset.rate||'0.9')); return; }
    const g = e.target.closest('[data-go]');
    if(g){ e.preventDefault(); hide(); const c = $('w'+g.dataset.go); c.scrollIntoView({behavior:'smooth'}); c.classList.remove('flash'); void c.offsetWidth; c.classList.add('flash'); }
  });
  document.addEventListener('click', hide);
  document.addEventListener('keydown', e => e.key==='Escape' && hide());
  window.addEventListener('resize', hide);

  /* ---------- quiz ---------- */
  const bank = D.words.map((w,k) => ({w:w.word, i:k+1}));
  const shuffled = bank.slice().sort((a,b) => ((a.i*7+3)%11) - ((b.i*7+3)%11));
  const opts = '<option value="">— 選 —</option>' + shuffled.map(o => `<option value="${o.i}">${esc(o.w)}</option>`).join('');
  $('quiz').innerHTML = D.quiz.map((q,k) =>
    `<li data-a="${q.a}" data-form="${esc(q.form || D.words[q.a-1].word)}">` +
    esc(q.q).replace('___', `<select aria-label="第 ${k+1} 題">${opts}</select>`) + '<span class="fb"></span></li>').join('');
  function check(reveal){
    let ok = 0;
    $('quiz').querySelectorAll('li').forEach(li => {
      const s = li.querySelector('select'), fb = li.querySelector('.fb');
      if(reveal) s.value = li.dataset.a;
      const right = s.value === li.dataset.a;
      if(!s.value){ li.classList.remove('ok','ng'); fb.textContent = '（未作答）'; return; }
      li.classList.toggle('ok', right); li.classList.toggle('ng', !right);
      if(right) ok++;
      fb.textContent = right ? ('✓ ' + (li.dataset.form !== D.words[li.dataset.a-1].word ? '（' + li.dataset.form + '）' : ''))
                             : '✗ 答案：' + li.dataset.form;
    });
    $('score').textContent = reveal ? '' : ok + ' / ' + D.quiz.length;
  }
  $('check').onclick = () => check(false);
  $('reveal').onclick = () => check(true);
})();
