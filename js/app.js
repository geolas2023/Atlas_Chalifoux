// Atlas Chalifoux — carte MapLibre + timeline + journal de bord
// Les entités ont des attributs numériques « debut » et « fin » (années décimales : 1697.68 = début septembre 1697).
// La timeline affiche toutes les entités commencées avant la date choisie (affichage cumulatif).
//
// Échelle de la timeline en deux segments :
//   - 1780 à 1825, par année (origines, frères, Nord-Ouest), en segment compressé ;
//   - 1826 à 1889, par mois (Taos, Californie, Huerfano, Culebra).
// La dernière position (max) = « toutes les dates ».
// Langue de la page : <html lang="en"> (index-en.html) affiche l'interface et les données en anglais.
const EN = document.documentElement.lang === 'en';
const L = (fr, en) => EN ? en : fr;
const AN_DEBUT = 1780, AN_DETAIL = 1826, AN_FIN = 1890;
const NB_ANNEES = AN_DETAIL - AN_DEBUT;                       // 46 positions annuelles
const POS_MAX = NB_ANNEES + (AN_FIN - AN_DETAIL) * 12;        // 46 + 768 = 814
const MOIS = EN ? ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
             : ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
function lirePosition(v) {
  v = Number(v);
  if (v >= POS_MAX) return { libelle: L('Toutes les dates', 'All dates'), borne: null };
  if (v < NB_ANNEES) return { libelle: `${AN_DEBUT + v}`, borne: AN_DEBUT + v + 1 };
  const m = v - NB_ANNEES;
  return { libelle: `${MOIS[m % 12]} ${AN_DETAIL + Math.floor(m / 12)}`, borne: AN_DETAIL + (m + 1) / 12 };
}

// Les époques de la vie de Chalifoux, pour situer chaque entrée du journal
const CHAPITRES = EN ? [
  [1826, 'I · Charlesbourg, St. Louis and the North'],
  [1836.9, 'II · Taos, the Gila and the Ute country'],
  [1841, 'III · The Chaguanosos in California'],
  [1853, 'IV · Embudo, Taos and the war of 1847'],
  [9999, 'V · The Huerfano, Trinidad and the Culebra']
]
  : [
  [1826, 'I · Charlesbourg, Saint-Louis et le Nord'],
  [1836.9, 'II · Taos, la Gila et le pays ute'],
  [1841, 'III · Les Chaguanosos en Californie'],
  [1853, 'IV · Embudo, Taos et la guerre de 1847'],
  [9999, 'V · La Huerfano, Trinidad et la Culebra']
];
const chapitre = t => CHAPITRES.find(([fin]) => t < fin)[1];

const VERSION = new URL(document.currentScript.src).searchParams.get('v') || '';

const carte = new maplibregl.Map({
  container: 'carte',
  style: 'https://tiles.openfreemap.org/styles/positron',
  center: [-100, 38],
  zoom: 3.6,
  attributionControl: { compact: true }
});
carte.addControl(new maplibregl.NavigationControl(), 'top-left');
if (typeof installerStreetView === 'function') installerStreetView(carte, EN);
carte.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');
// Légende en cartouche dans le coin supérieur droit (contenu défini dans index.html)
carte.addControl({
  onAdd() { const el = document.getElementById('legende-carte'); el.classList.add('maplibregl-ctrl'); return el; },
  onRemove() {}
}, 'top-right');
new ResizeObserver(() => carte.resize()).observe(document.getElementById('carte'));

// Couleurs d'encre par membre de la famille
const COULEURS = { baptiste: '#9a3322', chaguanosos: '#5b3f6b', famille: '#3f5a2a', compagnons: '#2f4d63', homonymes: '#8a6a12' };
const couleurCategorie = ['match', ['get', 'categorie'], ...Object.entries(COULEURS).flat(), '#1f2f3a'];
const NOMS_CATEGORIE = EN ? { baptiste: 'Jean-Baptiste Chalifoux', chaguanosos: 'the Chaguanosos', famille: 'the family', compagnons: 'companions and partners', homonymes: 'other Chalifouxes' }
  : { baptiste: 'Jean-Baptiste Chalifoux', chaguanosos: 'les Chaguanosos', famille: 'la famille', compagnons: 'compagnons et associés', homonymes: 'autres Chalifoux' };
