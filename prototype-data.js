/**
 * Nạp rag_data.json và render các màn: lịch, điểm danh, thực đơn, bài tập, nhận xét, gợi ý AI.
 * Cần mở qua HTTP (vd: python -m http.server) để fetch được.
 */
const DATA_PENDING_MSG =
  'Nhà trường chưa cập nhật dữ liệu. Phụ huynh vui lòng thử lại sau.';

function getTodayStr() {
  const p = new URLSearchParams(window.location.search);
  const d = p.get('date');
  if (d && /^\d{2}\/\d{2}\/\d{4}$/.test(d)) return d;
  return '09/04/2026';
}

function parseDateDMY(s) {
  const [dd, mm, yy] = s.split('/').map(Number);
  return new Date(yy, mm - 1, dd);
}

function toDMY(date) {
  const dd = String(date.getDate()).padStart(2, '0');
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const yy = date.getFullYear();
  return dd + '/' + mm + '/' + yy;
}

function addDays(date, n) {
  const d = new Date(date.getTime());
  d.setDate(d.getDate() + n);
  return d;
}

/** Thứ Hai đầu tuần (T2…CN trong strip) */
function mondayOfWeek(date) {
  const d = new Date(date.getTime());
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  d.setHours(12, 0, 0, 0);
  return d;
}

function setAttStats(onTime, late, absOk, absNo) {
  const a = (id, v) => {
    const el = document.getElementById(id);
    if (el) el.textContent = String(v);
  };
  a('att-stat-ontime', onTime);
  a('att-stat-late', late);
  a('att-stat-absok', absOk);
  a('att-stat-absno', absNo);
}

function countAttendanceStats(day) {
  let onTime = 0;
  let late = 0;
  for (const ch of day.chunks) {
    const c = ch.content;
    const st = extractField(c, 'Trạng thái tiết học');
    if (!st) continue;
    if (/Đúng giờ|Tiết kép/i.test(st)) onTime += 1;
    else if (/Đi muộn/i.test(st)) late += 1;
  }
  return { onTime, late };
}

/** Thứ 2 … Thứ 7, Chủ nhật */
function thuLabelFromDate(d) {
  const map = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
  return map[d.getDay()];
}

function filterSheet(data, name) {
  return data.filter((x) => x.metadata && x.metadata.sheet === name);
}

function sortByRow(items) {
  return items.slice().sort((a, b) => (a.metadata.row || 0) - (b.metadata.row || 0));
}

function extractField(block, label) {
  const re = new RegExp('- ' + label + ':\\s*([^\\n]+)');
  const m = block.match(re);
  return m ? m[1].trim() : '';
}

function extractDayColumn(content, dayLabel) {
  const esc = dayLabel.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(
    '- ' + esc + ':\\s*([^\\n]+)(?:\\n\\s*\\n\\s*\\(([^)]+)\\))?',
    'm'
  );
  const m = content.match(re);
  if (!m) return null;
  return { subject: m[1].trim(), teacher: (m[2] || '').trim() };
}

function groupAttendanceByDay(rows) {
  const sorted = sortByRow(rows);
  const days = [];
  let cur = null;
  for (const row of sorted) {
    const c = row.content;
    const dm = c.match(/(\d{2}\/\d{2}\/\d{4})/);
    if (c.includes('Ngày:') && dm) {
      if (cur) days.push(cur);
      cur = { date: dm[1], chunks: [] };
    }
    if (cur) cur.chunks.push(row);
  }
  if (cur) days.push(cur);
  return days;
}

function parseHomework(content) {
  const subj = extractField(content, 'Mã lớp / Môn học') || extractField(content, 'Môn học');
  const name = extractField(content, 'Tên bài tập / Kiểm tra');
  let status = extractField(content, 'Trạng thái');
  const score = extractField(content, 'Điểm số');
  let deadline = '';
  const hm = content.match(/Hạn nộp dự kiến:\s*(\d{4}-\d{2}-\d{2})/);
  if (hm) {
    const [Y, M, D] = hm[1].split('-');
    deadline = `${D}/${M}`;
  }
  return { subj: subj || '—', name: name || '—', status, score: score || '', deadline };
}

