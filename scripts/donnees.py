"""Construit data/lieux.geojson et data/trajets.geojson de l'Atlas Chalifoux.

Deux sources de fiches :
  1. scripts/reseau_chalifoux.json : les fiches de l'Atlas de l'Amérique française (réseau) qui portent sur
     Jean-Baptiste Chalifoux ou sur d'autres Chalifoux (notice de J. Lecompte, carnets Cragin, livres d'archive.org),
     reprises ici avec un identifiant propre (champ « reseau » = identifiant d'origine) ;
  2. les fiches rédigées pour cet atlas (plus bas), tirées des livres et documents du dossier de l'auteur.

Le champ « categorie » porte le fil du récit (couleur de la pastille) :
  baptiste (Jean-Baptiste Chalifoux), chaguanosos (la bande de Californie, 1837-1840),
  famille (frère, épouses, enfants, descendants), compagnons (associés, compagnons de route),
  homonymes (autres Chalifoux de l'Ouest, non attribués à Jean-Baptiste).

Lancer depuis la racine du dépôt : python3 scripts/donnees.py
"""
import json, datetime, os

ICI = os.path.dirname(os.path.abspath(__file__))

LEC = "J. Lecompte, « Jean-Baptiste Chalifoux », dans L. R. Hafen (dir.), French Fur Traders and Voyageurs in the American West (1995), p. 58-75 (repris de The Mountain Men and the Fur Trade of the Far West, vol. 7)"
NEL = "J. W. Nelson, Forgotten Pathfinders Along the North Branch of the Old Spanish Trail, 1650-1850 (2003), p. 31, 50-51"
SAN = "V. Sanchez, « Chalifu Ditch No. 10, Costilla County, Colorado » (2012), dossier de l'auteur"
ATH = "M. Athearn, An Isolated Empire: A History of Northwest Colorado (BLM, Colorado State Office, 1977 ; rééd. 1982), ch. 2"
TEN = "W. L. Tennent, John Jarvie of Brown's Park (BLM, Utah, 1981), p. 13-14 et n. 9"
CRA = "F. W. Cragin, Early Far West Notebooks (1902-1923), transcription dactylographiée"
BAN = "H. H. Bancroft, History of California, vol. II (1885), Pioneer Register, entrée « Charlefoux »"
CM = "J. Lecompte, « Charles Autobees », The Colorado Magazine, vol. XXXIV, n° 3 (juillet 1957), p. 167-168, n. 28-29 (dossier de l'auteur)"
PHG = "Lecompte, Janet (1978), Pueblo, Hardscrabble, Greenhorn: The Upper Arkansas, 1832-1856, Norman, University of Oklahoma Press"
JAN = "A. Janssens, The Life and Adventures in California of Don Agustín Janssens, 1834-1856, éd. W. H. Ellison et F. Price (Huntington Library, 1953)"


def dec(edtf):
    d = edtf.replace('~', '').replace('?', '')
    p = [int(x) for x in d.split('-')]
    if len(p) == 1:
        return round(p[0] + 0.5, 4)
    j = datetime.date(p[0], p[1], 15) if len(p) == 2 else datetime.date(*p)
    n = 366 if j.year % 4 == 0 else 365
    return round(j.year + ((j - datetime.date(j.year, 1, 1)).days + 0.5) / n, 4)


def precision_de(edtf):
    a = edtf.split('/')[0]
    if '~' in a:
        return 'circa'
    return {1: 'annee', 2: 'mois', 3: 'jour'}[len(a.split('-'))]


LIEUX, TRAJETS = [], []


def L(id, nom, lon, lat, edtf, certitude, membre, description, sources, note='', images=None, reseau=None, precision=None):
    a, b = (edtf.split('/') + [None])[:2]
    LIEUX.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]},
                  "properties": {"id": id, "nom": nom, "debut": dec(a), "fin": dec(b or a), "date_edtf": edtf,
                                 "precision": precision or precision_de(edtf), "certitude": certitude, "categorie": membre,
                                 "description": description, "sources": sources, "note": note, "type": "lieu",
                                 "images": images or [], "reseau": reseau}})