const NOMS_MODE = EN ? { mer: 'sea route', cote: 'coastal voyage', terre: 'on horseback, by caravan', fleuve: 'by boat' }
  : { mer: 'route maritime', cote: 'cabotage', terre: 'à cheval, en caravane', fleuve: 'en bateau' };
const ENCRE_MER = '#9a3322', ENCRE_TERRE = '#1f2f3a';
const estMer = ['in', ['get', 'mode'], ['literal', ['mer', 'cote']]];

carte.on('load', async () => {
  const [lieux, trajets, parcours] = await Promise.all([
    fetch(`data/lieux${L('', '-en')}.geojson?v=${VERSION}`).then(r => r.json()),
    fetch(`data/trajets${L('', '-en')}.geojson?v=${VERSION}`).then(r => r.json()),
    fetch(`data/parcours.geojson?v=${VERSION}`).then(r => r.json())
  ]);
  window.DONNEES = { lieux, trajets }; // utilisé par la visite animée (visite.js)
  const couchesDeBase = carte.getStyle().layers.map(l => l.id);
  carte.addSource('lieux', { type: 'geojson', data: lieux });
  carte.addSource('trajets', { type: 'geojson', data: trajets });
  carte.addSource('parcours', { type: 'geojson', data: parcours });

  // Fond satellite (Esri World Imagery), masqué par défaut
  carte.addSource('satellite', {
    type: 'raster', tileSize: 256, maxzoom: 19,
    tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
    attribution: L('Imagerie © Esri, Maxar, Earthstar Geographics et contributeurs', 'Imagery © Esri, Maxar, Earthstar Geographics and contributors')
  });
  carte.addLayer({ id: 'satellite', type: 'raster', source: 'satellite', layout: { visibility: 'none' } });

  // Routes : encre rouge et tirets pour la mer, encre brune et points pour les terres et les rivières.
  // Une ligne claire dessous détache le tracé du fond.
  carte.addLayer({
    id: 'trajets-halo', type: 'line', source: 'trajets',
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': '#eff0e4', 'line-width': 5, 'line-opacity': ['case', ['==', ['get', 'certitude'], 'hypothetique'], 0.35, 0.6] }
  });
  carte.addLayer({
    id: 'trajets-mer', type: 'line', source: 'trajets', filter: estMer,
    layout: { 'line-join': 'round' },
    paint: { 'line-color': ENCRE_MER, 'line-width': ['case', ['==', ['get', 'certitude'], 'hypothetique'], 1.6, 2.4],
             'line-dasharray': [3, 2], 'line-opacity': ['case', ['==', ['get', 'certitude'], 'hypothetique'], 0.6, 0.95] }
  });
  carte.addLayer({
    id: 'trajets-terre', type: 'line', source: 'trajets', filter: ['!', estMer],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': ENCRE_TERRE, 'line-width': ['case', ['==', ['get', 'certitude'], 'hypothetique'], 2, 2.8],
             'line-dasharray': [0.1, 2], 'line-opacity': ['case', ['==', ['get', 'certitude'], 'hypothetique'], 0.6, 0.95] }
  });
  // Trajet sélectionné
  carte.addLayer({
    id: 'trajet-actif', type: 'line', source: 'trajets', filter: ['==', ['get', 'id'], ''],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': '#c8903e', 'line-width': 6, 'line-opacity': 0.55 }
  }, 'trajets-halo');

  // Lieux : pastille d'encre pleine si localisation certaine, cerclée sur vélin sinon
  carte.addLayer({
    id: 'lieux', type: 'circle', source: 'lieux',
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 4.5, 8, 7.5],
      'circle-color': ['case', ['==', ['get', 'certitude'], 'certaine'], couleurCategorie, '#eff0e4'],
      'circle-stroke-color': couleurCategorie,
      'circle-stroke-width': ['case', ['==', ['get', 'certitude'], 'certaine'], 1.5, 2.5]
    }
  });
  // Les combats sont marqués d'un anneau supplémentaire
  carte.addLayer({
    id: 'lieux-anneau', type: 'circle', source: 'lieux', filter: ['==', ['get', 'categorie'], 'combat'],
    paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 7.5, 8, 11.5], 'circle-color': 'rgba(0,0,0,0)',
             'circle-stroke-color': '#9a3322', 'circle-stroke-width': 1, 'circle-stroke-opacity': 0.8 }
  }, 'lieux');
  carte.addLayer({
    id: 'lieux-noms', type: 'symbol', source: 'lieux',
    layout: { 'text-field': ['get', 'nom'], 'text-size': ['interpolate', ['linear'], ['zoom'], 2, 10.5, 8, 13],
              'text-offset': [0, 1.1], 'text-anchor': 'top', 'text-font': ['Noto Sans Italic'], 'text-max-width': 9,
              'text-optional': true, 'symbol-sort-key': ['get', 'debut'] },
    paint: { 'text-color': '#1f2f3a', 'text-halo-color': '#eff0e4', 'text-halo-width': 1.6 }
  });

  // Parcours de Jean-Baptiste : les 23 étapes de la notice de Lecompte, reliées et numérotées dans l'ordre du récit
  carte.addLayer({
    id: 'parcours-ligne', type: 'line', source: 'parcours', filter: ['==', ['geometry-type'], 'LineString'],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': COULEURS.baptiste, 'line-width': 1.6, 'line-opacity': 0.55 }
  }, 'lieux');
  carte.addLayer({
    id: 'parcours-num', type: 'symbol', source: 'parcours', filter: ['==', ['geometry-type'], 'Point'],
    layout: { 'text-field': ['to-string', ['get', 'ordre']], 'text-size': 11, 'text-font': ['Noto Sans Italic'],
              'text-offset': [-0.95, -0.95], 'text-allow-overlap': true, 'text-ignore-placement': true },
    paint: { 'text-color': '#fff', 'text-halo-color': COULEURS.baptiste, 'text-halo-width': 2.2 }
  });
  carte.on('click', 'parcours-num', e => {
    const id = e.features[0].properties.lieu;
    const f = lieux.features.find(x => x.properties.id === id);
    if (f) { afficherFiche(f.properties, f.geometry.type); zoomerSur(f); }
  });
  carte.on('mouseenter', 'parcours-num', () => { carte.getCanvas().style.cursor = 'pointer'; });
  carte.on('mouseleave', 'parcours-num', () => { carte.getCanvas().style.cursor = ''; });

  ['lieux', 'trajets-mer', 'trajets-terre'].forEach(id => {
    carte.on('click', id, e => {
      const f = e.features[0];
      afficherFiche(f.properties, f.geometry.type);
      zoomerSur(f);
    });
    carte.on('mouseenter', id, () => { carte.getCanvas().style.cursor = 'pointer'; });
    carte.on('mouseleave', id, () => { carte.getCanvas().style.cursor = ''; });
  });

  // clic ailleurs que sur un lieu ou une route : le journal se referme
  carte.on('click', e => {
    if (!carte.queryRenderedFeatures(e.point, { layers: ['lieux', 'trajets-mer', 'trajets-terre', 'parcours-num'] }).length) fermerFiche();
  });

  appliquerFond = installerFonds(carte, couchesDeBase, 'satellite');
  await appliquerFond('plan');
  appliquerDate(curseur.value);

  // Cadrer la carte sur l'ensemble des données
  const b = new maplibregl.LngLatBounds();
  [...lieux.features, ...trajets.features].forEach(f => {
    (f.geometry.type === 'Point' ? [f.geometry.coordinates] : f.geometry.coordinates).forEach(xy => b.extend(xy));
  });
  window.LIMITES_DONNEES = b;
  carte.fitBounds(b, { padding: { top: 50, bottom: 50, left: 170, right: 270 }, duration: 0 });
  lireAncre();
  window.addEventListener('hashchange', lireAncre);
});