function parseComment(content) {
  const dm = content.match(/Ngày:\s*(\d{4}-\d{2}-\d{2})/);
  const gv = extractField(content, 'Giáo viên');
  const mon = extractField(content, 'Bộ môn');
  const txt = extractField(content, 'Nội dung nhận xét');
  let shortDate = '';
  if (dm) {
    const [Y, M, D] = dm[1].split('-');
    shortDate = `${D}/${M}`;
  }
  return { iso: dm ? dm[1] : '', gv, mon, txt, shortDate };
}

function groupMenuByDay(rows) {
  const sorted = sortByRow(rows);
  const days = [];
  let cur = null;
  for (const row of sorted) {
    const c = row.content;
    const dm = c.match(/Ngày:[^\n]*(\d{2}\/\d{2}\/\d{4})/);
    if (dm) {
      if (cur) days.push(cur);
      cur = { date: dm[1], items: [] };
    }
    if (cur && c.includes('Tên món ăn')) {
      const meal = extractField(c, 'Bữa ăn') || '';
      const name = extractField(c, 'Tên món ăn');
      const km = c.match(/Năng lượng[^:]*:\s*([^\n]+)/);
      const kcal = km ? km[1].trim() : '';
      if (name) cur.items.push({ meal, name, kcal });
    }
  }
  if (cur) days.push(cur);
  return days;
}

