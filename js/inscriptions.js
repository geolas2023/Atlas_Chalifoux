// Page thématique « Les inscriptions » de l'Atlas Chalifoux.
// Les données viennent de data/lieux.geojson (généré par scripts/donnees.py) : une seule source pour la carte et la page.

const IDS = ['L09', 'L44'];
const PERSONNE = { L09: 'chalifoux', L44: 'leroux' };
const COULEUR = { chalifoux: '#9a3322', leroux: '#2f4d63', julien: '#2f4d63' };
const NOM = { chalifoux: 'Juan Valdez et B. Chalifou', leroux: 'Antoine Leroux', julien: '' };
const CERTITUDE = { certaine: 'position précise', approximative: 'position approximative', hypothetique: 'position hypothétique' };
const MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];

// Photos d'archives et de terrain qu'on ne peut pas reproduire ici (droits réservés) : liens vers leur page.
const UOU = 'Utah State Historical Society / Marriott Library';
const ADVP = { titre: 'Photographies de terrain (adventr.co)', url: 'https://adventr.co/microposts/denis-julien-inscriptions/' };
const PHOTOS = {
  L44: [{ titre: 'Photographie de 1968 des inscriptions de Leroux et de « F. R. B. Chalifou » (Missouri Historical Society, Western Travel Collection, A1734-00001)', url: 'https://mohistory.org/collections' }]
};

const echapper =s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const personne = id => PERSONNE[id] || 'leroux';

function dateLisible(edtf) {
  const [a, b] = edtf.split('/');
  const un = d => {
    const p = d.replace(/[~?]/g, '').split('-').map(Number);
    if (p.length === 3) return `${p[2] === 1 ? '1er' : p[2]} ${MOIS[p[1] - 1]} ${p[0]}`;
    if (p.length === 2) return `${MOIS[p[1] - 1]} ${p[0]}`;
    return String(p[0]);
  };
  return b ? `entre ${un(a)} et ${un(b)}` : un(a);
}

function ouvrirImage(src, legende) {
  const lb = document.getElementById('lightbox');
  document.getElementById('lb-image').src = src;
  document.getElementById('lb-image').alt = legende;
  document.getElementById('lb-legende').textContent = legende;
  lb.hidden = false;
}
document.getElementById('lb-fermer').onclick = () => { document.getElementById('lightbox').hidden = true; };
document.getElementById('lightbox').onclick = e => { if (e.target.id === 'lightbox') e.currentTarget.hidden = true; };
document.addEventListener('keydown', e => { if (e.key === 'Escape') document.getElementById('lightbox').hidden = true; });

