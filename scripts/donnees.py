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
PAQ = "E. Paquin, La colonie canadienne-française de Chicago (Chicago, Stromberg, Allen & Cie, 1893), biographie de Joseph Chalifoux (epub Wikisource du Drive de l'auteur)"
PHG = "Lecompte, Janet (1978), Pueblo, Hardscrabble, Greenhorn: The Upper Arkansas, 1832-1856, Norman, University of Oklahoma Press"
BOU = "S. Bouchard et M.-C. Lévesque, Ils ont couru l'Amérique (Montréal, Lux, 2014), ch. « Hommes des montagnes : Provost, Chalifoux, Robidoux »"
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

L('L48', "Fort Uintah : « Jean B. Charlefou » au « rendez-vous de Robidoux » (automne 1839)", -109.98, 40.43, '1839-09/1840-03', 'approximative', 'chaguanosos',
  "À la fin de l'époque des rendez-vous, tant de trappeurs se réunissent au fort Uintah d'Antoine Robidoux qu'on parle du « rendez-vous de Robidoux ». À l'automne 1839 s'y trouvent Bill Williams, Peg-leg Smith, « Jean B. Charlefou » et Frederick « Cut Nose » ; au printemps 1840, ce groupe d'une dizaine ou d'une quinzaine d'hommes part du fort pour aller voler des chevaux en Californie, la grande razzia de 1840.",
  "J. Hardee, « \"Taos Trappers\" and the Demise of the Rocky Mountain Rendezvous », dans Proceedings of the 2015 Fur Trade Symposium: Bent's Fort and the Southern Fur Trade (La Junta, 2016), d'après R. Newell, Memoranda, et J. Lecompte, « Levin Mitchell » (Hafen, Mountain Men, t. V).",
  "Point au fort Uintah (Fort Robidoux), près de Whiterocks (Utah).")

L('L47', "Chicago : Joseph Chalifoux, marin montréalais devenu entrepreneur de pompes funèbres (1867-1893)", -87.6470, 41.8752, '1867/1893', 'approximative', 'homonymes',
  "Né à Montréal en 1841, menuisier puis marin pendant cinq ans, Joseph Chalifoux arrive à Chicago en 1867 avec 75 cents en poche. Il devient entrepreneur de pompes funèbres et propriétaire d'une grande écurie de chevaux de louage, l'un des Canadiens français les mieux établis de la ville. Avec André Leclaire, il offre le tableau des Épousailles à la nouvelle église Notre-Dame.",
  f"{PAQ}.",
  "Homonyme sans lien établi avec Jean-Baptiste Chalifoux. Point placé au premier emplacement de Notre-Dame de Chicago (Halsted et Congress).")

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

# --- Bouchard et Lévesque (2014), « Hommes des montagnes » ---
L('L49', "Haut-Missouri (Dakota) : huit ans d'apprentissage avec son frère Pierre (1804-1812 env.)", -100.35, 44.37, '1804~/1812~', 'hypothetique', 'baptiste',
  "Selon Bouchard et Lévesque, Jean-Baptiste rejoint à treize ans, en 1804, son frère aîné Pierre à Saint-Louis ; celui-ci abandonne alors la vie sédentaire et l'emmène dans les territoires du Dakota, où ils passent au moins huit ans. Jean-Baptiste y apprend le métier des pelleteries. C'est là qu'il aurait subi l'accident qui le fera souffrir toute sa vie : poursuivi par des cavaliers pieds-noirs, il tombe de cheval, se brise les deux jambes et reste caché des jours dans une grotte.",
  f"{BOU}.", "Point symbolique sur le Missouri (secteur de Pierre, Dakota du Sud) : le livre ne précise pas le lieu. Les auteurs s'appuient en partie sur les entrevues des petites-filles Luz Gonzalez et Genoveva Naranjo (années 1950) ; la date de naissance de 1791 reste discutée.")
L('L50', "Saint-Louis : au service de la Missouri Fur Company, puis « free men » (1814-1816)", -90.1880, 38.6270, '1814~/1816~', 'hypothetique', 'baptiste',
  "Revenus du Dakota vers 1812-1814, Jean-Baptiste et Pierre Chalifoux offrent leurs services comme trappeurs et prennent part, pendant deux ans, à plusieurs expéditions vers l'ouest, notamment pour la Missouri Fur Company — peut-être dans la même brigade qu'Étienne Provost. Vers 1816, ils quittent Saint-Louis et rompent avec les Chouteau, Pratte et Lisa pour redevenir traiteurs indépendants ; ils dérivent une dizaine d'années dans les Rocheuses vers le Nouveau-Mexique, où l'on retrouve Provost, Robidoux et Chalifoux à Santa Fe, Embudo et Taos à partir de 1820. Des documents montrent Jean-Baptiste associé à François Robidoux près de Tucson.",
  f"{BOU}.", "Point au quartier du vieux Saint-Louis. Le lien avec Provost est une conjecture des auteurs.")
