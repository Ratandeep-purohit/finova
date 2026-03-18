// ============================================================
//  scenarios.js  –  Shared engine for UPI Safety + Tax pages
// ============================================================
// Element IDs required by host pages:
//   q-counter, q-progress, action-zone, explain-card,
//   explain-verdict, verdict-icon, verdict-change,
//   explain-text, next-btn, score-correct, score-wrong,
//   score-xp, xp-flash
// SCAM pages also need:  phone-content, sc-badge
// TAX  pages also need:  sc-title, sc-desc, cat-icon, cat-label

let _all         = [];   // full shuffled question list
let _idx         = -1;
let _item        = null;
let _type        = 'SCAM';
let _correct     = 0;
let _wrong       = 0;
let _xpEarned    = 0;
let _streak      = 0;

// ── Shuffle ──────────────────────────────────────────────────
function _shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

// ── Boot: fetch all questions once ───────────────────────────
async function initScenarioModule(type) {
    _type = type;
    _all  = [];
    _idx  = -1;
    _setText('q-counter', 'Loading…');

    try {
        const res = await fetch(API_BASE + '/scenarios/all/?type=' + type);
        if (!res.ok) { _showFatal('Could not load questions (HTTP ' + res.status + ').'); return; }
        const data = await res.json();
        if (!Array.isArray(data) || !data.length) {
            _showFatal('No questions in database. Run: python seed_db.py'); return;
        }
        _all = _shuffle(data);
        _advance();
    } catch (e) {
        _showFatal('Connection failed – is Django running?');
        console.error(e);
    }
}
function loadScenario(t) { initScenarioModule(t); }  // alias

// ── Advance to next question ─────────────────────────────────
function _nextQuestion() { _advance(); }

function _advance() {
    _idx++;
    if (_idx >= _all.length) { _all = _shuffle(_all); _idx = 0; }
    _item = _all[_idx];

    // Reset UI
    _hide('explain-card');
    _showEl('action-zone');
    _enableButtons();

    // Progress
    const num = _idx + 1, tot = _all.length;
    _setText('q-counter', 'Question ' + num + ' of ' + tot);
    _setText('q-number',  'Question ' + num);
    _setPct('q-progress', Math.round((num / tot) * 100));

    // Render — allow page-level override for custom designs
    if (_type === 'SCAM') _renderScam(_item);
    else if (typeof window._renderTaxOverride === 'function') window._renderTaxOverride(_item);
    else _renderTax(_item);
}

// ── SCAM renderer ────────────────────────────────────────────
const PHONE_COLORS = { sms:'#16a34a', whatsapp:'#128c7e', call:'#1c1c1e', email:'#0071e3', qr:'#5856d6', portal:'#ea580c' };

function _renderScam(item) {
    const hint  = item.hint_type || 'sms';
    const color = PHONE_COLORS[hint] || '#16a34a';
    const el    = document.getElementById('phone-content');
    if (el) el.innerHTML = _buildPhone(hint, color, item.description);
    _setText('sc-badge', item.correct_action === 'PAY' ? 'Safe Payment?' : 'Scam Alert');
    const badge = document.getElementById('sc-badge');
    if (badge) badge.style.background = item.correct_action === 'PAY' ? '#dcfce7' : '#fee2e2';
    if (badge) badge.style.color      = item.correct_action === 'PAY' ? '#166534' : '#991b1b';

    // Rebuild buttons each time (correct for this item)
    const zone = document.getElementById('action-zone');
    if (zone) zone.innerHTML = `
        <button id="btn-decline" class="choice-btn choice-safe"  onclick="submitAnswer('DECLINE')">Decline &amp; Report</button>
        <button id="btn-pay"     class="choice-btn choice-risky" onclick="submitAnswer('PAY')">Go Ahead &amp; Pay</button>`;
}

