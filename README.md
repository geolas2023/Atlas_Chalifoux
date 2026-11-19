# Atlas Chalifoux (v. 1791–1860)

Atlas géohistorique de Jean-Baptiste Chalifoux, trappeur canadien-français de Taos, chef des « Chaguanosos » en Californie (1837-1840), ranchero d'Embudo et pionnier de la Huerfano et de Trinidad.

Membre du réseau [Atlas de l'Amérique française](https://geolas2023.github.io/Atlas-Les-Canadiens-Fran-ais-de-l-Ouest/). Atlas voisin : [Atlas Robidoux](https://geolas2023.github.io/Les-Robidoux/). En ligne : https://geolas2023.github.io/Atlas_Chalifoux/ (une fois GitHub Pages activé : *Settings → Pages → main / root*).

## Contenu
- 46 lieux et 6 routes, chacun avec une date (EDTF), une certitude de localisation, une description et ses sources.
- Cinq fils, chacun sa couleur : Jean-Baptiste Chalifoux ; les Chaguanosos ; la famille et les descendants ; les compagnons ; les autres Chalifoux de l'Ouest (homonymes : Green Bay, Nord-Ouest, Oregon, Nisqually), placés pour éviter les confusions mais non attribués à Jean-Baptiste.
- Une page « Les inscriptions » (`inscriptions.html`) : « B. Chalifou » et Juan Valdez (1835), A' Leroux (1835), sur la piste Westwater-Willow Creek.
- La timeline va par année de 1780 à 1825, puis par mois de 1826 à 1889. Les liens directs `#lieu=L12` et `#trajet=T03` ouvrent une fiche.

## Sources
- J. Lecompte, « Jean-Baptiste Chalifoux », dans L. R. Hafen (dir.), *The Mountain Men and the Fur Trade of the Far West*, vol. 7, repris dans *French Fur Traders and Voyageurs in the American West* (1995), p. 58-75 : 23 étapes, reprises de l'onglet `chalifoux` de la salle de lecture de l'Atlas de l'Amérique française.
- A. Janssens, *The Life and Adventures in California of Don Agustín Janssens, 1834-1856*, éd. Ellison et Price (Huntington Library, 1953).
- F. W. Cragin, *Early Far West Notebooks* (1902-1923) : Doyle-Wootton, Taos, Trinidad.
- *The Colorado Magazine*, vol. XXXIV-XXXV (Kroenig) ; L. B. Prince, *Historical Sketches of New Mexico* (1883) ; H. H. Bancroft, *History of California*, vol. II (1885).
- J. W. Nelson, *Forgotten Pathfinders Along the North Branch of the Old Spanish Trail* (2003), p. 50-51.
- M. Athearn, *An Isolated Empire: A History of Northwest Colorado* (BLM, 1977) ; W. L. Tennent, *John Jarvie of Brown's Park* (BLM, 1981) : la question de « Baptiste Brown ».
- V. Sanchez, « Chalifu Ditch No. 10, Costilla County, Colorado » (2012).
- Homonymes : Tassé (1878), Dugas (1883), Houck (1908), Masson (1889), Gaston (1912), *Washington Historical Quarterly*, Grignon (1857), *Wisconsin Historical Collections*.

## À dépouiller
Trois livres du dossier de l'auteur dépassent la taille que les outils peuvent lire d'un bloc (plus de 10 Mo) : le journal de Janssens (PDF de 14 Mo, lu jusqu'au ch. IV seulement), H. Inman, *The Old Santa Fe Trail* (Baptiste Brown, 40 Mo) et G. F. Ruxton, *Adventures in Mexico and the Rocky Mountains* (28 Mo). Les découper en parties de moins de 10 Mo permettra de compléter les fiches.

## Données
`python3 scripts/donnees.py` régénère `data/lieux.geojson` et `data/trajets.geojson` (sources : `scripts/reseau_chalifoux.json` et les fiches du script).

Olivier J. Caron, Département de géographie, UQAM.