L('L52', "Brown's Hole : Unami et l'enfant adoptif « Bible Back Brown »", -108.93, 40.86, '1830~/1835~', 'hypothetique', 'famille',
  "Dans la version que retiennent Bouchard et Lévesque, Jean-Baptiste vit cinq ou six ans, tranquille, dans la vallée de la Green avec Unami, une Arapaho, au milieu d'une petite communauté de trappeurs et d'Indiens de passage. Le couple adopte un garçon bossu surnommé Bible Back Brown, parce qu'il porte toujours une bible dans un sac posé sur sa bosse. Avant 1835, Chalifoux quitte femme et fils pour reprendre la piste de Californie. Les auteurs reconnaissent qu'il est difficile de départager faits et roman dans la légende de « Baptiste Brown ».",
  f"{BOU}.", "Même vallée que L07 et L46 ; Lecompte reste sceptique sur l'identification.")


# --- Presse ancienne (Newspapers.com, dépouillement du 20 novembre 2026 ; voir salle-de-lecture.html#journaux) ---
NP = "Newspapers.com (abonnement de l'auteur), consulté le 20 novembre 2026"
def JX(fichier, legende, page):
    return {"src": f"images/journaux/{fichier}", "legende": legende, "lien": f"https://www.newspapers.com/image/{page}/"}
L('L54', "Fort Bent : départ de la grande expédition de Wootton, où « Charlefou » tient le calendrier (automne 1838)", -103.430, 38.040, '1838-09/1840', 'hypothetique', 'compagnons',
  "Selon les souvenirs d'Uncle Dick Wootton, résumés en 1952 par le Pueblo Chieftain, vingt trappeurs partent de Fort Bent à l'automne 1838 pour une campagne de deux ans qui les mène jusqu'au Pacifique. Un Français nommé Charlefou tient le compte des jours sur un bâton carré à encoches ; il le perd le jour où, poursuivi par des Pieds-Noirs, son cheval s'écrase dans un arroyo. Les jambes brisées, il est porté deux mois sur une litière.",
  f"Pueblo Star-Journal and Sunday Chieftain, 6 janv. 1952, p. 8 (R. C. Taylor, « Colorful Colorado »), d'après H. L. Conard, « Uncle Dick » Wootton (1890) ; {NP}.",
  "Le parcours passe par le pays ute et la Californie, ce qui cadre avec Chalifoux au fort Uintah à l'automne 1839 (L48) et en Californie à l'hiver 1839-1840 (L15). La tradition familiale place l'accident des jambes au Dakota (L49).",
  images=[JX("1952-01-06-pueblo-chieftain-wootton-charlefou.jpg", "Pueblo Chieftain, 6 janv. 1952 : l'expédition de 1838, le calendrier de Charlefou et le juré endormi", 1251818427)])
L('L55', "Rancho San Bernardino : une troupe contre les « Indiens Chaguanosos » du col Cajon (1851)", -117.219, 34.047, '1851-05', 'certaine', 'chaguanosos',
  "Dans ses souvenirs, José del Carmen Lugo raconte qu'en mai 1851 un détachement est posté sur son ranch de San Bernardino pour garder la vallée contre « les Indiens Chaguanosos » et les autres voleurs qui entrent par le col Cajon. Onze ans après la grande razzia, le nom de la bande de Chalifoux désigne encore les voleurs de chevaux venus du désert.",
  f"Redlands Daily Facts, 4 avril 1951, p. 6, et 11 mars 1961, p. 10 (F. et B. Moore, « With a Grain of Salt ») ; {NP}.",
  "Point à l'Asistencia de San Bernardino (chemin Barton, Redlands), où vivait Lugo. Seules mentions du mot « Chaguanosos » dans Newspapers.com.",
  images=[JX("1951-04-04-redlands-daily-facts-lugo-chaguanosos.jpg", "Redlands Daily Facts, 4 avril 1951 : Lugo et les Indiens Chaguanosos", 995121274)])
L('L56', "La Veta : mort de Don Leo Chalifu, fils du trappeur (déc. 1917)", -105.008, 37.505, '1917-12', 'certaine', 'famille',
  "Le Santa Fe New Mexican du 3 janvier 1918 annonce, d'après un journal de Walsenburg, la mort récente de Don Leo Chalifu, de La Veta : né à Embudo en 1846, fils d'un Canadien français, il avait accompagné son père en 1858 sur le site de l'actuelle Trinidad.",
  f"Santa Fe New Mexican, 3 janv. 1918, p. 5 (« New Mexico Old-Timer ») ; {NP}.",
  "Il s'agit de José León Chalifoux (1846-1917). Le journal de Walsenburg cité n'a pas été retrouvé.",
  images=[JX("1918-01-03-santa-fe-new-mexican-leo-chalifu.jpg", "Santa Fe New Mexican, 3 janv. 1918 : « New Mexico Old-Timer »", 583672848)])