def T(id, nom, coords, edtf, certitude, mode, membre, description, sources, note=''):
    a, b = edtf.split('/')
    TRAJETS.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": coords},
                    "properties": {"id": id, "nom": nom, "debut": dec(a), "fin": dec(b), "date_edtf": edtf, "certitude": certitude,
                                   "mode": mode, "membre": membre, "description": description, "sources": sources,
                                   "note": note, "type": "trajet", "images": []}})


def LOC(fichier, legende):
    return {"src": f"images/photos/{fichier}", "legende": legende}
IMAGES = {
  'L19': [LOC("charles-autobees-portrait.jpg", "Charles Autobees (1812-1882), chez qui Chalifoux vit et meurt sur la Huerfano (photographie ancienne, dossier de l'auteur)")],
  'L23': [LOC("charles-autobees-portrait.jpg", "Charles Autobees, l'hôte des dernières années de Chalifoux (dossier de l'auteur)")],
}

# ------------------------------------------------------------------ 1. Fiches reprises de l'atlas du réseau
# rid -> (identifiant ici, catégorie, changements éventuels)
REPRISES = {
  'F-chalifoux-01': ('L01', 'baptiste', {}),
  'F-chalifoux-02': ('L02', 'famille', {}),
  'F-chalifoux-03': ('L03', 'baptiste', {'certitude': 'hypothetique'}),
  'F-chalifoux-04': ('L04', 'baptiste', {}),
  'F-chalifoux-05': ('L05', 'baptiste', {}),
  'F-chalifoux-06': ('L06', 'baptiste', {}),
  'F-chalifoux-07': ('L07', 'baptiste', {'certitude': 'hypothetique', 'note_plus':
      f" Deux études du BLM reprennent l'identification : pour M. Athearn, Chalifoux, « autrement connu sous le nom de Baptiste Brown », travaille dans la région dès 1820 et découvre la longue vallée de la Green qui portera son nom ({ATH}). W. L. Tennent rapporte les trois thèses (Brown réel, personnage inventé par Inman selon Lecompte, alias de Chalifoux) et juge improbable qu'un homme aussi en vue ait mené une double vie ({TEN})."}),
  'F-chalifoux-08': ('L08', 'baptiste', {'note_plus': " Voir aussi l'Atlas Robidoux, fiche L21."}),
  'F-chalifoux-09': ('L09', 'baptiste', {'coords': [-109.44, 39.56], 'certitude': 'approximative', 'sources_plus': f" ; {NEL}",
      'note': "Nelson situe les inscriptions « Juan Valdez Paso 8 & 9 N 9 1835 », « F.R.B. » et « B. Chalifou » en contrebas de l'accès de Pine Springs au Willow Creek, sur la piste Westwater-Willow Creek de la branche nord de la Vieille piste espagnole ; Chalifoux étant illettré, Valdez aurait gravé les noms. Point placé dans le Willow Creek sous le débouché du Pine Spring Canyon (GNIS), à quelques kilomètres près ; l'inscription de Louis Robidoux (1841) est quelques kilomètres en amont."}),
  'F-chalifoux-10': ('L10', 'chaguanosos', {}),
  'F-chalifoux-11': ('L11', 'chaguanosos', {}),
  'F-chalifoux-12': ('L12', 'chaguanosos', {'sources_plus': f" ; {JAN}, ch. VI-VIII"}),
  'F-chalifoux-13': ('L13', 'chaguanosos', {}),
  'F-chalifoux-14': ('L14', 'chaguanosos', {}),
  'F-chalifoux-15': ('L15', 'chaguanosos', {}),
  'F-chalifoux-16': ('L16', 'chaguanosos', {}),
  'F-chalifoux-17': ('L17', 'baptiste', {'note_plus': " En 1849, Kroenig le trouve encore à Embudo (Colorado Magazine, vol. XXXIV-XXXV)."}),
  'F-chalifoux-18': ('L18', 'famille', {'sources_plus': f" ; {PHG}, p. 196",
      'note_plus': " Janet Lecompte (1978) range « Jean-Baptiste Charlefou » parmi les jurés du procès d'avril 1847 venus des établissements de l'Arkansas, avec Lucien Maxwell, Charles Town, Robert Fisher, Charles Autobees, John L. Hatcher et Asa Estes."}),
  'F-chalifoux-19': ('L19', 'baptiste', {}),
  'F-chalifoux-20': ('L20', 'baptiste', {'note_plus': " A. W. Archibald, interrogé par Cragin, les trouve campés sur le site de Trinidad en novembre 1860 ; le Dr Beshoar (1882) nomme « Jean-B. Charlefou » parmi les colons de 1859 (Cragin, PDF p. 131-134). W. L. Tennent date à tort de 1869 « la première maison de Trinidad »."}),
  'F-chalifoux-21': ('L21', 'famille', {}),
  'F-chalifoux-22': ('L22', 'famille', {}),
  'F-chalifoux-23': ('L23', 'baptiste', {'sources_plus': f" ; {CM}", 'note_plus': " En 1957, Lecompte le faisait encore mourir au ranch d'Autobees « à la fin des années 1860 » et lui attribuait « probablement la première maison » de Trinidad (1860) ; sa notice ultérieure des Mountain Men (vol. 7) fixe la mort au 12 décembre 1860."}),
  'C011': ('L24', 'compagnons', {'certitude': 'hypothetique', 'edtf': '1828', 'nom': "Saint-Louis : « le vieux Charlefou » parmi les compagnons d'Autobees (1828 ?)",
      'sources_plus': f" ; {CM}",
      'note_plus': " Liste de compagnons dressée de mémoire par Tom Autobees, fils de Charles. En examinant chaque nom, Janet Lecompte montre que beaucoup de ces hommes n'ont pas pu partir de Saint-Louis avec Autobees en 1828 : ils furent ses compagnons plus tard. Pour Chalifoux, c'est l'ami des années 1850 sur la Huerfano."}),
  'C014': ('L25', 'baptiste', {'sources_plus': f" ; {PHG}, p. 234-235",
      'note_plus': " Lecompte (1978) précise que les cinq placitas (Doyle, Wootton, Autobees, Kroenig, Juan « Guero » Pais) sont dispersées dans la plaine boisée, et que Jean-Baptiste Charlefou vit, comme d'autres journaliers français et mexicains, dans un « dug-out » creusé dans la berge de la rivière, près de John Smith et de sa femme cheyenne."}),
  'C146': ('L26', 'baptiste', {}),
  'VU-chalifoux-batiste-santa-fe': ('L27', 'baptiste', {'sources_plus': f" ; {PHG}, p. 195",
      'note_plus': " Selon Lecompte (1978), « Baptiste Charlefou » sert comme simple soldat dans la compagnie de volontaires levée par Ceran St. Vrain à Santa Fe pour réprimer la révolte de Taos (janvier 1847), avec d'autres hommes de l'Arkansas : Metcalf, Charles et Tom Autobees, Antoine Cournoyer, Baptiste Sabowrain et Charles Town."}),
  'YY-charlefoux-los-angele': ('L28', 'chaguanosos', {}),
  'CL-charlefoux-charlefou-san-juan-p': ('L29', 'baptiste', {}),
  'CL-charlefoux-charlefou-huerfano': ('L30', 'baptiste', {}),
  'HK-chalifoux-jean-baptiste-miss-district-d': ('L31', 'homonymes', {'note_plus': " Un autre Jean-Baptiste Chalifoux, peut-être un parent : Lecompte signale un Joseph et un Jean-Baptiste Challifoux près de Saint-Louis à cette époque."}),
  'TA-chalifoux-pierre-green-bay': ('L32', 'homonymes', {}),
  'GY-chalifoux-pierre-green-bay': ('L33', 'homonymes', {}),
  'HF-chalifoux-pierre-green-bay': ('L34', 'homonymes', {}),
  'MA-chalifoux-michel-haut-de-la': ('L35', 'homonymes', {}),
  'DG-chalifoux-x-pembina': ('L36', 'homonymes', {}),
  'DG-chalifoux-x-sarcee-cou': ('L37', 'homonymes', {}),
  'CA-chalifoux-chilifaux-spokane-ho': ('L38', 'homonymes', {}),
  'CA-chalifoux-chilifaux-fort-colvi': ('L39', 'homonymes', {}),
  'CA-chalifoux-chilifaux-fort-okana': ('L40', 'homonymes', {}),
  'BB-chalifoux-andre-champoeg-o': ('L41', 'homonymes', {}),
  'F-elucier-15': ('L42', 'homonymes', {'nom': "Saint-Paul (Oregon) : le nom Chalifoux sur la plaque des pionniers"}),
  'CA-chalifoux-baptiste-chaulifou-nisqually': ('L43', 'homonymes', {'note_plus': " Ce Baptiste, serviteur de la Compagnie de la Baie d'Hudson, n'est pas le Chalifoux de Taos, établi au Nouveau-Mexique à la même date."}),
}
HOMONYME = "Homonyme : rien ne permet de l'identifier à Jean-Baptiste Chalifoux de Taos."

