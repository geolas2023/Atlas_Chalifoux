// Bouton Street View : activez-le, puis cliquez sur la carte pour ouvrir Google Street View à cet endroit.
function installerStreetView(carte, en) {
  const T = en
    ? { titre: 'Street View: turn on, then click the map', aide: 'Click the map to open Street View there (Esc to cancel)' }
    : { titre: 'Street View : activez, puis cliquez sur la carte', aide: 'Cliquez sur la carte pour ouvrir Street View à cet endroit (Échap pour annuler)' };
  const url = (lng, lat) => `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat.toFixed(6)},${lng.toFixed(6)}`;
  let actif = false, bouton, aide;
  const arret = () => {
    actif = false; bouton.classList.remove('sv-actif'); bouton.setAttribute('aria-pressed', 'false');
    carte.getCanvas().style.cursor = ''; aide.hidden = true;
  };
  carte.addControl({
    onAdd() {
      const div = document.createElement('div');
      div.className = 'maplibregl-ctrl maplibregl-ctrl-group';
      bouton = document.createElement('button');
      bouton.type = 'button'; bouton.title = T.titre; bouton.setAttribute('aria-label', T.titre); bouton.setAttribute('aria-pressed', 'false');
      bouton.textContent = '📷'; bouton.style.fontSize = '15px';
      bouton.onclick = () => {
        if (actif) return arret();
        actif = true; bouton.classList.add('sv-actif'); bouton.setAttribute('aria-pressed', 'true');
        carte.getCanvas().style.cursor = 'crosshair'; aide.hidden = false;
      };
      div.appendChild(bouton);
      aide = document.createElement('div');
      aide.hidden = true; aide.textContent = T.aide;
      aide.style.cssText = 'position:absolute;left:44px;top:0;white-space:nowrap;background:#3b3328;color:#f4efe6;font:12px Georgia,serif;padding:4px 8px;border-radius:3px;pointer-events:none';
      div.style.position = 'relative'; div.appendChild(aide);
      const st = document.createElement('style');
      st.textContent = '.maplibregl-ctrl-group button.sv-actif{background:#c8903e!important}';
      document.head.appendChild(st);
      return div;
    },
    onRemove() {}
  }, 'top-left');
  // fenêtre Street View intégrée (sans clé d'API), avec lien vers Google Maps
  const emb = (lng, lat) => `https://maps.google.com/maps?layer=c&cbll=${lat.toFixed(6)},${lng.toFixed(6)}&cbp=11,0,0,0,0&output=svembed`;
  const m = document.createElement('div');
  m.hidden = true;
  m.style.cssText = 'position:fixed;inset:0;background:rgba(20,16,10,.75);z-index:10000;align-items:center;justify-content:center;padding:16px';
  m.innerHTML = '<div style="background:#fffdf8;width:min(1100px,100%);height:min(720px,90vh);display:flex;flex-direction:column;border:1px solid #8a7a60">'
    + '<div style="display:flex;align-items:center;gap:1rem;padding:.4rem .8rem;border-bottom:1px solid #c9bba3;font-family:Georgia,serif">'
    + '<b style="flex:1">Street View</b><a target="_blank" rel="noopener">Google Maps ↗</a>'
    + '<button type="button" aria-label="' + (en ? 'Close' : 'Fermer') + '" style="font-size:1.4rem;border:0;background:none;cursor:pointer">×</button></div>'
    + '<iframe title="Street View" allowfullscreen referrerpolicy="no-referrer-when-downgrade" style="flex:1;border:0;width:100%"></iframe></div>';
  document.body.appendChild(m);
  const fermer = () => { m.hidden = true; m.style.display = 'none'; m.querySelector('iframe').src = 'about:blank'; };
  m.querySelector('button').onclick = fermer;
  m.addEventListener('click', e => { if (e.target === m) fermer(); });
  const ouvrir = (lng, lat) => {
    m.querySelector('iframe').src = emb(lng, lat); m.querySelector('a').href = url(lng, lat);
    m.hidden = false; m.style.display = 'flex';
  };
  window.ouvrirStreetView = ouvrir;
  // clic sur la carte : Google Maps cherche le panorama le plus proche (nouvel onglet)
  carte.on('click', e => { if (!actif) return; window.open(url(e.lngLat.lng, e.lngLat.lat), '_blank', 'noopener'); arret(); });
  document.addEventListener('keydown', e => { if (e.key !== 'Escape') return; if (actif) arret(); if (!m.hidden) fermer(); });
}