L('L57', "Alamosa et la vallée de San Luis : les Charlifu (1944-1962)", -105.870, 37.469, '1944/1962', 'approximative', 'famille',
  "Au XXe siècle, les descendants de José León écrivent leur nom « Charlifu ». Le Pueblo Chieftain mentionne Donald Charlifu d'Alamosa (1948), Jake Charlifu, peintre à l'Adams State College (1956), Ursulita Charlifu de La Veta (1959-1960), Daniel et Ellen Charlifu d'Alamosa et Henry Charlifu de Pueblo (1962).",
  f"Pueblo Chieftain, 26 août 1948 ; 16 juillet 1956 ; 7 juillet 1959 ; 30 nov. 1960 ; 9 et 13 juin, 21 août 1962 ; {NP}.",
  "Point sur Alamosa ; les mentions portent aussi sur La Veta et Pueblo.",
  images=[JX("1948-08-26-pueblo-chieftain-donald-charlifu.jpg", "Pueblo Chieftain, 26 août 1948 : Donald Charlifu, d'Alamosa", 1251812458)])

# Découpures ajoutées aux fiches existantes, avec une phrase de note.
PRESSE = {
  'L18': ([JX("1952-01-06-pueblo-chieftain-wootton-charlefou.jpg", "Pueblo Chieftain, 6 janv. 1952 : le juré endormi de Taos, d'après Wootton", 1251818427)],
          " Le Pueblo Chieftain du 6 janvier 1952 reprend l'anecdote de Wootton : Charlefou dort pendant tout le procès et, réveillé, répond qu'il faut pendre l'accusé."),
  'L20': ([JX("1916-06-24-denver-labor-bulletin-trinidad-charlefou.jpg", "Denver Labor Bulletin, 24 juin 1916 : la première cabane, à l'embouchure du Gray's Creek", 897888797),
           JX("1918-01-03-santa-fe-new-mexican-leo-chalifu.jpg", "Santa Fe New Mexican, 3 janv. 1918 : León accompagne son père à Trinidad en 1858", 583672848)],
          " La presse confirme : « Charlefou, un vieux trappeur canadien » a bâti la première cabane à l'embouchure du Gray's Creek l'année avant 1860 (Denver Labor Bulletin, 24 juin 1916) ; son fils León l'y accompagne en 1858 (Santa Fe New Mexican, 3 janv. 1918). Le Gray Creek se jette dans la Purgatoire en aval de Trinidad (USGS, 37,2067 N, 104,4675 O)."),
  'L23': ([JX("1963-03-10-pueblo-chieftain-autobees-charlefou.jpg", "Pueblo Chieftain, 10 mars 1963 : Jean-Baptiste Charlefou parmi les amis d'Autobees", 1252703016)],
          " Le Pueblo Chieftain du 10 mars 1963 le range parmi les amis de Charles Autobees, avec Carson, Bridger, Beaubien et Beckwourth."),
  'L27': ([JX("1894-08-03-santa-fe-new-mexican-volontaires-st-vrain.jpg", "Santa Fe New Mexican, 3 août 1894 : « Tardy Justice » et le rôle de la compagnie St. Vrain", 600359556)],
          " Le Santa Fe New Mexican du 3 août 1894 publie le rôle de la compagnie St. Vrain (23 janv.-20 févr. 1847 ; batailles de La Cañada, d'Embudo et de Taos), avec « Batiste Chalifoux », à l'occasion d'un projet de loi qui accorde enfin solde et pension à ces volontaires."),
  'L28': ([JX("1891-11-15-los-angeles-herald-charlefoux-fusiliers.jpg", "Los Angeles Herald, 15 nov. 1891 : vingt-cinq fusiliers américains sous Charlefoux", 42218920)],
          " Le Los Angeles Herald du 15 novembre 1891 (B. A. Stephens, « North and South ») raconte que Los Angeles lève en mai 1837 vingt-cinq fusiliers américains sous le commandement de Charlefoux."),
  'L45': ([JX("1917-11-16-revista-de-taos-juan-b-chalifu-garcia.jpg", "La Revista de Taos, 16 nov. 1917 : Don Juan B. Chalifu, de Garcia (Colorado)", 168100122),
           JX("1913-11-07-revista-de-taos-suscripcion-juan-b-chalifu.jpg", "La Revista de Taos, 7 nov. 1913 : Juan B. Chalifu dans une souscription", 168081474)],
          " La Revista de Taos nomme « Don Juan B. Chalifu, de Garcia, Colo. », voisin immédiat de Costilla, en 1917, et le compte parmi les donateurs d'une souscription en 1913. En 1917, Don Jesús M. Varela, de Pina, est dit son frère : un demi-frère, ce qui suggère un remariage de Mariana Lucero."),
}
for f_ in LIEUX:
    p = f_['properties']
    if p['id'] in PRESSE:
        ims, txt = PRESSE[p['id']]
        p['images'] = (p.get('images') or []) + ims
        p['note'] = (p['note'] + txt).strip()
        p['sources'] = p['sources'] + f" ; presse : {NP}"

os.makedirs('data', exist_ok=True)
for nom, feats in (('lieux', LIEUX), ('trajets', TRAJETS)):
    json.dump({"type": "FeatureCollection", "features": feats}, open(f'data/{nom}.geojson', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(LIEUX), 'lieux,', len(TRAJETS), 'trajets')