function lireAncre() {
  const m = decodeURIComponent(location.hash || '').match(/(?:lieu|trajet)=([LT]\d+)/);
  if (!m || !window.DONNEES) return;
  const f = [...window.DONNEES.lieux.features, ...window.DONNEES.trajets.features].find(x => x.properties.id === m[1]);
  if (f) { afficherFiche(f.properties, f.geometry.type); zoomerSur(f); }
}

// ---------- Timeline ----------
const curseur = document.getElementById('curseur');
const sortie = document.getElementById('date-affichee');
const btnLecture = document.getElementById('lecture');
function appliquerDate(v) {
  const { libelle, borne } = lirePosition(v);
  sortie.textContent = libelle;
  const f = borne === null ? null : ['<', ['get', 'debut'], borne];
  const et = base => f ? ['all', base, f] : base;
  ['lieux', 'lieux-noms'].forEach(id => carte.setFilter(id, f));
  carte.setFilter('lieux-anneau', et(['==', ['get', 'categorie'], 'combat']));
  carte.setFilter('trajets-halo', f);
  carte.setFilter('trajets-mer', et(estMer));
  carte.setFilter('trajets-terre', et(['!', estMer]));
}
curseur.max = POS_MAX;
curseur.value = POS_MAX;
curseur.addEventListener('input', () => appliquerDate(curseur.value));