function renderSchedule(root, tkbRows, todayStr) {
  const d = parseDateDMY(todayStr);
  const dayLabel = thuLabelFromDate(d);
  root.innerHTML = '';
  if (dayLabel === 'Chủ nhật') {
    root.innerHTML =
      '<div style="padding:20px;text-align:center;color:#6b7280;font-size:13px;">' +
      DATA_PENDING_MSG +
      '</div>';
    return;
  }
  const sorted = sortByRow(tkbRows);
  let periodNum = 0;
  for (const row of sorted) {
    const content = row.content;
    const tiet = extractField(content, 'Tiết');
    const time = extractField(content, 'Thời gian');
    const cell = extractDayColumn(content, dayLabel);
    if (!time) continue;

    if (tiet === '-' || /Nghỉ/i.test(content)) {
      const isLunch = /Nghỉ trưa/i.test(content);
      const div = document.createElement('div');
      div.className = 'break-row';
      div.textContent = (isLunch ? '🍱 ' : '☕ ') + 'Nghỉ · ' + time.replace(/\s+/g, ' ');
      root.appendChild(div);
      continue;
    }

    if (!cell || !cell.subject) {
      const div = document.createElement('div');
      div.className = 'period-card';
      div.innerHTML =
        '<div class="top"><span class="per-num">' +
        tiet +
        '</span><span class="per-subj">' +
        DATA_PENDING_MSG +
        '</span></div>';
      root.appendChild(div);
      continue;
    }

    periodNum++;
    const subj = cell.subject.replace(/\s+/g, ' ');
    const teacher = cell.teacher || '—';
    const card = document.createElement('div');
    card.className = 'period-card';
    card.innerHTML =
      '<div class="top"><span class="per-num">' +
      tiet +
      '</span><span class="per-subj">' +
      escapeHtml(subj) +
      '</span><span class="per-time">' +
      escapeHtml(time) +
      '</span></div>' +
      '<div class="per-details"><div class="per-room">Phòng học: Phòng học lớp CN</div><div class="per-teacher">GV: ' +
      escapeHtml(teacher) +
      '</div></div>';
    root.appendChild(card);
  }
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

/**
 * Chỉ hiển thị điểm danh cho đúng một ngày (ngày "hôm nay" / anchor từ ?date=),
 * không liệt kê toàn bộ lịch sử trong JSON.
 */
function renderAttendance(root, attRows, anchorDateStr) {
  const days = groupAttendanceByDay(attRows);
  const bar = document.getElementById('att-date-bar');
  if (bar) bar.textContent = '📅 ' + anchorDateStr;

  const day = days.find((x) => x.date === anchorDateStr);

  if (!day) {
    root.innerHTML =
      '<div style="padding:16px;color:#6b7280;font-size:13px;text-align:center;">' +
      DATA_PENDING_MSG +
      '</div>';
    setAttStats(0, 0, 0, 0);
    return;
  }

  const { onTime, late } = countAttendanceStats(day);
  setAttStats(onTime, late, 0, 0);

  const first = day.chunks[0] && day.chunks[0].content;
  let badge = '';
  if (first && first.includes('Điểm danh đầu giờ')) {
    const bm = first.match(/Điểm danh đầu giờ:\s*([^\n]+)/);
    const isLate = /Đi muộn/i.test(bm ? bm[1] : '');
    if (bm) {
      badge =
        '<span class="att-badge ' +
        (isLate ? 'lt' : 'ok') +
        '">GV chủ nhiệm điểm danh | ' +
        escapeHtml(bm[1].trim()) +
        '</span>';
    }
  }

  let html = '<div class="att-day">';
  html +=
    '<div class="att-day-hdr" style="cursor:default;"><span>' +
    escapeHtml(anchorDateStr) +
    '</span><span style="display:flex;align-items:center;gap:8px;">' +
    badge +
    '</span></div>';
  html += '<div>';
  for (const ch of day.chunks) {
    const c = ch.content;
    const time = extractField(c, 'Thời gian');
    const subj = extractField(c, 'Môn học');
    const st = extractField(c, 'Trạng thái tiết học');
    if (!time && !subj) continue;
    if (!time) continue;
    const ok = /Đúng giờ|Tiết kép/.test(st || '') ? 'att-ok' : 'att-lt';
    html +=
      '<div class="att-row"><span>' +
      escapeHtml(time) +
      ' · ' +
      escapeHtml(subj || '—') +
      '</span><span class="' +
      ok +
      '">' +
      escapeHtml(st || '—') +
      '</span></div>';
  }
  html += '</div></div>';
  root.innerHTML = html;
}

function renderMenu(root, menuDays, todayStr) {
  const day = menuDays.find((x) => x.date === todayStr);
  root.innerHTML = '';
  if (!day || !day.items.length) {
    root.innerHTML =
      '<div style="padding:20px;text-align:center;color:#92400e;font-size:13px;">' +
      DATA_PENDING_MSG +
      '</div>';
    return;
  }
  const lunch = day.items.filter((i) => /trưa|Ăn trưa/i.test(i.meal));
  const snack = day.items.filter((i) => /phụ|Ăn phụ/i.test(i.meal));
  let h = '';
  if (lunch.length) {
    h += '<div class="meal-section"><div class="meal-lbl lunch">🍽 Ăn trưa</div>';
    for (const i of lunch) {
      h +=
        '<div class="meal-item"><span class="meal-name">' +
        escapeHtml(i.name) +
        '</span><span class="meal-cal">' +
        escapeHtml(i.kcal || '') +
        '</span></div>';
    }
    h += '</div>';
  }
  if (snack.length) {
    h +=
      '<div class="meal-section" style="padding-top:12px;padding-bottom:16px;"><div class="meal-lbl snack">🥤 Ăn phụ</div>';
    for (const i of snack) {
      h +=
        '<div class="meal-item"><span class="meal-name">' +
        escapeHtml(i.name) +
        '</span><span class="meal-cal">' +
        escapeHtml(i.kcal || '') +
        '</span></div>';
    }
    h += '</div>';
  }
  root.innerHTML = h || '<div style="padding:16px;">' + DATA_PENDING_MSG + '</div>';
}

function renderHomework(todoEl, allEl, hwRows) {
  const parsed = hwRows.map((r) => ({ raw: r, ...parseHomework(r.content) }));
  const undone = (s) => /Chưa làm|Chưa hoàn thành/i.test(s || '');
  const todo = parsed.filter((p) => undone(p.status));
  const buildItem = (p) => {
    const tagClass = /CIE|5B06-/.test(p.subj) ? 'subj-tag blue' : 'subj-tag';
    const dot = /Chưa làm/.test(p.status || '')
      ? 'undone'
      : /Chưa hoàn thành/.test(p.status || '')
        ? 'pending'
        : 'done';
    return (
      '<div class="hw-item"><div class="' +
      tagClass +
      '">' +
      escapeHtml(p.subj) +
      '</div><div class="hw-name">' +
      escapeHtml(p.name) +
      '</div><div class="hw-meta"><div class="hw-status"><span class="sdot ' +
      dot +
      '"></span>' +
      escapeHtml(p.status || '') +
      (p.deadline ? ' · Hạn ' + escapeHtml(p.deadline) : '') +
      '</div><div class="hw-score">' +
      escapeHtml(p.score || '-') +
      '</div></div></div>'
    );
  };
  if (todoEl) {
    todoEl.innerHTML = todo.length
      ? todo.map(buildItem).join('')
      : '<div style="padding:14px;color:#6b7280;font-size:13px;">' + DATA_PENDING_MSG + '</div>';
  }
  if (allEl) {
    allEl.innerHTML = parsed.length
      ? parsed.map(buildItem).join('')
      : '<div style="padding:14px;color:#6b7280;font-size:13px;">' + DATA_PENDING_MSG + '</div>';
  }
}

function renderComments(root, nxRows, todayStr) {
  const parsed = nxRows
    .map((r) => ({ ...parseComment(r.content), id: r.id }))
    .filter((p) => p.iso);
  parsed.sort((a, b) => b.iso.localeCompare(a.iso));
  const bar = document.getElementById('cmt-date-bar');
  if (bar) bar.textContent = '📅 ' + todayStr;
  if (!parsed.length) {
    root.innerHTML =
      '<div style="padding:16px;color:#6b7280;font-size:13px;">' + DATA_PENDING_MSG + '</div>';
    return;
  }
  let h = '';
  for (const p of parsed.slice(0, 12)) {
    h +=
      '<div class="cmt-card"><div class="cmt-hdr"><div class="cmt-avatar">👨‍🏫</div><div><div class="cmt-tname">' +
      escapeHtml(p.gv) +
      '</div><div class="cmt-sub">' +
      escapeHtml(p.mon) +
      '</div></div><div class="cmt-date">' +
      escapeHtml(p.shortDate) +
      '</div></div>';
    h += '<div class="cmt-text">' + escapeHtml(p.txt) + '</div>';
    h +=
      '<div class="cmt-action"><span>👍 1</span><span>💬 Bình luận</span></div></div>';
  }
  root.innerHTML = h;
}

function renderAiSearch(aiRoot, hwRows, menuDays, todayStr) {
  const todo = hwRows
    .map((r) => parseHomework(r.content))
    .filter((p) => /Chưa làm|Chưa hoàn thành/i.test(p.status || ''));
  const day = menuDays.find((x) => x.date === todayStr);
  let h = '';

  h += '<div style="padding:8px 14px 4px;font-size:11px;font-weight:700;color:#6b7280;letter-spacing:.3px;">KẾT QUẢ GẦN ĐÂY</div>';
  h += '<div class="ai-result-card"><div class="ai-result-header"><span style="font-size:18px;">📋</span>';
  h +=
    '<span class="ai-result-title">Bài tập chưa làm — theo dữ liệu nhà trường</span><span class="ai-badge">AI ✨</span></div><div class="ai-result-body">';
  if (!todo.length) {
    h +=
      '<div style="padding:8px;color:#6b7280;font-size:13px;">' + DATA_PENDING_MSG + '</div>';
  } else {
    for (const p of todo.slice(0, 5)) {
      const urg = p.deadline ? p.deadline : '';
      h +=
        '<div class="ai-result-row"><span class="ri">📝</span><span class="rt">' +
        escapeHtml(p.name) +
        ' · ' +
        escapeHtml(p.subj) +
        '</span><span class="rb" style="color:#ef4444;font-weight:700;">' +
        escapeHtml(urg) +
        '</span></div>';
    }
  }
  h +=
    '<button class="ai-deeplink-btn" onclick="goTo(\'page-homework\')">Mở Bài tập - Kiểm tra →</button><div class="ai-source-badge">📊 Dữ liệu từ Bài tập</div></div></div>';

  h += '<div class="ai-result-card"><div class="ai-result-header"><span style="font-size:18px;">🍱</span>';
  const d = parseDateDMY(todayStr);
  const wd = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'][d.getDay()];
  h +=
    '<span class="ai-result-title">Thực đơn — ' +
    wd +
    ', ' +
    todayStr.slice(0, 5) +
    '</span><span class="ai-badge">AI ✨</span></div><div class="ai-result-body">';
  if (!day || !day.items.length) {
    h +=
      '<div style="padding:8px;color:#6b7280;font-size:13px;">' + DATA_PENDING_MSG + '</div>';
  } else {
    for (const it of day.items.slice(0, 6)) {
      h +=
        '<div class="ai-result-row"><span class="ri">🍽</span><span class="rt">' +
        escapeHtml(it.name) +
        '</span><span class="rb">' +
        escapeHtml((it.kcal || '').replace(/kcal.*/i, '').trim()) +
        '</span></div>';
    }
  }
  h +=
    '<button class="ai-deeplink-btn" onclick="goTo(\'page-menu\')">Xem thực đơn đầy đủ →</button><div class="ai-source-badge">📊 Dữ liệu từ Thực đơn</div></div></div>';

  aiRoot.innerHTML = h;
}

function renderWeekStrips() {
  const viewing = window.__protoViewingDate || getTodayStr();
  const anchor = window.__protoAnchorToday || getTodayStr();
  const mon = mondayOfWeek(parseDateDMY(viewing));
  const end = addDays(mon, 6);
  const rangeLabel = toDMY(mon) + ' – ' + toDMY(end);
  const labels = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];
  let inner = '';
  for (let i = 0; i < 7; i++) {
    const d = addDays(mon, i);
    const dmy = toDMY(d);
    const cls = ['day-cell'];
    if (dmy === anchor) cls.push('today');
    if (dmy === viewing) cls.push('selected');
    inner +=
      '<div class="' +
      cls.join(' ') +
      '" onclick="protoSelectDay(\'' +
      dmy +
      "')\"><div class=\"dn\">" +
      labels[i] +
      '</div><div class="dd">' +
      d.getDate() +
      '</div></div>';
  }
  const schedEl = document.getElementById('schedule-week-days');
  const menuEl = document.getElementById('menu-week-days');
  if (schedEl) schedEl.innerHTML = inner;
  if (menuEl) menuEl.innerHTML = inner;
  const ml = document.getElementById('schedule-month-label');
  const ml2 = document.getElementById('menu-month-label');
  if (ml) ml.textContent = rangeLabel;
  if (ml2) ml2.textContent = rangeLabel;
}

