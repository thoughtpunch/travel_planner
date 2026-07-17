/* Curated, verified real-place photos — Wikimedia Commons, freely licensed,
   hotlinked with attribution. Consumed by /photos.js.
   Each entry: window.TRIP_PHOTOS[pageKey] = { hero, items[] }.
   Every url was curl-verified (HTTP 200 + image content-type) at build time. */
(function () {
  var rome = {
    hero: { place: 'Colosseum', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/3840px-Colosseo_2020.jpg', credit: 'FeaturedPics', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Colosseum' },
    items: [
      { place: 'Roman Forum', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Foro_Romano_Musei_Capitolini_Roma.jpg/3840px-Foro_Romano_Musei_Capitolini_Roma.jpg', credit: 'Wolfgang Moroder', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Roman_Forum' },
      { place: "St. Peter's Basilica", url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/3840px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg', credit: 'Alvesgaspar', license: 'CC BY-SA 4.0', pageLink: "https://en.wikipedia.org/wiki/St._Peter's_Basilica" },
      { place: 'Sistine Chapel', url: 'https://upload.wikimedia.org/wikipedia/commons/8/82/Sistina-interno.jpg', credit: 'Snowdog', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Sistine_Chapel' },
      { place: "Castel Sant'Angelo", url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Castel_Sant%27Angelo_at_Night.jpg/3840px-Castel_Sant%27Angelo_at_Night.jpg', credit: 'Livioandronico2013', license: 'CC BY-SA 4.0', pageLink: "https://en.wikipedia.org/wiki/Castel_Sant'Angelo" },
      { place: 'Pantheon', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Pantheon_%28Rome%29_-_Right_side_and_front.jpg/3840px-Pantheon_%28Rome%29_-_Right_side_and_front.jpg', credit: 'NikonZ7II', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Pantheon,_Rome' },
      { place: 'Trevi Fountain', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Trevi_Fountain_-_Roma.jpg/3840px-Trevi_Fountain_-_Roma.jpg', credit: 'NikonZ7II', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Trevi_Fountain' },
      { place: 'Piazza Navona', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Piazza_Navona_%28Rome%29_at_night.jpg/3840px-Piazza_Navona_%28Rome%29_at_night.jpg', credit: 'NikonZ7II', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Piazza_Navona' },
      { place: 'Apollo and Daphne (Borghese)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Apollo_and_Daphne_%28Bernini%29_%28cropped%29.jpg/3840px-Apollo_and_Daphne_%28Bernini%29_%28cropped%29.jpg', credit: 'Architas', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Apollo_and_Daphne_(Bernini)' },
      { place: 'Capuchin Crypt', url: 'https://upload.wikimedia.org/wikipedia/commons/2/2e/1389RomaSMariaConcezione.jpg', credit: 'Geobia', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Santa_Maria_della_Concezione_dei_Cappuccini' },
      { place: 'Appian Way', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Paesaggio_dell%27Appia_antica.jpg/3840px-Paesaggio_dell%27Appia_antica.jpg', credit: 'LuisaV72', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Appian_Way' },
      { place: 'Gardens of Bomarzo (Park of Monsters)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Monster_in_Parco_dei_Mostri_%28Bomarzo%29.jpg/3840px-Monster_in_Parco_dei_Mostri_%28Bomarzo%29.jpg', credit: 'Livioandronico2013', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Gardens_of_Bomarzo' },
      { place: 'Tarot Garden', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Sculptures_in_Giardino_dei_Tarocchi.jpg/3840px-Sculptures_in_Giardino_dei_Tarocchi.jpg', credit: 'DustyLosAngeles', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Tarot_Garden' },
      { place: 'Civita di Bagnoregio', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Civita_%28Bagnoregio%29_-_Panorama.jpg/3840px-Civita_%28Bagnoregio%29_-_Panorama.jpg', credit: 'Orlando Paride', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Civita_di_Bagnoregio' }
    ]
  };
  var naples = {
    hero: { place: 'Pompeii & Mount Vesuvius', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Aerial_image_of_Pompeii_and_Mount_Vesuvius_%28view_from_the_southeast%29.jpg/3840px-Aerial_image_of_Pompeii_and_Mount_Vesuvius_%28view_from_the_southeast%29.jpg', credit: 'Carsten Steger', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Pompeii' },
    items: [
      { place: 'Mount Vesuvius crater', url: 'https://upload.wikimedia.org/wikipedia/commons/5/5e/Il_cratere_del_Vulcano_-_panoramio.jpg', credit: 'Pietro Scerrato', license: 'CC BY 3.0', pageLink: 'https://en.wikipedia.org/wiki/Mount_Vesuvius' },
      { place: 'Herculaneum', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Antigua_ciudad_de_Herculano%2C_Italia%2C_2023-03-27%2C_DD_135-138_PAN.jpg/3840px-Antigua_ciudad_de_Herculano%2C_Italia%2C_2023-03-27%2C_DD_135-138_PAN.jpg', credit: 'Diego Delso', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Herculaneum' },
      { place: 'The Veiled Christ (Cappella Sansevero)', url: 'https://upload.wikimedia.org/wikipedia/commons/4/48/Cristo_Velato.jpg', credit: 'FabioEspositoWiki', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Veiled_Christ' },
      { place: 'Napoli Sotterranea', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Napoli_Sotterranea_1.jpg/1920px-Napoli_Sotterranea_1.jpg', credit: 'Photo2023', license: 'CC BY 4.0', pageLink: 'https://commons.wikimedia.org/wiki/File:Napoli_Sotterranea_1.jpg' },
      { place: 'National Archaeological Museum (MANN)', url: 'https://upload.wikimedia.org/wikipedia/commons/9/91/Natmuseumnaples.jpg', credit: 'Jeffmatt', license: 'Public domain', pageLink: 'https://en.wikipedia.org/wiki/National_Archaeological_Museum,_Naples' },
      { place: 'Spaccanapoli', url: 'https://upload.wikimedia.org/wikipedia/commons/f/ff/Naples_spaccanapoli.JPG', credit: 'Velvet', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Spaccanapoli_(street)' },
      { place: 'Paestum Greek temples', url: 'https://upload.wikimedia.org/wikipedia/commons/f/fb/Veduta_di_Paestum_2010.jpg', credit: 'Oliver-Bonjoch', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Paestum' },
      { place: 'Neapolitan pizza', url: 'https://upload.wikimedia.org/wikipedia/commons/5/57/Neapolitan_pizza_at_Trappica_%2848701940197%29.jpg', credit: 'Bex Walton', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/Neapolitan_pizza' },
      { place: 'Capri', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Capri_in_Cartolina_-_Vista_da_Termini_%28Massa_Lubrense%29.jpg/1920px-Capri_in_Cartolina_-_Vista_da_Termini_%28Massa_Lubrense%29.jpg', credit: 'Mario Apuzzo', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Capri' },
      { place: 'Procida (Marina Corricella)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Corricella_2016%2C_Procida_%282%29.jpg/3840px-Corricella_2016%2C_Procida_%282%29.jpg', credit: 'Ekrem Canli', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Procida' },
      { place: 'Catacombs of San Gennaro', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Catacombe_di_San_Gennaro_021.jpg/3840px-Catacombe_di_San_Gennaro_021.jpg', credit: 'Dominik Matus', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Catacombs_of_San_Gennaro' },
      { place: 'Certosa di San Martino', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Certosa_di_San_Martino%2C_Naples_%2811%29.jpg/1920px-Certosa_di_San_Martino%2C_Naples_%2811%29.jpg', credit: 'Prof. Mortel', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/Certosa_di_San_Martino' }
    ]
  };
  var sicily = {
    hero: { place: 'Mount Etna, above Catania', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Mt_Etna_and_Catania1.jpg/1920px-Mt_Etna_and_Catania1.jpg', credit: 'BenAveling', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Mount_Etna' },
    items: [
      { place: 'Valley of the Temples, Agrigento', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Valley_of_the_Temples%2C_Agrigento%2C_Sicily_-_49662368756.jpg/1920px-Valley_of_the_Temples%2C_Agrigento%2C_Sicily_-_49662368756.jpg', credit: 'cattan2011', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/Valle_dei_Templi' },
      { place: 'Ear of Dionysius, Syracuse', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Ear_of_Dionysius.jpg/1920px-Ear_of_Dionysius.jpg', credit: 'Michael Wilson', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/Ear_of_Dionysius' },
      { place: 'Teatro Antico di Taormina', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Ancient_Greek-Roman_theatre_%28Taormina%29_15.jpg/1920px-Ancient_Greek-Roman_theatre_%28Taormina%29_15.jpg', credit: 'Derbrauni', license: 'CC BY 4.0', pageLink: 'https://en.wikipedia.org/wiki/Ancient_theatre_of_Taormina' },
      { place: 'Palermo', url: 'https://upload.wikimedia.org/wikipedia/commons/c/c7/Sicilia_Palermo5_tango7174.jpg', credit: 'Tango7174', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Palermo' },
      { place: 'Monreale Cathedral mosaics', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/%22Die_Kathedrale_zeigt_in_besonders_eindrucksvoller_Weise_den_normannisch-arabisch-byzantinischen_Baustil%22_02.jpg/1920px-%22Die_Kathedrale_zeigt_in_besonders_eindrucksvoller_Weise_den_normannisch-arabisch-byzantinischen_Baustil%22_02.jpg', credit: 'Holger Uwe Schmitt', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Monreale_Cathedral' },
      { place: 'Villa Romana del Casale', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Villa_romana_di_Piazza_Armerina_-_Sicilia_-_tigre.JPG/1920px-Villa_romana_di_Piazza_Armerina_-_Sicilia_-_tigre.JPG', credit: 'Robur.q', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Villa_Romana_del_Casale' },
      { place: 'Cefalù', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Cefalu_View_0832.jpg/1920px-Cefalu_View_0832.jpg', credit: 'Ludvig14', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Cefal%C3%B9' },
      { place: 'Capuchin Catacombs, Palermo', url: 'https://upload.wikimedia.org/wikipedia/commons/f/f9/Professionalists%27_Corridor.jpg', credit: 'Sibeaster', license: 'Public domain', pageLink: 'https://en.wikipedia.org/wiki/Catacombe_dei_Cappuccini' },
      { place: 'Aeolian Islands (Lipari)', url: 'https://upload.wikimedia.org/wikipedia/commons/3/3d/Liparic_Islands.jpg', credit: 'Wolfram Schubert', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/Aeolian_Islands' },
      { place: 'Erice', url: 'https://upload.wikimedia.org/wikipedia/commons/c/cd/Erice_-_Stefano_Pannucci.jpg', credit: 'Stefano Pannucci', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Erice' },
      { place: 'San Vito Lo Capo beach', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/San_Vito_Lo_Capo_%281%29.jpg/1920px-San_Vito_Lo_Capo_%281%29.jpg', credit: 'Roberto Fontana', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/San_Vito_Lo_Capo' }
    ]
  };
  var bologna = {
    hero: { place: 'Florence Cathedral (Duomo)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Cattedrale_di_Santa_Maria_del_Fiore_%E2%80%93_Il_Duomo_di_Firenze.jpg/3840px-Cattedrale_di_Santa_Maria_del_Fiore_%E2%80%93_Il_Duomo_di_Firenze.jpg', credit: 'Gary Campbell-Hall', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/Florence_Cathedral' },
    items: [
      { place: 'Museo Ferrari, Maranello', url: 'https://upload.wikimedia.org/wikipedia/commons/e/e8/Mus%C3%A9e_Ferrari_Maranello_0007.JPG', credit: 'Arnaud 25', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Museo_Ferrari' },
      { place: 'Museo Lamborghini', url: 'https://upload.wikimedia.org/wikipedia/commons/d/d3/Mus%C3%A9e_Lamborghini_0128.JPG', credit: 'Arnaud 25', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Lamborghini' },
      { place: 'Piazza Maggiore, Bologna', url: 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Piazza_Maggiore_2025.jpg', credit: 'Nick.mon', license: 'CC0', pageLink: 'https://en.wikipedia.org/wiki/Piazza_Maggiore' },
      { place: 'Two Towers of Bologna', url: 'https://upload.wikimedia.org/wikipedia/commons/3/3b/Asinelli_e_Garisenda.jpg', credit: 'Vanni Lazzari', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Two_Towers_(Bologna)' },
      { place: 'Portico di San Luca, Bologna', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Santuario_della_Beata_Vergine_di_San_Luca.jpg/3840px-Santuario_della_Beata_Vergine_di_San_Luca.jpg', credit: 'Alex.J.Collins', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Sanctuary_of_the_Madonna_di_San_Luca' },
      { place: 'Ponte Vecchio, Florence', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Ponte_Vecchio_from_Ponte_alle_Grazie.jpg/3840px-Ponte_Vecchio_from_Ponte_alle_Grazie.jpg', credit: 'Ingo Mehling', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Ponte_Vecchio' },
      { place: 'David by Michelangelo', url: 'https://upload.wikimedia.org/wikipedia/commons/b/bb/%27David%27_by_Michelangelo_Fir_JBU004.jpg', credit: 'Jörg Bittner Unna', license: 'CC BY 3.0', pageLink: 'https://en.wikipedia.org/wiki/David_(Michelangelo)' },
      { place: 'Stibbert Museum, Florence', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Stibbert_Museum_%2881866%29.jpg/3840px-Stibbert_Museum_%2881866%29.jpg', credit: 'Rhododendrites', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Stibbert_Museum' },
      { place: 'Byzantine mosaics, Ravenna', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Basilica_of_San_Vitale.jpg/3840px-Basilica_of_San_Vitale.jpg', credit: 'Commonists', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Basilica_of_San_Vitale' },
      { place: 'Museo del Violino, Cremona', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Cremona_-_Museo_del_Violino_2.JPG/3840px-Cremona_-_Museo_del_Violino_2.JPG', credit: 'Bimbacami', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Museo_del_Violino' }
    ]
  };
  var bolzano = {
    hero: { place: 'Seceda ridgeline, Dolomites', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Seceda_e_nuvole.jpg/1920px-Seceda_e_nuvole.jpg', credit: 'Luigi Rossini', license: 'CC BY-SA 4.0', pageLink: 'https://commons.wikimedia.org/wiki/File:Seceda_e_nuvole.jpg' },
    items: [
      { place: 'Bolzano', url: 'https://upload.wikimedia.org/wikipedia/commons/1/14/Bozen-Bolzano_from_the_Oswaldpromenade.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/Bolzano' },
      { place: 'Ötzi museum, Bolzano', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/BozenArchMuseum.jpg/3840px-BozenArchMuseum.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/South_Tyrol_Museum_of_Archaeology' },
      { place: 'Ötzi the Iceman (reconstruction)', url: 'https://upload.wikimedia.org/wikipedia/commons/e/ee/Otzi-Quinson.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/%C3%96tzi' },
      { place: 'Earth Pyramids of Ritten', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Renon-Ritten_earth_pyramids_20060121.jpg/1920px-Renon-Ritten_earth_pyramids_20060121.jpg', credit: 'Julian Mendez', license: 'Public domain', pageLink: 'https://en.wikipedia.org/wiki/Earth_pyramids_of_Ritten' },
      { place: 'Lago di Braies', url: 'https://upload.wikimedia.org/wikipedia/commons/3/3e/Pragser_Wildsee_Seekofel_von_Bucht.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/Pragser_Wildsee' },
      { place: 'Bletterbach Canyon', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/%C3%9Adol%C3%AD_%C5%99eky_Bletterbach.jpg/1920px-%C3%9Adol%C3%AD_%C5%99eky_Bletterbach.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/Bletterbach' },
      { place: 'Castel Roncolo, Bolzano', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Runkelstein_Castle_1.jpg/1920px-Runkelstein_Castle_1.jpg', credit: 'User:Mattes', license: 'Public domain', pageLink: 'https://en.wikipedia.org/wiki/Runkelstein_Castle' },
      { place: 'Buonconsiglio Castle, Trento', url: 'https://upload.wikimedia.org/wikipedia/commons/7/76/20110727_Trento_Buonconsiglio_Castle_6609.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/Buonconsiglio_Castle' },
      { place: 'Alpe di Siusi / Seiser Alm', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Saslonch_udu_da_Mont_de_Seuc.jpg/3840px-Saslonch_udu_da_Mont_de_Seuc.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/Seiser_Alm' },
      { place: 'Tre Cime di Lavaredo', url: 'https://upload.wikimedia.org/wikipedia/commons/4/4f/2019_Tre_Cime.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/Tre_Cime_di_Lavaredo' },
      { place: 'Lagazuoi cable car', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Lagazuoi_cable_car_2.jpg/3840px-Lagazuoi_cable_car_2.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/Lagazuoi' }
    ]
  };
  var venice = {
    hero: { place: 'Piazza San Marco', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Piazza_San_Marco_%28Venice%29_at_night-msu-2021-6449-.jpg/3840px-Piazza_San_Marco_%28Venice%29_at_night-msu-2021-6449-.jpg', credit: 'Matthias Süßen', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Piazza_San_Marco' },
    items: [
      { place: "St Mark's Basilica", url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Venezia_Basilica_di_San_Marco_Fassade_2.jpg/3840px-Venezia_Basilica_di_San_Marco_Fassade_2.jpg', credit: 'Zairon', license: 'Public domain', pageLink: "https://en.wikipedia.org/wiki/St_Mark's_Basilica" },
      { place: "Doge's Palace", url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/%28Venice%29_Doge%27s_Palace_and_campanile_of_St._Mark%27s_Basilica_facing_the_sea.jpg/3840px-%28Venice%29_Doge%27s_Palace_and_campanile_of_St._Mark%27s_Basilica_facing_the_sea.jpg', credit: 'Didier Descouens', license: 'CC BY-SA 4.0', pageLink: "https://en.wikipedia.org/wiki/Doge's_Palace" },
      { place: 'Murano', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Murano_sunset.JPG/1920px-Murano_sunset.JPG', credit: 'Wittylama', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Murano' },
      { place: 'Burano', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Burano_Venice_17.jpg/3840px-Burano_Venice_17.jpg', credit: 'kallerna', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Burano' },
      { place: 'Torcello', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Venezia_-_Torcello_01.JPG/1920px-Venezia_-_Torcello_01.JPG', credit: 'Godromil', license: 'Public domain', pageLink: 'https://en.wikipedia.org/wiki/Torcello' },
      { place: 'Grand Canal', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/View_of_the_Grand_Canal_from_Rialto_to_Ca%27Foscari.jpg/3840px-View_of_the_Grand_Canal_from_Rialto_to_Ca%27Foscari.jpg', credit: 'Didier Descouens', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Grand_Canal_(Venice)' },
      { place: 'Rialto Bridge', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Rialto_2025_4.jpg/3840px-Rialto_2025_4.jpg', credit: 'kallerna', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Rialto_Bridge' },
      { place: 'Libreria Acqua Alta', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Libreria_Acqua_Alta_04.jpg/1920px-Libreria_Acqua_Alta_04.jpg', credit: 'Davide Mauro', license: 'CC BY-SA 4.0', pageLink: 'https://commons.wikimedia.org/wiki/File:Libreria_Acqua_Alta_04.jpg' },
      { place: 'Peggy Guggenheim Collection', url: 'https://upload.wikimedia.org/wikipedia/commons/9/97/PI5DAE~2_-_CopyPeggy_Guggenheim_Museum.JPG', credit: 'G.Lanting', license: 'CC BY 3.0', pageLink: 'https://en.wikipedia.org/wiki/Peggy_Guggenheim_Collection' },
      { place: 'Lido di Venezia', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Lido_Aug_2020_1.jpg/3840px-Lido_Aug_2020_1.jpg', credit: 'Kasa Fue', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Lido_di_Venezia' },
      { place: 'Scrovegni Chapel, Padua', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Padova_Cappella_degli_Scrovegni_Innen_Langhaus_West_5.jpg/3840px-Padova_Cappella_degli_Scrovegni_Innen_Langhaus_West_5.jpg', credit: 'Zairon', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Scrovegni_Chapel' },
      { place: 'Verona Arena', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Arena-XE3F2406a.jpg/3840px-Arena-XE3F2406a.jpg', credit: 'Claconvr', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Verona_Arena' }
    ]
  };
  var croatia = {
    hero: { place: 'Dubrovnik City Walls', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Dubrovnik_s_24.jpg/3840px-Dubrovnik_s_24.jpg', credit: 'Diego Delso', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Walls_of_Dubrovnik' },
    items: [
      { place: 'Klis Fortress, above Split', url: 'https://upload.wikimedia.org/wikipedia/commons/5/56/Klis_iz_zraka.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/Klis_Fortress' },
      { place: "Diocletian's Palace, Split", url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Croatia-01239_-_The_Peristil_%289551533404%29.jpg/3840px-Croatia-01239_-_The_Peristil_%289551533404%29.jpg', credit: 'Dennis Jarvis', license: 'CC BY-SA 2.0', pageLink: "https://en.wikipedia.org/wiki/Diocletian's_Palace" },
      { place: 'Split waterfront', url: 'https://upload.wikimedia.org/wikipedia/commons/a/ab/Split_080620-133710-IMG_0968x.jpg', credit: 'Ballota', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Split,_Croatia' },
      { place: 'Bay of Kotor, Montenegro', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/20090719_Crkva_Gospa_od_Zdravlja_Kotor_Bay_Montenegro.jpg/3840px-20090719_Crkva_Gospa_od_Zdravlja_Kotor_Bay_Montenegro.jpg', credit: 'Bracodbk', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Kotor' },
      { place: 'Perast, Bay of Kotor', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Perast_100.jpg/3840px-Perast_100.jpg', credit: 'Ljuba brank', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Perast' },
      { place: 'Plitvice Lakes National Park', url: 'https://upload.wikimedia.org/wikipedia/commons/3/39/View_in_Plitvice_Lakes_National_Park.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/Plitvice_Lakes_National_Park' },
      { place: 'Krka National Park', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Krkawatervallen.jpg/3840px-Krkawatervallen.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA', pageLink: 'https://en.wikipedia.org/wiki/Krka_National_Park' },
      { place: 'Trogir old town', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Trogir_%2820611290808%29.jpg/3840px-Trogir_%2820611290808%29.jpg', credit: 'Mike Norton', license: 'CC BY-SA 2.0', pageLink: 'https://en.wikipedia.org/wiki/Trogir' },
      { place: 'Pula Arena', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Pula_Arena_%282024-10-10_1%29.jpg/3840px-Pula_Arena_%282024-10-10_1%29.jpg', credit: 'Wikimedia Commons', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Pula_Arena' },
      { place: 'Port of Ancona (ferry gateway)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Il_porto_di_Ancona_%282426413820%29.jpg/3840px-Il_porto_di_Ancona_%282426413820%29.jpg', credit: 'Ariel Cerrud', license: 'CC BY-SA 2.0', pageLink: 'https://en.wikipedia.org/wiki/Ancona' }
    ]
  };
  var housing = {
    hero: { place: 'Barga, Garfagnana (Tuscany)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Barga_Panorama_01.jpg/1920px-Barga_Panorama_01.jpg', credit: 'Spike', license: 'CC BY-SA 4.0', pageLink: 'https://commons.wikimedia.org/wiki/File:Barga_Panorama_01.jpg' },
    items: [
      { place: 'Coreglia Antelminelli', url: 'https://upload.wikimedia.org/wikipedia/commons/4/4a/Coreglia_Antelminelli-Rocca.jpg', credit: 'Wokulski', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Coreglia_Antelminelli' },
      { place: 'Castelnuovo di Garfagnana', url: 'https://upload.wikimedia.org/wikipedia/commons/c/c7/Rocca_aroistesca%2C_esterno_03.JPG', credit: 'Sailko', license: 'CC BY 2.5', pageLink: 'https://en.wikipedia.org/wiki/Castelnuovo_di_Garfagnana' },
      { place: 'Bagni di Lucca (Serchio)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Serchio_Ponte_a_Serraglio.JPG/3840px-Serchio_Ponte_a_Serraglio.JPG', credit: 'H005', license: 'Public domain', pageLink: 'https://en.wikipedia.org/wiki/Bagni_di_Lucca' },
      { place: 'Serchio valley', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Serchio-Flowing-Near-Lucca-2012.JPG/3840px-Serchio-Flowing-Near-Lucca-2012.JPG', credit: 'Bjørn Christian Tørrissen', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Serchio' },
      { place: 'Garfagnana (Fornovolasco)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Garfagnana_-_Tal_von_Fornovolasco.JPG/1920px-Garfagnana_-_Tal_von_Fornovolasco.JPG', credit: 'H005', license: 'Public domain', pageLink: 'https://en.wikipedia.org/wiki/Garfagnana' },
      { place: 'Lucca', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Italy_-_Lucca_-_2.jpg/3840px-Italy_-_Lucca_-_2.jpg', credit: 'Arne Müseler', license: 'CC BY-SA 3.0 de', pageLink: 'https://en.wikipedia.org/wiki/Lucca' },
      { place: 'Mestre (Venice belt)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Mestre-Tour_de_l%27horloge.jpg/3840px-Mestre-Tour_de_l%27horloge.jpg', credit: 'Didier Descouens', license: 'CC BY 4.0', pageLink: 'https://en.wikipedia.org/wiki/Mestre' },
      { place: 'Garbatella (Rome belt)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Roma_Garbatella_teatro_Palladium.jpg/3840px-Roma_Garbatella_teatro_Palladium.jpg', credit: 'Blackcat', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Garbatella' },
      { place: 'Casalecchio di Reno (Bologna belt)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Mlntdx-01.jpg/3840px-Mlntdx-01.jpg', credit: 'Maretta Angelini', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Casalecchio_di_Reno' },
      { place: 'Vomero (Naples belt)', url: 'https://upload.wikimedia.org/wikipedia/commons/a/a8/Vomero.jpg', credit: 'Inviaggiocommons', license: 'Public domain', pageLink: 'https://en.wikipedia.org/wiki/Vomero' },
      { place: 'Pozzuoli (Naples belt)', url: 'https://upload.wikimedia.org/wikipedia/commons/a/ab/Pozzuoli_2010-by-RaBoe-23.jpg', credit: 'Ra Boe', license: 'CC BY-SA 3.0 de', pageLink: 'https://en.wikipedia.org/wiki/Pozzuoli' }
    ]
  };

  var rhys = {
    hero: { place: "Naples (Maschio Angioino) — Rhys's 18th", url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Napoli_-_Maschio_Angioino_-_202209302342_3.jpg/3840px-Napoli_-_Maschio_Angioino_-_202209302342_3.jpg', credit: 'Richard Nevell', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Castel_Nuovo' },
    items: [
      naples.items[7], // Neapolitan pizza
      naples.hero,     // Pompeii & Vesuvius
      { place: 'Amalfi Coast', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Amalfi_Coast_%28Italy%2C_October_2020%29_-_75_%2850558355441%29.jpg/3840px-Amalfi_Coast_%28Italy%2C_October_2020%29_-_75_%2850558355441%29.jpg', credit: 'Bruno Rijsman', license: 'CC BY-SA 2.0', pageLink: 'https://en.wikipedia.org/wiki/Amalfi_Coast' },
      bologna.items[9], // Museo del Violino Cremona
      bologna.items[0], // Museo Ferrari
      rome.items[9]     // Appian Way
    ]
  };
  var jude = {
    hero: { place: 'Carrara marble quarries', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Marble_Quarry_near_Carrera.jpg/1920px-Marble_Quarry_near_Carrera.jpg', credit: 'Ingo Mehling', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Carrara_marble' },
    items: [
      bologna.items[0], // Museo Ferrari
      { place: 'Pagani Zonda', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Pagani_Zonda_C12_%27chassis_001%27_Genf_2019_1Y7A5539.jpg/3840px-Pagani_Zonda_C12_%27chassis_001%27_Genf_2019_1Y7A5539.jpg', credit: 'Alexander Migl', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Pagani_Zonda' },
      { place: 'Museo Lamborghini', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Lamborghini_Museum_.jpg/1920px-Lamborghini_Museum_.jpg', credit: 'Valentina 84', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Lamborghini' },
      { place: 'Ducati Museum, Bologna', url: 'https://upload.wikimedia.org/wikipedia/commons/3/3c/Ducati_Museum_%286080034108%29.jpg', credit: 'jimmyweee', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/Ducati' },
      { place: 'Maserati', url: 'https://upload.wikimedia.org/wikipedia/commons/f/f5/Maserati_Mod%C3%A8ne_0002.JPG', credit: 'Arnaud 25', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Maserati' },
      { place: 'Enzo Ferrari Museum, Modena', url: 'https://upload.wikimedia.org/wikipedia/commons/0/0c/Museo_Casa_Enzo_Ferrari_Entrance.jpg', credit: 'Alien life form', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Museo_Casa_Enzo_Ferrari' },
      { place: 'Tourmaline mineral', url: 'https://upload.wikimedia.org/wikipedia/commons/0/00/Tourmaline-121240.jpg', credit: 'Robert M. Lavinsky', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Tourmaline' },
      naples.items[0] // Vesuvius crater
    ]
  };
  var grey = {
    hero: { place: 'Gelato', url: 'https://upload.wikimedia.org/wikipedia/commons/8/89/Gelato_T.jpg', credit: 'Emna Mizouni', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Gelato' },
    items: [
      naples.items[7], // pizza
      { place: 'Tagliatelle', url: 'https://upload.wikimedia.org/wikipedia/commons/6/67/Nests_of_tagliatelle_bolognesi.jpg', credit: 'Paolo Piscolla', license: 'CC BY-SA 2.0', pageLink: 'https://en.wikipedia.org/wiki/Tagliatelle' },
      { place: 'Tortellini', url: 'https://upload.wikimedia.org/wikipedia/commons/4/42/Tortellini_Bolognesi.jpg', credit: 'Angelo.Muratore', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Tortellini' },
      { place: 'Parmigiano-Reggiano', url: 'https://upload.wikimedia.org/wikipedia/commons/d/d1/Parmigiano_Reggiano%2C_Italien%2C_Europ%C3%A4ische_Union.jpg', credit: 'Naturpuur', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Parmesan' },
      { place: 'Sfogliatella', url: 'https://upload.wikimedia.org/wikipedia/commons/8/87/Sfogliatelle_ricce_e_frolle.jpg', credit: 'Saggittarius A', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Sfogliatella' },
      { place: 'Buffalo mozzarella', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Mozzarella_di_bufala3.jpg/3840px-Mozzarella_di_bufala3.jpg', credit: 'Popo le Chien', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Buffalo_mozzarella' },
      { place: 'Venetian cicchetti', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Cicchetti_Venezia_%281%29.jpg/3840px-Cicchetti_Venezia_%281%29.jpg', credit: 'Benreis', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Cicchetti' }
    ]
  };
  var keir = {
    hero: { place: 'Appian Way — Roman gladiator country', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Paesaggio_dell%27Appia_antica.jpg/3840px-Paesaggio_dell%27Appia_antica.jpg', credit: 'LuisaV72', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Appian_Way' },
    items: [
      { place: "Falconry — Harris's hawk", url: 'https://upload.wikimedia.org/wikipedia/commons/6/65/Harris%27s_Hawk_%28Parabuteo_unicinctus%29_3_of_4_in_set.jpg', credit: 'Alan Vernon', license: 'CC BY 2.0', pageLink: "https://en.wikipedia.org/wiki/Harris's_hawk" },
      { place: 'Frasassi Caves', url: 'https://upload.wikimedia.org/wikipedia/commons/2/2c/Genga04.jpg', credit: 'Kessiye', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/Frasassi_Caves' },
      { place: 'Torrechiara Castle (armor)', url: 'https://upload.wikimedia.org/wikipedia/commons/d/dc/Castello_di_Torrechiara.JPG', credit: 'Davide Bolsi', license: 'CC BY 3.0', pageLink: 'https://en.wikipedia.org/wiki/Torrechiara_Castle' },
      venice.items[2], // Murano glass
      naples.items[7], // pizza
      naples.hero      // Pompeii & Vesuvius
    ]
  };

  var activities = {
    hero: bologna.items[0], // Museo Ferrari
    items: [
      { place: 'Ferruccio Lamborghini Museum', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Ferruccio_Lamborghini_Museum.jpg/1920px-Ferruccio_Lamborghini_Museum.jpg', credit: 'TKOIII', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Lamborghini' },
      { place: 'Ducati Museum, Bologna', url: 'https://upload.wikimedia.org/wikipedia/commons/f/f9/Ducati_Museum_%286080034726%29.jpg', credit: 'jimmyweee', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/Ducati' },
      { place: 'Murano glassblowing', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Murano_glassblowing_demo.jpg/1920px-Murano_glassblowing_demo.jpg', credit: 'Wknight94', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Murano_glass' },
      naples.items[7], // pizza
      { place: 'Tagliatelle bolognesi', url: 'https://upload.wikimedia.org/wikipedia/commons/6/67/Nests_of_tagliatelle_bolognesi.jpg', credit: 'Paolo Piscolla', license: 'CC BY-SA 2.0', pageLink: 'https://en.wikipedia.org/wiki/Tagliatelle' },
      { place: 'Gelato', url: 'https://upload.wikimedia.org/wikipedia/commons/8/89/Gelato_T.jpg', credit: 'Emna Mizouni', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Gelato' },
      { place: 'Carrara marble town', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Carrara%2C_veduta_verso_il_centro_storico%2C_avenza_e_il_mare_da_via_salita_sponda_04.jpg/3840px-Carrara%2C_veduta_verso_il_centro_storico%2C_avenza_e_il_mare_da_via_salita_sponda_04.jpg', credit: 'Sailko', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Carrara' },
      rome.hero // Colosseum
    ]
  };
  var adventures = {
    hero: { place: 'Frasassi Caves, Genga (Marche)', url: 'https://upload.wikimedia.org/wikipedia/commons/2/2c/Genga04.jpg', credit: 'Kessiye', license: 'CC BY 2.0', pageLink: 'https://en.wikipedia.org/wiki/Frasassi_Caves' },
    items: [
      { place: 'Scarperia (knife-forging town)', url: 'https://upload.wikimedia.org/wikipedia/commons/a/a3/IMG_0351_Scarperia_Palazzo.JPG', credit: 'Matteo Tani', license: 'Public domain', pageLink: 'https://en.wikipedia.org/wiki/Scarperia_e_San_Piero' },
      { place: 'Gladiator school, Rome', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Il_Gladiatore.jpg/1920px-Il_Gladiatore.jpg', credit: 'Roberto Barone', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Gladiator' },
      bologna.items[7], // Stibbert Museum
      venice.items[1],  // Doge's Palace
      { place: 'Murano glassblowing at the furnace', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Murano_glassblowing_pipe.jpg/1920px-Murano_glassblowing_pipe.jpg', credit: 'Wknight94', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Murano_glass' },
      { place: 'Falconry', url: 'https://upload.wikimedia.org/wikipedia/commons/0/0b/GoshawkFalconry.jpg', credit: 'Aubyn Trevor-Battye', license: 'Public domain', pageLink: 'https://en.wikipedia.org/wiki/Falconry' },
      naples.items[0], // Vesuvius crater
      { place: 'Via ferrata (Dolomites)', url: 'https://upload.wikimedia.org/wikipedia/commons/2/27/Climber_on_fixed_rope_route_Piz_Mitgel_2.jpg', credit: 'Savognin Tourismus', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Via_ferrata' }
    ]
  };
  var worldschooling = {
    hero: { place: "Val d'Orcia, Tuscany", url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/I_cipressi_della_Val_D%27Orcia.jpg/3840px-I_cipressi_della_Val_D%27Orcia.jpg', credit: 'Carlo Cattaneo', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Val_d%27Orcia' },
    items: [
      { place: 'Pistoia, Tuscany', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Pistoia_Cathedral_facade_and_bell_tower_01.jpg/3840px-Pistoia_Cathedral_facade_and_bell_tower_01.jpg', credit: 'Spike', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Pistoia' },
      { place: 'Florence (Piazzale Michelangelo)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Firenze_-_Piazzale_Michelangelo%2C_Firenze%2C_Italy_-_April_6%2C_2015_02.jpg/3840px-Firenze_-_Piazzale_Michelangelo%2C_Firenze%2C_Italy_-_April_6%2C_2015_02.jpg', credit: 'Giorgio Galeotti', license: 'CC BY 4.0', pageLink: 'https://en.wikipedia.org/wiki/Florence' },
      { place: 'Hands-on pasta-making', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Le_orecchiette_di_Bari.jpg/1920px-Le_orecchiette_di_Bari.jpg', credit: 'Maddy16869', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Orecchiette' },
      { place: 'Murano glassblowing', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Murano_glassblowing_demo.jpg/1920px-Murano_glassblowing_demo.jpg', credit: 'Wknight94', license: 'CC BY-SA 3.0', pageLink: 'https://en.wikipedia.org/wiki/Murano_glass' },
      rome.hero, // Colosseum
      { place: 'Venice (aerial)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Venezia_aerial_view.jpg/3840px-Venezia_aerial_view.jpg', credit: 'kallerna', license: 'CC BY-SA 4.0', pageLink: 'https://en.wikipedia.org/wiki/Venice' },
      { place: 'Tuscan countryside', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Grape_vines_and_cypress_trees_in_Tuscany.jpg/1920px-Grape_vines_and_cypress_trees_in_Tuscany.jpg', credit: 'Ian McKellar', license: 'CC BY-SA 2.0', pageLink: 'https://en.wikipedia.org/wiki/Tuscany' }
    ]
  };

  var T = {
    rome: rome, naples: naples, sicily: sicily, bologna: bologna,
    bolzano: bolzano, venice: venice, croatia: croatia, housing: housing,
    rhys: rhys, jude: jude, grey: grey, keir: keir,
    activities: activities, adventures: adventures, worldschooling: worldschooling
  };

  // Composed pages (reuse verified shots)
  T.home = { hero: bolzano.hero, items: [rome.hero, naples.hero, sicily.hero, bologna.hero, venice.hero, croatia.hero, housing.hero] };
  T.plan = { hero: rome.hero, items: [naples.hero, sicily.hero, bologna.hero, bolzano.hero, venice.hero, croatia.hero, housing.hero] };
  T.budget = {
    hero: bologna.items[2], // Piazza Maggiore — living like locals
    items: [naples.items[7], housing.items[6], housing.items[7], housing.items[8], housing.items[9], housing.items[10], housing.items[5], croatia.items[2]]
  };

  window.TRIP_PHOTOS = T;
})();