function _buildPhone(hint, color, msg) {
    const t = new Date().toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit'});
    const e = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

    if (hint === 'sms') return `
        <div style="background:${color};color:#fff;padding:0.6rem 1rem;display:flex;align-items:center;gap:0.5rem;">
          <div style="width:28px;height:28px;background:rgba(255,255,255,0.25);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;">VM</div>
          <div><div style="font-size:0.82rem;font-weight:700;">VM-ALERTS</div><div style="font-size:0.65rem;opacity:0.8;">Today, ${t}</div></div>
        </div>
        <div style="padding:1rem;background:#f2f2f7;">
          <div style="background:#fff;border-radius:12px 12px 12px 0;padding:0.75rem;font-size:0.8rem;line-height:1.5;box-shadow:0 1px 4px rgba(0,0,0,0.1);">${e(msg)}</div>
          <div style="font-size:0.65rem;color:#8e8e93;margin-top:0.3rem;">${t}</div>
        </div>`;

    if (hint === 'whatsapp') return `
        <div style="background:#128c7e;color:#fff;padding:0.6rem 1rem;display:flex;align-items:center;gap:0.5rem;">
          <div style="width:28px;height:28px;background:rgba(255,255,255,0.25);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;">?</div>
          <div><div style="font-size:0.82rem;font-weight:700;">Unknown Contact</div><div style="font-size:0.65rem;opacity:0.75;">online</div></div>
        </div>
        <div style="background:#ece5dd;padding:1rem;min-height:160px;">
          <div style="background:#fff;border-radius:0 8px 8px 8px;padding:0.5rem 0.75rem;font-size:0.8rem;line-height:1.5;max-width:90%;box-shadow:0 1px 2px rgba(0,0,0,0.12);">${e(msg)}<div style="font-size:0.6rem;color:#8e8e93;text-align:right;margin-top:4px;">${t}</div></div>
        </div>`;

    if (hint === 'call') return `
        <div style="background:#1c1c1e;padding:1.5rem;text-align:center;color:#fff;">
          <div style="font-size:2rem;margin-bottom:0.5rem;">📞</div>
          <div style="font-size:1rem;font-weight:700;">+91-9876XXXXX</div>
          <div style="font-size:0.7rem;color:#aeaeb2;margin-bottom:1rem;">Unknown Number · Incoming Call</div>
          <div style="background:#2c2c2e;border-radius:8px;padding:0.75rem;font-size:0.75rem;line-height:1.5;color:#e5e5ea;text-align:left;">"${e(msg)}"</div>
        </div>`;

    if (hint === 'email') return `
        <div style="background:#fff;padding:0.5rem 0.75rem;border-bottom:1px solid #e5e5ea;">
          <div style="font-size:0.68rem;color:#636366;">From: noreply@govt-portal.in · To: you@email.com</div>
          <div style="font-size:0.8rem;font-weight:700;color:#1c1c1e;">${e(msg).substring(0,50)}...</div>
        </div>
        <div style="padding:0.75rem;font-size:0.78rem;line-height:1.5;background:#fff;">${e(msg)}
          <div style="display:inline-block;margin-top:0.75rem;padding:0.3rem 1rem;background:#0071e3;color:#fff;border-radius:6px;font-size:0.75rem;font-weight:600;cursor:default;">Verify Now</div>
        </div>`;

    if (hint === 'qr') return `
        <div style="padding:1.5rem;text-align:center;background:#fff;">
          <div style="font-size:0.85rem;font-weight:700;margin-bottom:1rem;">UPI Payment Request</div>
          <div style="width:100px;height:100px;margin:0 auto 0.75rem;border:3px solid #000;border-radius:4px;background:repeating-conic-gradient(#000 0% 25%, #fff 0% 50%) 0 0 / 8px 8px;"></div>
          <div style="font-size:0.75rem;color:#636366;">${e(msg).substring(0,70)}...</div>
        </div>`;

    return `<div style="padding:1rem;font-size:0.82rem;line-height:1.6;">${e(msg)}</div>`;
}

// ── TAX renderer ─────────────────────────────────────────────
const TAX_CATS = {
    salary:   { icon:'💼', label:'Salary & TDS' },
    document: { icon:'📑', label:'Capital Gains' },
    form:     { icon:'📋', label:'Deductions' },
    news:     { icon:'📰', label:'Tax Facts' },
};

function _renderTax(item) {
    _setText('sc-title', item.title);
    _setText('sc-desc',  item.description);
    const cat = TAX_CATS[item.hint_type] || { icon:'📄', label:'Income Tax' };
    _setText('cat-icon',  cat.icon);
    _setText('cat-label', cat.label);
    const stamps = { salary:'TDS Rules', document:'Capital Gains', form:'Deductions', news:'Tax Facts' };
    _setText('doc-stamp', stamps[item.hint_type] || 'Income Tax');

    // Rebuild buttons
    const zone = document.getElementById('action-zone');
    if (zone) zone.innerHTML = `
        <button id="btn-yes" class="choice-btn choice-safe"  onclick="submitAnswer('YES')">Yes, this is correct</button>
        <button id="btn-no"  class="choice-btn choice-risky" onclick="submitAnswer('NO')">No, this is wrong</button>`;
}

