/* Petit moteur autonome : charge les CSV déclarés dans window.DASH_SOURCES
   et expose l'API `dash` utilisée par les pages (data, calc, onData, setLink). */
(function () {
  const sources = window.DASH_SOURCES || {};
  const store = {}, calcs = {}, cache = {}, listeners = [];
  for (const id of Object.keys(sources)) store[id] = { status: 'loading', data: [], columns: [] };
  const notify = () => { for (const k in cache) delete cache[k]; listeners.forEach(fn => { try { fn(); } catch (e) { console.error(e); } }); };
  function data(id) {
    if (store[id]) return { ...store[id], refreshing: false, meta: [] };
    const c = calcs[id];
    if (!c) return { status: 'missing', data: [], columns: [] };
    if (cache[id]) return cache[id];
    const ins = c.inputs.map(data);
    const bad = ins.find(i => i.status !== 'ok');
    if (bad) return { status: bad.status, data: [], columns: [] };
    let out;
    try { const d = c.fn(...ins.map(i => i.data)); out = { status: 'ok', data: d, columns: Array.isArray(d) && d[0] ? Object.keys(d[0]) : [] }; }
    catch (e) { console.error(e); out = { status: 'error', data: [], columns: [], message: String(e) }; }
    return (cache[id] = out);
  }
  window.dash = {
    data,
    calc(id, def) { calcs[id] = def; },
    loader() {},
    onData(fn) { listeners.push(fn); fn(); },
    colors: ['var(--f-c0)', 'var(--f-c1)', 'var(--f-c2)', 'var(--f-c3)', 'var(--f-c4)', 'var(--f-c5)', 'var(--f-c6)', 'var(--f-c7)'],
    setLink(name) { try { history.replaceState(null, '', '#' + name); } catch (e) {} },
    params() { return {}; }, setParams() {}, resetParams() {}, refresh() {}
  };
  Promise.all(Object.entries(sources).map(([id, url]) => d3.csv(url).then(
    rows => { store[id] = { status: 'ok', data: rows, columns: rows.columns }; },
    err => { store[id] = { status: 'error', data: [], columns: [], message: String(err) }; }
  ))).then(() => {
    notify();
    document.querySelectorAll('.dash-skeleton').forEach(e => e.classList.remove('dash-skeleton'));
  });
  let t; addEventListener('resize', () => { clearTimeout(t); t = setTimeout(notify, 120); });
})();