// Graduation : segment 1780-1825 compressé (par année), puis une année tous les 12 mois
(function graduer() {
  const g = document.getElementById('graduation');
  const POUCE = 18; // largeur du bouton du curseur (voir style.css)
  const position = v => `calc(${v / POS_MAX} * (100% - ${POUCE}px) + ${POUCE / 2}px)`;
  const trait = (v, cls) => { const t = document.createElement('span'); t.className = cls; t.style.left = position(v); g.appendChild(t); };
  const annee = (v, texte) => {
    const a = document.createElement('span');
    a.className = 'annee'; a.textContent = texte; a.style.left = position(v);
    a.title = L(`Aller à ${texte}`, `Go to ${texte}`);
    a.addEventListener('click', () => { curseur.value = v; appliquerDate(v); });
    g.appendChild(a);
  };
  const bande = document.createElement('span');
  bande.className = 'segment-compresse'; bande.style.left = position(0);
  bande.style.width = `calc(${(NB_ANNEES - 0.5) / POS_MAX} * (100% - ${POUCE}px))`;
  bande.title = L('1780-1825 : échelle compressée (une position par année)', '1780-1825: compressed scale (one step per year)');
  g.appendChild(bande);
  for (let v = 0; v < NB_ANNEES; v++) if ((AN_DEBUT + v) % 5 === 0) trait(v, (AN_DEBUT + v) % 10 === 0 ? 'trait' : 'trait mineur');
  annee(0, '1780'); annee(20, '1800');
  trait(NB_ANNEES - 0.5, 'trait coupure');
  for (let v = NB_ANNEES; v < POS_MAX; v += 6) {
    const m = v - NB_ANNEES, a = AN_DETAIL + m / 12;
    trait(v, m % 12 === 0 ? 'trait' : 'trait mineur');
    if (m % 12 === 0 && a % 8 === 0) annee(v, `${a}`);
  }
})();

let minuterie = null;
btnLecture.addEventListener('click', () => {
  // « Suivre Chalifoux » coché : visite animée (visite.js) ; sinon, simple défilement de la timeline
  if (document.getElementById('suivi').checked && typeof Visite !== 'undefined') { Visite.basculer(); return; }
  if (minuterie) { clearInterval(minuterie); minuterie = null; btnLecture.textContent = '▶'; return; }
  if (Number(curseur.value) >= Number(curseur.max)) curseur.value = curseur.min;
  btnLecture.textContent = '❚❚';
  minuterie = setInterval(() => {
    const v = Number(curseur.value) + 1;
    curseur.value = v; appliquerDate(v);
    if (v >= Number(curseur.max)) btnLecture.click();
  }, 250);
});

// ---------- Couches ----------
let appliquerFond = null;
document.querySelectorAll('input[name=fond]').forEach(r => r.addEventListener('change', e => { if (appliquerFond) appliquerFond(e.target.value); }));
document.getElementById('c-lieux').addEventListener('change', e => {
  ['lieux', 'lieux-anneau', 'lieux-noms'].forEach(id => carte.setLayoutProperty(id, 'visibility', e.target.checked ? 'visible' : 'none'));
});
document.getElementById('c-parcours').addEventListener('change', e => {
  ['parcours-ligne', 'parcours-num'].forEach(id => carte.setLayoutProperty(id, 'visibility', e.target.checked ? 'visible' : 'none'));
});
document.getElementById('c-trajets').addEventListener('change', e => {
  ['trajets-halo', 'trajets-mer', 'trajets-terre', 'trajet-actif'].forEach(id => carte.setLayoutProperty(id, 'visibility', e.target.checked ? 'visible' : 'none'));
});