// ── Submit ────────────────────────────────────────────────────
async function submitAnswer(action) {
    if (!_item) return;

    // Disable all buttons immediately
    _disableButtons();

    const user = localStorage.getItem('finova_user');
    if (!user) {
        _showResult(false, 'Not logged in. Please log in again.', 0, 0, '');
        return;
    }

    try {
        const res = await fetch(API_BASE + '/scenarios/answer/', {
            method : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body   : JSON.stringify({ username: user, scenario_id: _item.id, action })
        });

        let data;
        try { data = await res.json(); }
        catch (_) { _showResult(false, 'Server error – could not parse response.', 0, 0, ''); return; }

        if (!res.ok) {
            _showResult(false, data.error || 'Server error ' + res.status, 0, 0, '');
            return;
        }

        if (data.correct) {
            _correct++;
            _streak++;
            const xp = data.xp_reward || _item.xp_reward || 50;
            _xpEarned += xp;
            _flashXP(true, xp);
            _setStreak(_streak);
            _showResult(true, data.message, 0, xp, _item.explanation || '');

            if (typeof checkAndRewardMission === 'function') {
                if (_type === 'SCAM' && _correct >= 3) checkAndRewardMission('safety', 50);
                if (_type === 'TAX' && _streak >= 2) checkAndRewardMission('tax', 50);
            }
        } else {
            _wrong++;
            _streak = 0;
            _setStreak(0);
            const pen = parseFloat(data.penalty || _item.penalty || 500);
            _flashXP(false, pen);
            _showResult(false, data.message, pen, 0, _item.explanation || '');
        }

        _updateScore();
        fetchProfile();  // refresh balance & XP in topbar

    } catch (err) {
        _showResult(false, 'Network error – check server connection.', 0, 0, '');
        console.error('submitAnswer:', err);
    }

    _hide('action-zone');
}

// ── Show result card ──────────────────────────────────────────
function _showResult(ok, msg, penalty, xpGain, explanation) {
    const card    = document.getElementById('explain-card');
    const verdict = document.getElementById('explain-verdict');
    const icon    = document.getElementById('verdict-icon');
    const change  = document.getElementById('verdict-change');
    const text    = document.getElementById('explain-text');
    const nextBtn = document.getElementById('next-btn');

    if (!card) return;

    if (ok) {
        if (verdict) verdict.className = 'explain-verdict correct result-header correct';
        if (icon)    icon.innerText   = 'Correct Answer!';
        if (change)  change.innerText = xpGain ? '+' + xpGain + ' XP' : '';
        const em = document.getElementById('result-emoji');
        if (em) em.innerText = '✅';
    } else {
        if (verdict) verdict.className = 'explain-verdict wrong result-header wrong';
        if (icon)    icon.innerText   = 'Wrong Answer';
        if (change)  change.innerText = penalty ? 'Rs.' + parseFloat(penalty).toFixed(0) + ' deducted' : '';
        const em = document.getElementById('result-emoji');
        if (em) em.innerText = '❌';
    }

    // Show explanation text
    const displayText = (explanation && explanation.trim()) ? explanation : msg;
    if (text) text.innerText = displayText;

    // Wire up next button onclick EVERY time
    if (nextBtn) {
        nextBtn.style.display = 'block';
        nextBtn.innerText     = _type === 'SCAM' ? 'Next Scenario' : 'Next Question';
        nextBtn.onclick       = _advance;  // <-- critical fix
    }

    card.style.display = 'block';
    // Smooth scroll to result
    setTimeout(() => card.scrollIntoView({ behavior:'smooth', block:'nearest' }), 50);
}

// ── Helpers ───────────────────────────────────────────────────
function _flashXP(gain, amount) {
    const el = document.getElementById('xp-flash');
    if (!el) return;
    el.className = 'xp-flash ' + (gain ? 'gain' : 'loss');
    el.innerText = gain ? '+' + amount + ' XP' : '-Rs.' + Math.round(amount);
    el.style.display = 'inline-block';
    setTimeout(() => { el.style.display = 'none'; }, 2500);
}

function _setStreak(n) {
    const el = document.getElementById('streak-val');
    if (el) el.innerText = n;
    const badge = document.getElementById('streak-badge');
    if (badge) {
        badge.style.display = n >= 3 ? 'inline-block' : 'none';
        badge.innerText = n + ' streak!';
    }
}

function _updateScore() {
    _setText('score-correct', _correct);
    _setText('score-wrong',   _wrong);
    _setText('score-xp',      _xpEarned);
    const total = _correct + _wrong;
    const pct   = total ? Math.round((_correct / total) * 100) : 0;
    _setText('accuracy-val', total ? pct + '%' : '—');
    const bar = document.getElementById('accuracy-bar');
    if (bar) bar.style.width = pct + '%';
}

function _showFatal(msg) {
    const el = document.getElementById('phone-content') || document.getElementById('sc-desc');
    if (el) el.innerText = msg;
    _hide('action-zone');
}

function _disableButtons() {
    document.querySelectorAll('#action-zone button').forEach(b => { b.disabled = true; b.style.opacity = '0.5'; });
}
function _enableButtons() {
    document.querySelectorAll('#action-zone button').forEach(b => { b.disabled = false; b.style.opacity = '1'; });
}

function _setText(id, v) { const el = document.getElementById(id); if (el) el.innerText = v; }
function _setPct(id, p)  { const el = document.getElementById(id); if (el) el.style.width = p + '%'; }
function _hide(id)       { const el = document.getElementById(id); if (el) el.style.display = 'none'; }
function _showEl(id)     { const el = document.getElementById(id); if (el) el.style.display = ''; }