function protoRefreshScheduleMenuOnly() {
  const b = window.__protoRagBundle;
  if (!b) return;
  renderWeekStrips();
  const v = window.__protoViewingDate || getTodayStr();
  const schedRoot = document.getElementById('schedule-periods-root');
  const menuRoot = document.getElementById('menu-root');
  if (schedRoot) renderSchedule(schedRoot, b.tkb, v);
  if (menuRoot) renderMenu(menuRoot, b.menuDays, v);
}

window.protoSelectDay = function (dmy) {
  window.__protoViewingDate = dmy;
  protoRefreshScheduleMenuOnly();
};

window.protoShiftWeek = function (delta) {
  const cur = window.__protoViewingDate || getTodayStr();
  const d = parseDateDMY(cur);
  d.setDate(d.getDate() + 7 * delta);
  window.__protoViewingDate = toDMY(d);
  protoRefreshScheduleMenuOnly();
};

function updateHomeBanner(todayStr, menuDays, hwRows) {
  const lbl = document.querySelector('#page-home .smart-banner .lbl');
  const ttl = document.querySelector('#page-home .smart-banner .ttl');
  const d = parseDateDMY(todayStr);
  const tnames = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
  const thu = tnames[d.getDay()];
  if (lbl) {
    lbl.textContent = '✨ SMART DAILY BRIEF · ' + thu.toUpperCase() + ', ' + todayStr;
  }
  const todoN = hwRows.filter((r) =>
    /Chưa làm|Chưa hoàn thành/i.test(parseHomework(r.content).status || '')
  ).length;
  const lunch = menuDays.find((x) => x.date === todayStr);
  const lunchItem =
    lunch && lunch.items.find((i) => /trưa|Ăn trưa/i.test(i.meal || ''));
  if (ttl) {
    ttl.textContent = lunchItem
      ? 'Hưng có ' +
        todoN +
        ' bài tập chưa làm · Bữa trưa: ' +
        lunchItem.name.split(/[,+]/)[0].trim()
      : 'Hưng có ' + todoN + ' bài tập chưa làm · ' + DATA_PENDING_MSG;
  }
}