vus = set()
for r in json.load(open(os.path.join(ICI, 'reseau_chalifoux.json'), encoding='utf-8')):
    if r['rid'] not in REPRISES or r['rid'] in vus:
        continue
    vus.add(r['rid'])
    nid, cat, ch = REPRISES[r['rid']]
    lon, lat = ch.get('coords', r['coords'])
    note = ch.get('note', r['note'])
    if cat == 'homonymes' and r['rid'] != 'F-elucier-15':
        note = (note + ' ' if note else '') + HOMONYME
    note = (note + ch.get('note_plus', '')).strip()
    sources = r['sources'] + ch.get('sources_plus', '')
    if r.get('pages_pdf'):
        sources += f" (PDF p. {r['pages_pdf']})"
    L(nid, ch.get('nom', r['nom']), lon, lat, ch.get('edtf', r['edtf']), ch.get('certitude', r['certitude']), cat,
      r['description'], sources, note, reseau=r['rid'], images=IMAGES.get(nid))

# ------------------------------------------------------------------ 2. Fiches propres à cet atlas
L('L44', "Willow Creek : « A' Leroux 1835 »", -109.45, 39.58, '1835', 'hypothetique', 'compagnons',
  "Sous un surplomb rocheux, en aval de l'accès de Pine Spring au Willow Creek, Antoine Leroux grave son nom et l'année 1835, l'année même où Juan Valdez taille « B. Chalifou » un peu plus bas. Leroux, guide de Taos, voyage souvent avec les frères Robidoux dans le pays ute ; il guidera l'expédition Gunnison en 1853.",
  f"{NEL}.",
  "Emplacement exact non publié : point placé dans le Willow Creek en aval du Pine Spring Canyon. Le Missouri Historical Society conserve une photographie de 1968 des inscriptions de Leroux et de « F. R. B. Chalifou » (Western Travel Collection, A1734-00001).")