function fiche(f) {
  const p = f.properties, qui = personne(p.id);
  const imgs = p.images || [];
  const el = document.createElement('article');
  el.className = 'fiche' + (imgs.length ? '' : ' sans-image');
  el.id = 'fiche-' + p.id;
  el.innerHTML = `
    ${imgs.length ? `<div>${imgs.map((im, i) => `<img src="${echapper(im.src)}" alt="${echapper(im.legende)}" data-i="${i}" loading="lazy">`).join('')}</div>` : ''}
    <div>
      <h3>${echapper(p.nom)}</h3>
      <div class="date"><span>${echapper(dateLisible(p.date_edtf))}</span>
        <span class="badge" style="background:${COULEUR[qui]};color:#fff">${NOM[qui]}</span>
        <span class="badge b-${echapper(p.certitude)}">${CERTITUDE[p.certitude] || ''}</span></div>
      <p class="texte">${echapper(p.description.replace(/^Denis Julien, traiteur[^.]*\.\s*/, ''))}</p>
      ${p.note ? `<p class="note">${echapper(p.note)}</p>` : ''}
      ${(PHOTOS[p.id] || []).length ? `<p class="photos">📷 Photos d'archives et de terrain (droits réservés, à consulter sur place) :</p><ul class="photos">${PHOTOS[p.id].map(x => `<li><a href="${echapper(x.url)}" target="_blank" rel="noopener">${echapper(x.titre)} ↗</a></li>`).join('')}</ul>` : ''}
      <p class="src">Sources : ${echapper(p.sources)}</p>
      <p class="actions"><a href="index.html#lieu=${p.id}">Voir dans l'atlas →</a>
        <a href="#" data-zoom="${p.id}">Centrer la carte</a>
        <span>${f.geometry.coordinates[1].toFixed(4)}, ${f.geometry.coordinates[0].toFixed(4)}</span></p>
    </div>`;
  el.querySelectorAll('img').forEach(img => {
    img.onclick = () => { const im = imgs[+img.dataset.i]; ouvrirImage(im.lien || im.src, im.legende); };
  });
  return el;
}

Promise.all([fetch('data/lieux.geojson').then(r => r.json()), fetch('data/trajets.geojson').then(r => r.json())])
  .then(([lieux, trajets]) => {
    const feats = lieux.features.filter(f => IDS.includes(f.properties.id))
      .sort((a, b) => (a.properties.date_edtf.includes('/') - b.properties.date_edtf.includes('/')) || a.properties.debut - b.properties.debut);
    feats.forEach(f => { f.properties.qui = personne(f.properties.id); f.properties.precis = f.properties.certitude === 'certaine' ? 1 : 0; });

    const nb = q => feats.filter(f => f.properties.qui === q).length;
    document.getElementById('chiffres').innerHTML =
      `<div><b>${feats.length}</b>inscriptions placées</div><div><b>1835</b>l'année de « B. Chalifou »</div><div><b>Willow Creek</b>branche nord de la Vieille piste espagnole</div>`;

    const liste = document.getElementById('fiches');
    feats.forEach(f => liste.appendChild(fiche(f)));
    if (typeof maplibregl === 'undefined') {
      document.getElementById('carte').innerHTML = '<p class="encart">La carte n\'a pas pu être chargée.</p>';
      return;
    }

    const carte = new maplibregl.Map({
      container: 'carte', style: 'https://tiles.openfreemap.org/styles/positron',
      bounds: [[-110.4, 38.9], [-108.8, 40.6]], fitBoundsOptions: { padding: 40 }, cooperativeGestures: true
    });
    carte.addControl(new maplibregl.NavigationControl({ showCompass: false }));
    carte.addControl(new maplibregl.ScaleControl({ unit: 'metric' }));

    const allerA = id => {
      const f = feats.find(x => x.properties.id === id); if (!f) return;
      carte.flyTo({ center: f.geometry.coordinates, zoom: 10 });
      document.getElementById('carte').scrollIntoView({ behavior: 'smooth', block: 'center' });
    };
    liste.addEventListener('click', e => { const a = e.target.closest('[data-zoom]'); if (a) { e.preventDefault(); allerA(a.dataset.zoom); } });

    carte.on('load', () => {
      const route = trajets.features.filter(t => t.properties.id === 'T02');
      carte.addSource('route', { type: 'geojson', data: { type: 'FeatureCollection', features: route } });
      carte.addLayer({ id: 'route', type: 'line', source: 'route', paint: { 'line-color': '#9a3322', 'line-width': 2, 'line-dasharray': [2, 2], 'line-opacity': .7 } });
      carte.addSource('insc', { type: 'geojson', data: { type: 'FeatureCollection', features: feats } });
      const couleur = ['match', ['get', 'qui'], 'chalifoux', COULEUR.chalifoux, COULEUR.leroux];
      carte.addLayer({ id: 'insc', type: 'circle', source: 'insc', paint: {
        'circle-radius': 7, 'circle-stroke-width': 2.5, 'circle-stroke-color': couleur,
        'circle-color': ['case', ['==', ['get', 'precis'], 1], couleur, '#f4efe6'] } });
      carte.addLayer({ id: 'insc-noms', type: 'symbol', source: 'insc', layout: {
        'text-field': ['get', 'nom'], 'text-size': 11, 'text-offset': [0, 1.2], 'text-anchor': 'top', 'text-max-width': 12 },
        paint: { 'text-color': '#2b2620', 'text-halo-color': '#fffdf8', 'text-halo-width': 1.5 } });
      carte.on('mouseenter', 'insc', () => { carte.getCanvas().style.cursor = 'pointer'; });
      carte.on('mouseleave', 'insc', () => { carte.getCanvas().style.cursor = ''; });
      carte.on('click', 'insc', e => {
        const p = e.features[0].properties;
        new maplibregl.Popup({ offset: 10 }).setLngLat(e.features[0].geometry.coordinates)
          .setHTML(`<b>${echapper(p.nom)}</b><br>${echapper(dateLisible(p.date_edtf))} · ${CERTITUDE[p.certitude] || ''}<br><a href="#fiche-${p.id}">Lire la fiche ↓</a>`)
          .addTo(carte);
        document.querySelectorAll('.fiche.active').forEach(x => x.classList.remove('active'));
        document.getElementById('fiche-' + p.id)?.classList.add('active');
      });
    });
  })
  .catch(err => {
    document.getElementById('fiches').innerHTML = `<p class="encart">Impossible de charger les données (${echapper(err.message)}). Ouvrez la page depuis le site ou un serveur local.</p>`;
  });