// ---------- Journal de bord (panneau documentaire) ----------
const echapper = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const NOMS_CERTITUDE = EN ? { certaine: 'location certain', approximative: 'approximate', hypothetique: 'hypothetical' }
                         : { certaine: 'localisation certaine', approximative: 'approximative', hypothetique: 'hypothétique' };
// Date EDTF -> date lisible (« 1697-09-05 » -> « 5 septembre 1697 » ; « ~ » = vers)
function dateLisible(edtf) {
  if (!edtf) return '';
  return String(edtf).split('/').map(d => {
    const approx = /[~?]/.test(d), [a, m, j] = d.replace(/[~?]/g, '').split('-').map(Number);
    const txt = j ? (EN ? `${MOIS[m - 1]} ${j}, ${a}` : `${j === 1 ? '1er' : j} ${MOIS[m - 1]} ${a}`) : m ? `${MOIS[m - 1]} ${a}` : `${a}`;
    return approx ? `${L('vers', 'c.')} ${txt}` : txt;
  }).join(' – ');
}

const ZOOM_POINT = 7;
function zoomerSur(f) {
  if (f.geometry.type === 'Point') {
    carte.flyTo({ center: f.geometry.coordinates, zoom: Math.max(carte.getZoom(), ZOOM_POINT), speed: 1.4, essential: true });
    return;
  }
  const b = new maplibregl.LngLatBounds();
  f.geometry.coordinates.forEach(xy => b.extend(xy));
  carte.fitBounds(b, { padding: { top: 60, bottom: 60, left: 60, right: 260 }, maxZoom: 7, essential: true });
}

function afficherFiche(p, geom) {
  const estTrajet = geom === 'LineString' || p.type === 'trajet';
  if (carte.getLayer('trajet-actif')) carte.setFilter('trajet-actif', ['==', ['get', 'id'], estTrajet ? p.id : '']);
  const genre = estTrajet ? (NOMS_MODE[p.mode] || 'route') : (NOMS_CATEGORIE[p.categorie] || '');
  const panneau = document.getElementById('panneau');
  panneau.innerHTML = `
    <button type="button" class="fermer" aria-label="${L('Fermer le journal', 'Close the journal')}" title="${L('Fermer (Échap)', 'Close (Esc)')}">✕</button>
    <p class="chapitre">${echapper(chapitre(Number(p.debut)))}</p>
    <h2>${echapper(p.nom)}</h2>
    <div class="filet" aria-hidden="true">✦</div>
    <p class="entree-date">${echapper(dateLisible(p.date_edtf))}</p>
    <p class="meta">
      ${genre ? `<span class="badge genre ${echapper(estTrajet ? p.mode : p.categorie)}">${echapper(genre)}</span>` : ''}
      <span class="badge ${echapper(p.certitude)}">${echapper(NOMS_CERTITUDE[p.certitude] || p.certitude)}</span>
    </p>
    ${galerie(p)}
    ${p.description ? `<p class="description">${echapper(p.description)}</p>` : ''}
    ${p.note ? `<p class="note"><strong>${L('Note critique :', 'Critical note:')}</strong> ${echapper(p.note)}</p>` : ''}
    <div class="sources"><strong>${L('Source :', 'Source:')}</strong> ${echapper(p.sources)}</div>`;
  panneau.querySelector('.fermer').addEventListener('click', fermerFiche);
  imagesFiche = lireImages(p);
  panneau.querySelectorAll('.vignette').forEach(b => b.addEventListener('click', () => ouvrirImage(Number(b.dataset.i))));
  panneau.classList.add('ouvert');
  panneau.scrollTop = 0;
}