L('L45', "Plaza de los Chalifoux et acequia Chalifu (Costilla)", -105.53, 37.02, '1860/1889', 'hypothetique', 'famille',
  "Dans la vallée de la Costilla, un « Jean Bautista Chalifoux II », appelé Juan Bautista par ses voisins hispanos, fonde la Plaza de los Chalifoux. L'acequia Chalifu n° 10 tire son eau de la rive est du ruisseau Costilla, face à la Placita de los Madrilles, et arrose 400 acres ; son décret de 1889 nomme vingt parciantes, dont « Juan B. Chalifu », époux de Mariana Lucero, également parciante de l'acequia Trujillo.",
  f"{SAN}.",
  "La notice attribue à ce « Chalifoux II » la naissance de 1791 au Québec, celle du trappeur : il s'agit sans doute du fils John B. (Juan Bautista), présent avec sa mère Mariana Lucero au recensement de 1860 (fiche L22). Point placé sur le ruisseau Costilla, près de l'ancienne Placita de los Madrilles ; emplacement à préciser.")
L('L46', "Brown's Park : la tradition de Baptiste Brown", -109.0, 40.87, '1820~/1830', 'hypothetique', 'baptiste',
  "La tradition locale fait d'un « Baptiste Brown » le premier Blanc établi dans la vallée de la Green qu'on appelle Brown's Hole, puis Brown's Park. Pour M. Athearn, ce Brown n'est autre que Jean-Baptiste Chalifoux, qui y aurait trappé dès 1820. Le ranch de John Jarvie, au cœur de la vallée, est aujourd'hui un site historique du BLM.",
  f"{ATH} ; {TEN} ; {LEC}.",
  "Hypothèse disputée : Lecompte tient Baptiste Brown pour un personnage inventé par le colonel Inman (1897). Point au ranch Jarvie (Brown's Park, Utah).")

