/* global React, ReactDOM */
const { useEffect, useState } = React;
const h = React.createElement;

function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetch(url, { credentials: 'same-origin' })
      .then(r => r.json())
      .then(j => { if (mounted) { setData(j); setLoading(false); } })
      .catch(() => mounted && setLoading(false));
    return () => { mounted = false; };
  }, [url]);
  return { data, loading };
}

function Landing() {
  const { data } = useFetch('/api/stats/');
  return h('div', { className: 'd-grid gap-3' },
    h('div', { className: 'd-flex gap-2 align-items-center' },
      h('span', { className: 'badge bg-primary' }, 'Global'),
      h('span', { className: 'text-muted' }, 'Listings worldwide')
    ),
    h('div', { className: 'row g-3' },
      h('div', { className: 'col-4' }, h('div', { className: 'p-3 bg-light rounded-3' },
        h('div', { className: 'text-muted' }, 'Total'),
        h('div', { className: 'h4 mb-0' }, (data && data.total) || '—')
      )),
      h('div', { className: 'col-4' }, h('div', { className: 'p-3 bg-light rounded-3' },
        h('div', { className: 'text-muted' }, 'Approved'),
        h('div', { className: 'h4 mb-0 text-success' }, (data && data.approved) || '—')
      )),
      h('div', { className: 'col-4' }, h('div', { className: 'p-3 bg-light rounded-3' },
        h('div', { className: 'text-muted' }, 'Pending'),
        h('div', { className: 'h4 mb-0 text-warning' }, (data && data.pending) || '—')
      ))
    )
  );
}

function Inventory() {
  const { data, loading } = useFetch('/api/cars/');
  if (loading) return h('div', null, 'Loading…');
  const items = (data && data.results) || [];
  return h('div', { className: 'row g-4' }, items.map(car => (
    h('div', { className: 'col-12 col-sm-6 col-lg-4', key: car.id },
      h('div', { className: 'card shadow-sm h-100' },
        car.image ? h('img', { src: car.image, className: 'card-img-top', style: { height: 200, objectFit: 'cover' }, alt: car.name }) : null,
        h('div', { className: 'card-body' },
          h('div', { className: 'd-flex justify-content-between align-items-start' },
            h('h3', { className: 'h5 card-title mb-1' }, car.name),
            h('span', { className: 'badge bg-success' }, `₹${car.expected_price}`)
          ),
          h('p', { className: 'card-text text-muted mb-2' }, `${car.year} • ${car.fuel} • ${car.transmission}`),
          h('div', { className: 'd-flex gap-2' },
            h('a', { className: 'btn btn-outline-primary btn-sm', href: `/cars/${car.id}/` }, 'View'),
            h('a', { className: 'btn btn-primary btn-sm', href: `/cars/${car.id}/buy/` }, 'Buy')
          )
        )
      )
    )
  )));
}

function AdminDashboard() {
  const { data, loading } = useFetch('/api/cars/pending/');
  const approve = (id) => fetch(`/api/cars/${id}/approve/`, { method:'POST', credentials:'same-origin', headers: {'X-Requested-With':'XMLHttpRequest'} }).then(() => location.reload());
  const reject = (id) => fetch(`/api/cars/${id}/reject/`, { method:'POST', credentials:'same-origin', headers: {'X-Requested-With':'XMLHttpRequest'} }).then(() => location.reload());
  if (loading) return h('div', null, 'Loading…');
  const items = (data && data.results) || [];
  return h('div', { className: 'd-grid gap-3' },
    h('h2', { className: 'h5' }, 'Pending approvals'),
    h('ul', { className: 'list-group' }, items.map(c => (
      h('li', { className: 'list-group-item d-flex justify-content-between align-items-center', key: c.id },
        h('span', null, `${c.name} by ${c.seller}`),
        h('span', null,
          h('button', { className: 'btn btn-sm btn-success me-2', onClick: () => approve(c.id) }, 'Approve'),
          h('button', { className: 'btn btn-sm btn-warning', onClick: () => reject(c.id) }, 'Reject')
        )
      )
    )))
  );
}

function CustomerDashboard() {
  const { data, loading } = useFetch('/api/my-cars/');
  if (loading) return h('div', null, 'Loading…');
  const items = (data && data.results) || [];
  return h('div', { className: 'table-responsive' },
    h('table', { className: 'table align-middle' },
      h('thead', null, h('tr', null, h('th', null, 'Car'), h('th', null, 'Status'), h('th', null, 'Price'))),
      h('tbody', null, items.map(c => (
        h('tr', { key: c.id },
          h('td', null, h('a', { href: `/cars/${c.id}/` }, c.name)),
          h('td', null, c.status),
          h('td', null, `₹${c.expected_price}`)
        )
      )))
    )
  );
}

function App() {
  const hash = typeof window !== 'undefined' ? window.location.hash : '';
  const route = (hash || '').replace(/^#/, '');
  if (route.startsWith('/inventory')) return h(Inventory);
  if (route.startsWith('/admin')) return h(AdminDashboard);
  if (route.startsWith('/dashboard')) return h(CustomerDashboard);
  return h(Landing);
}

function mountApp() {
  const root = document.getElementById('spa-root');
  if (!root) return;
  const render = () => ReactDOM.createRoot(root).render(h(App));
  window.addEventListener('hashchange', render);
  render();
}

document.addEventListener('DOMContentLoaded', mountApp);