// Photos et documents d'une fiche : vignettes cliquables (propriété « images » : liste de {src, legende, lien}), comme l'Atlas Aubry
function lireImages(p) {
  let im = p.images;
  if (typeof im === 'string') { try { im = JSON.parse(im); } catch { im = []; } } // MapLibre sérialise les tableaux des propriétés cliquées
  return Array.isArray(im) ? im : [];
}
function galerie(p) {
  const im = lireImages(p);
  if (!im.length) return '';
  return `<div class="galerie">${im.map((d, i) =>
    `<figure><button type="button" class="vignette" data-i="${i}" title="${L('Agrandir', 'Enlarge')}"><img src="${echapper(d.src)}" alt="${echapper(d.legende || '')}" loading="lazy"></button>
     <figcaption>${echapper(d.legende || '')}</figcaption></figure>`).join('')}</div>`;
}
let imagesFiche = [], imageCourante = 0;
function ouvrirImage(i) {
  imageCourante = (i + imagesFiche.length) % imagesFiche.length;
  const d = imagesFiche[imageCourante];
  document.getElementById('lb-image').src = d.src;
  document.getElementById('lb-image').alt = d.legende || '';
  document.getElementById('lb-legende').textContent = d.legende || '';
  document.getElementById('lb-ouvrir').href = d.lien || d.src;
  document.getElementById('lb-ouvrir').textContent = d.lien ? L('Page de l\'image et licence ↗', 'Image page and license ↗') : L('Ouvrir en taille réelle ↗', 'Open full size ↗');
  document.querySelectorAll('.lb-nav').forEach(b => b.hidden = imagesFiche.length < 2);
  document.getElementById('lightbox').hidden = false;
}
function fermerImage() { document.getElementById('lightbox').hidden = true; }
document.getElementById('lb-fermer').addEventListener('click', fermerImage);
document.getElementById('lb-prec').addEventListener('click', () => ouvrirImage(imageCourante - 1));
document.getElementById('lb-suiv').addEventListener('click', () => ouvrirImage(imageCourante + 1));
document.getElementById('lightbox').addEventListener('click', e => { if (e.target.id === 'lightbox') fermerImage(); });
document.addEventListener('keydown', e => {
  if (document.getElementById('lightbox').hidden) return;
  e.stopImmediatePropagation();
  if (e.key === 'Escape') fermerImage();
  if (e.key === 'ArrowLeft') ouvrirImage(imageCourante - 1);
  if (e.key === 'ArrowRight') ouvrirImage(imageCourante + 1);
}, true);
// Texte d'introduction (bouton « À propos » de la légende)
function afficherApropos() {
  if (carte.getLayer('trajet-actif')) carte.setFilter('trajet-actif', ['==', ['get', 'id'], '']);
  const panneau = document.getElementById('panneau');
  panneau.innerHTML = EN ? `
    <button type="button" class="fermer" aria-label="Close" title="Close (Esc)">✕</button>
    <h2>Logbook</h2>
    <div class="filet" aria-hidden="true">✦</div>
    <p class="description">Born near Quebec around 1791, Jean-Baptiste Chalifoux follows his brother Pierre to St. Louis, then moves on to New Mexico. A Taos trapper on the Gila and in the Ute country, he becomes in 1837 the chief of the “Chaguanosos,” a band of Canadians, New Mexicans, Shawnee and Delaware who hire out their rifles to the Californian revolutions and sweep thousands of horses from the missions. Back home, he keeps a small ranch at Embudo, sits as a juror at the trial of the Taos insurgents in 1847, lives in a cave in the riverbank at Charles Autobees's place on the Huerfano, builds the first houses of Trinidad and dies in 1860. His family puts down roots in the Culebra valley, where the Chalifu acequia still bears his name.</p>
    <p>Click a place or a route to open its logbook entry. The color of the dot shows the thread: Chalifoux himself, the Chaguanosos, the family, the companions, or other Chalifouxes of the West who have sometimes been confused with him. The timeline moves by year from 1780 to 1825, then by month from 1826 to 1889. The ▶ button starts the tour.</p>
    <p class="avertissement">Chalifoux was illiterate: his name is spelled Chalifou, Charlefoux, Charlifou, Shalifu, Califa… The sources contradict each other (birth in 1791 or 1798, identity with the “Baptiste Brown” of Brown's Hole): each entry says so. The “other Chalifouxes” points (Green Bay, the Northwest, Oregon, Nisqually) concern namesakes and are not attributed to Jean-Baptiste. The descriptions are translated from the French.</p>
    <p class="avertissement">Main sources: J. Lecompte, “Jean-Baptiste Chalifoux,” in L. R. Hafen (ed.), <em>The Mountain Men and the Fur Trade of the Far West</em>, vol. 7, reprinted in <em>French Fur Traders and Voyageurs in the American West</em> (1995), p. 58-75; A. Janssens, <em>The Life and Adventures in California of Don Agustín Janssens, 1834-1856</em> (Huntington Library, 1953); F. W. Cragin's notebooks; J. W. Nelson, <em>Forgotten Pathfinders</em> (2003); H. H. Bancroft, <em>History of California</em>, vol. II-IV; V. Sanchez, “Chalifu Ditch No. 10” (2012). Full bibliography in the repository README.</p>
    <p class="lien-lettres"><a class="btn-sv" href="inscriptions-en.html">The inscriptions of the Willow Creek trail →</a></p>
    <div class="sources">Olivier J. Caron, Department of Geography, UQAM.</div>` : `
    <button type="button" class="fermer" aria-label="Fermer" title="Fermer (Échap)">✕</button>
    <h2>Journal de bord</h2>
    <div class="filet" aria-hidden="true">✦</div>
    <p class="description">Né près de Québec vers 1791, Jean-Baptiste Chalifoux suit son frère Pierre jusqu'à Saint-Louis, puis passe au Nouveau-Mexique. Trappeur de Taos sur la Gila et dans le pays ute, il devient en 1837 le chef des « Chaguanosos », bande de Canadiens, de Néo-Mexicains, de Shawnees et de Delawares qui louent leurs fusils aux révolutions californiennes et raflent des milliers de chevaux aux missions. Rentré au pays, il tient un petit ranch à Embudo, est juré au procès des insurgés de Taos en 1847, vit dans une grotte de la berge chez Charles Autobees sur la Huerfano, bâtit les premières maisons de Trinidad et meurt en 1860. Sa famille fait souche dans la vallée de la Culebra, où l'acequia Chalifu porte encore son nom.</p>
    <p>Cliquez sur un lieu ou une route pour ouvrir son entrée du journal. La couleur de la pastille indique le fil : Chalifoux lui-même, les Chaguanosos, la famille, les compagnons, ou d'autres Chalifoux de l'Ouest qu'on a parfois confondus avec lui. La timeline avance par année de 1780 à 1825, puis par mois de 1826 à 1889. Le bouton ▶ lance la visite.</p>
    <p class="avertissement">Chalifoux était illettré : son nom s'écrit Chalifou, Charlefoux, Charlifou, Shalifu, Califa… Les sources se contredisent (naissance en 1791 ou 1798, identité avec le « Baptiste Brown » de Brown's Hole) : chaque entrée le signale. Les points « autres Chalifoux » (Green Bay, Nord-Ouest, Oregon, Nisqually) concernent des homonymes et ne sont pas attribués à Jean-Baptiste.</p>
    <p class="avertissement">Sources principales : J. Lecompte, « Jean-Baptiste Chalifoux », dans L. R. Hafen (dir.), <em>The Mountain Men and the Fur Trade of the Far West</em>, vol. 7, repris dans <em>French Fur Traders and Voyageurs in the American West</em> (1995), p. 58-75 ; A. Janssens, <em>The Life and Adventures in California of Don Agustín Janssens, 1834-1856</em> (Huntington Library, 1953) ; carnets de F. W. Cragin ; J. W. Nelson, <em>Forgotten Pathfinders</em> (2003) ; H. H. Bancroft, <em>History of California</em>, vol. II-IV ; V. Sanchez, « Chalifu Ditch No. 10 » (2012). Bibliographie complète dans le README du dépôt.</p>
    <p class="lien-lettres"><a class="btn-sv" href="inscriptions.html">Les inscriptions de la piste du Willow Creek →</a></p>
    <div class="sources">Olivier J. Caron, Département de géographie, UQAM.</div>`;
  panneau.querySelector('.fermer').addEventListener('click', fermerFiche);
  panneau.classList.add('ouvert');
  panneau.scrollTop = 0;
}
document.getElementById('btn-apropos').addEventListener('click', afficherApropos);
// Fermer une fiche ramène la présentation de l'atlas (journal de bord fixe, comme l'Atlas Aubry)
function fermerFiche() {
  if (carte.getLayer('trajet-actif')) carte.setFilter('trajet-actif', ['==', ['get', 'id'], '']);
  afficherApropos();
}
afficherApropos();
document.addEventListener('keydown', e => { if (e.key === 'Escape') fermerFiche(); });