# ------------------------------------------------------------------ Routes
TAOS = [-105.573, 36.407]
T('T01', "Avec James Baird, d'El Paso à Tucson puis à Janos", [[-106.48, 31.74], [-107.9, 32.3], [-109.3, 32.3], [-110.97, 32.22], [-109.6, 31.3], [-108.19, 30.89]],
  '1826-10/1827-01', 'hypothetique', 'terre', 'baptiste',
  "Fin octobre 1826, les frères Chalifoux quittent El Paso avec James Baird vers la Gila ; Baird meurt en route, ils poussent jusqu'à Tucson puis se retrouvent en prison à Janos en janvier 1827.",
  f"{LEC}.", "Tracé reconstitué entre les lieux connus.")
T('T02', "De Taos au pays ute avec François Robidoux", [TAOS, [-106.32, 36.21], [-107.5, 37.2], [-108.07, 38.75], [-109.29, 39.28], [-109.44, 39.56], [-109.68, 40.09], [-109.92, 40.46]],
  '1827-03/1827-09', 'hypothetique', 'terre', 'baptiste',
  "En mars 1827, Chalifoux part de Taos avec François Robidoux et Maurice LeDuc vers le pays ute. La route probable suit la branche nord de la Vieille piste espagnole : la Gunnison, les Book Cliffs par Westwater et le Willow Creek, jusqu'à l'Uinta.",
  f"{LEC} ; {NEL}.", "Tracé hypothétique par la piste Westwater-Willow Creek, où son nom est gravé en 1835.")
T('T03', "Vers la Californie par la Vieille piste espagnole", [TAOS, [-106.32, 36.21], [-108.5, 37.4], [-110.15, 38.99], [-112.1, 38.6], [-113.6, 37.6], [-115.15, 36.17], [-116.6, 35.0], [-117.44, 34.32], [-118.107, 34.097]],
  '1836-10/1837-01', 'hypothetique', 'terre', 'chaguanosos',
  "À l'automne 1836, Chalifoux mène une trentaine de Néo-Mexicains, de Canadiens, de Shawnees et de Delawares vers la Californie, avec des lainages à troquer contre des chevaux et des mules.",
  f"{LEC}.", "Tracé hypothétique par la Vieille piste espagnole.")
T('T04', "La campagne des Chaguanosos", [[-118.107, 34.097], [-118.461, 34.273], [-116.55, 33.82], [-117.87, 33.77], [-117.161, 32.716], [-117.87, 33.77], [-120.664, 35.28]],
  '1837-01/1837-11', 'approximative', 'terre', 'chaguanosos',
  "Enrôlés par Osio contre Alvarado, les Chaguanosos vont de San Gabriel à San Fernando, campent à Agua Caliente où Janssens les retrouve, marchent sur San Diego, puis, démobilisés sans solde, se paient en chevaux jusqu'à San Luis Obispo.",
  f"{LEC} ; {JAN}.")
T('T05', "La grande razzia de 1840 et le retour", [[-120.664, 35.28], [-118.107, 34.097], [-117.44, 34.32], [-116.32, 35.63], [-115.15, 36.17], [-113.6, 37.6], [-110.15, 38.99], [-108.5, 37.4], TAOS],
  '1840-04/1840-07', 'hypothetique', 'terre', 'chaguanosos',
  "Au printemps 1840, la bande, renforcée de Bill Williams et de Pegleg Smith, enlève des milliers de chevaux aux missions et file par le col Cajon et Agua de Tomasa vers le Nouveau-Mexique.",
  f"{LEC}.", "Retour par la Vieille piste espagnole, tracé hypothétique.")
T('T06', "D'Embudo à la Huerfano puis à Trinidad", [[-105.96, 36.21], TAOS, [-105.43, 37.08], [-105.0, 37.6], [-104.27, 38.2], [-104.45, 37.2], [-104.508, 37.169]],
  '1852/1860-11', 'hypothetique', 'terre', 'baptiste',
  "Dans les années 1850, Chalifoux quitte Embudo pour les établissements de la Huerfano, auprès de Charles Autobees, puis bâtit en 1859-1860 les premières maisons de Trinidad sur la Purgatoire.",
  f"{LEC} ; {CRA}.", "Tracé hypothétique entre les lieux connus.")

os.makedirs('data', exist_ok=True)
for nom, feats in (('lieux', LIEUX), ('trajets', TRAJETS)):
    json.dump({"type": "FeatureCollection", "features": feats}, open(f'data/{nom}.geojson', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(LIEUX), 'lieux,', len(TRAJETS), 'trajets')