window.initPrototypeFromRag = async function initPrototypeFromRag() {
  const anchorToday = getTodayStr();
  window.__protoAnchorToday = anchorToday;
  window.__protoViewingDate = anchorToday;

  let data;
  try {
    const res = await fetch('rag_data.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(String(res.status));
    data = await res.json();
  } catch (e) {
    const msg =
      DATA_PENDING_MSG +
      ' (Không tải được rag_data.json — hãy chạy máy chủ tĩnh trong thư mục này.)';
    ['schedule-periods-root', 'attendance-root', 'menu-root', 'comments-root'].forEach((id) => {
      const el = document.getElementById(id);
      if (el)
        el.innerHTML =
          '<div style="padding:16px;color:#6b7280;font-size:12px;">' + msg + '</div>';
    });
    const ai = document.getElementById('ai-search-results-root');
    if (ai) ai.innerHTML = '<div class="ai-result-card"><div class="ai-result-body">' + msg + '</div></div>';
    return;
  }

  const tkb = filterSheet(data, 'Thời khoá biểu');
  const att = filterSheet(data, 'Điểm danh');
  const menuDays = groupMenuByDay(filterSheet(data, 'Thực đơn'));
  const hw = filterSheet(data, 'Bài tập');
  const nx = filterSheet(data, 'Nhận xét');

  window.__protoRagBundle = { tkb, att, menuDays, hw, nx };

  renderWeekStrips();

  const schedRoot = document.getElementById('schedule-periods-root');
  if (schedRoot) renderSchedule(schedRoot, tkb, window.__protoViewingDate);

  const attRoot = document.getElementById('attendance-root');
  if (attRoot) renderAttendance(attRoot, att, anchorToday);

  const menuRoot = document.getElementById('menu-root');
  if (menuRoot) renderMenu(menuRoot, menuDays, window.__protoViewingDate);

  renderHomework(
    document.getElementById('hw-todo'),
    document.getElementById('hw-all'),
    hw
  );

  const cmtRoot = document.getElementById('comments-root');
  if (cmtRoot) renderComments(cmtRoot, nx, anchorToday);

  const aiRoot = document.getElementById('ai-search-results-root');
  if (aiRoot) renderAiSearch(aiRoot, hw, menuDays, anchorToday);

  updateHomeBanner(anchorToday, menuDays, hw);
};
