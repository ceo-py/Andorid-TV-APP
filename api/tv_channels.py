from playwright.sync_api import sync_playwright
import nodriver as uc
import asyncio
import re


ALL_CHANNELS_NOT_SORTED = {
    "Sport": {
        "MATCH! Futbol 3": {
            "url": ["https://www.gledaitv.fan/match-futbol-3-live-tv.html", "https://www.gledaitv.fan/match-futbol-3-alternative-live-tv.html", "https://www.gledaitv.fan/match-futbol-3-hd-live-tv.html"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/russia/match-futbol-3-ru.png",
            "epg_id": "",
            "epg_source": "",
        },
        "MATCH! Futbol 2": {
            "url": ["https://www.gledaitv.fan/match-futbol-2-alternative-live-tv.html", "https://www.gledaitv.fan/match-futbol-2-live-tv.html", "https://www.gledaitv.fan/match-futbol-2-hd-live-tv.html"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/russia/match-futbol-2-ru.png",
            "epg_id": "",
            "epg_source": "",
        },
        "MATCH! Futbol 1": {
            "url": ["https://www.gledaitv.fan/match-futbol-1-live-tv.html"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/russia/match-futbol-1-ru.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Diema Sport": {
            "url": [
                "https://www.gledaitv.fan/diema-sport-live-tv.html",
                "https://www.gledaitv.fan/diema-sport-alternative-live-tv.html",
                "https://www.gledaitv.live/watch-tv/13/diema-sport-online",
                "https://www.seirsanduk.online/?player=11&id=hd-diema-sport-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-diema-sport-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-diema-sport-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/diema-sport-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/diema-sport-hd-bg.png",
            "epg_id": "Diema.Sport.HD.bg",
            "epg_source": "BG1",
        },
        "Diema Sport 2": {
            "url": [
                "https://www.gledaitv.fan/diema-sport-2-alternative-live-tv.html",
                "https://www.gledaitv.fan/diema-sport-2-live-tv.html",
                "https://www.gledaitv.live/watch-tv/12/diema-sport-2-online",
                "https://www.seirsanduk.online/?player=11&id=hd-diema-sport-2-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-diema-sport-2-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-diema-sport-2-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/diema-sport-2-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/diema-sport2-hd-bg.png",
            "epg_id": "Diema.Sport.2.HD.bg",
            "epg_source": "BG1",
        },
        "Diema Sport 3": {
            "url": [
                "https://www.gledaitv.fan/diema-sport-3-alternative-live-tv.html",
                "https://www.gledaitv.fan/diema-sport-3-live-tv.html",
                "https://www.gledaitv.live/watch-tv/38/diema-sport-3-online",
                "https://www.seirsanduk.online/?player=11&id=hd-diema-sport-3-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-diema-sport-3-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-diema-sport-3-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/diema-sport-3-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/diema-sport3-hd-bg.png",
            "epg_id": "Diema.Sport.3.bg",
            "epg_source": "BG1",
        },
        "Eurosport 1 BG": {
            "url": [
                "https://www.gledaitv.fan/eurosport-1-bg-alternative-live-tv.html",
                "https://www.gledaitv.fan/eurosport-1-bg-live-tv.html",
                "https://www.gledaitv.live/watch-tv/33/eurosport-1-online",
                "https://www.seirsanduk.online/?player=11&id=hd-eurosport-1-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-eurosport-1-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-eurosport-1-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/eurosport-1-bg-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/romania/eurosport-1-ro.png",
            "epg_id": "Eurosport.bg",
            "epg_source": "BG1",
        },
        "Eurosport 2 BG": {
            "url": [
                "https://www.gledaitv.fan/eurosport-2-bg-alternative-live-tv.html",
                "https://www.gledaitv.fan/eurosport-2-bg-live-tv.html",
                "https://www.gledaitv.live/watch-tv/34/eurosport-2-online",
                "https://www.seirsanduk.online/?player=11&id=hd-eurosport-2-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-eurosport-2-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-eurosport-2-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/eurosport-2-bg-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/romania/eurosport-2-ro.png",
            "epg_id": "Eurosport.2.bg",
            "epg_source": "BG1",
        },
        "Max One": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=hd-max-one-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-max-one-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-max-one-hd&pass=",
            ],
            "url_hd": "",
            "image": "https://www.predavatel.com/bg/tv/cable-sat_img/max-one.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Max Sport 1": {
            "url": [
                "https://www.gledaitv.fan/max-sport-1-alternative-live-tv.html",
                "https://www.gledaitv.fan/max-sport-1-live-tv.html",
                "https://www.gledaitv.live/watch-tv/9/max-sport-bg-1-online",
                "https://www.seirsanduk.online/?player=11&id=hd-max-sport-1-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-max-sport-1-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-max-sport-1-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/max-sport-1-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/max-sport-1-bg.png",
            "epg_id": "MAX.Sport.1.bg",
            "epg_source": "BG1",
        },
        "Max Sport 2": {
            "url": ["https://www.gledaitv.fan/max-sport-2-alternative-live-tv.html",
                    "https://www.gledaitv.fan/max-sport-2-live-tv.html",
                    "https://www.gledaitv.live/watch-tv/10/max-sport-2-bg-online",
                    "https://www.seirsanduk.online/?player=11&id=hd-max-sport-2-hd&pass=",
                    "https://www.seirsanduk.online/?player=12&id=hd-max-sport-2-hd&pass=",
                    "https://www.seirsanduk.online/?player=13&id=hd-max-sport-2-hd&pass=",
                    ],
            "url_hd": "https://www.gledaitv.fan/max-sport-2-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/max-sport-2-bg.png",
            "epg_id": "MAX.Sport.2.bg",
            "epg_source": "BG1",
        },
        "Max Sport 3": {
            "url": [
                "https://www.gledaitv.fan/max-sport-3-alternative-live-tv.html",
                "https://www.gledaitv.fan/max-sport-3-live-tv.html",
                "https://www.gledaitv.live/watch-tv/11/max-sport-3-bg-online",
                "https://www.seirsanduk.online/?player=11&id=hd-max-sport-3-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-max-sport-3-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-max-sport-3-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/max-sport-3-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/max-sport-3-bg.png",
            "epg_id": "MAX.Sport.3.bg",
            "epg_source": "BG1",
        },
        "Max Sport 4": {
            "url": [
                "https://www.gledaitv.fan/max-sport-4-alternative-live-tv.html",
                "https://www.gledaitv.fan/max-sport-4-live-tv.html",
                "https://www.gledaitv.live/watch-tv/65/max-sport-4-bg-online",
                "https://www.seirsanduk.online/?player=11&id=hd-max-sport-4-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-max-sport-4-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-max-sport-4-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/max-sport-4-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/max-sport-4-bg.png",
            "epg_id": "MAX.Sport.4.bg",
            "epg_source": "BG1",
        },
        "Nova Sport": {
            "url": [
                "https://www.gledaitv.fan/nova-sport-live-tv.html",
                "https://www.gledaitv.fan/nova-sport-alternative-live-tv.html",
                "https://www.gledaitv.live/watch-tv/32/nova-sport-online",
                "https://www.seirsanduk.online/?player=11&id=hd-nova-sport-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-nova-sport-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-nova-sport-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/nova-sport-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/nova-sport-bg.png",
            "epg_id": "Нова.Спорт.bg",
            "epg_source": "BG1",
        },
        "Ring BG": {
            "url": [
                "https://www.gledaitv.fan/ring-bg-alternative-live-tv.html",
                "https://www.gledaitv.fan/ring-bg-live-tv.html",
                "https://www.gledaitv.live/watch-tv/31/ring-bg-online",
                "https://www.seirsanduk.online/?player=11&id=hd-ring-bg-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-ring-bg-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-ring-bg-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/ring-bg-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/ring-bg.png",
            "epg_id": "RING.BG.bg",
            "epg_source": "BG1",
        },
        "TJK Tv": {
            "url": ["https://www.gledaitv.fan/tjk-tv-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/tjk-tv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/tjk-tv-tr.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Trt Spor": {
            "url": ["gledaitv.fan/trt-spor-alternative-live-tv.html", "https://www.gledaitv.fan/trt-spor-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/trt-spor-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/trt-spor-hd-tr.png",
            "epg_id": "TRT.TÜRK.tr",
            "epg_source": "TR1",
        },
        "DAZN Combat": {
            "url": ["https://www.parsatv.com/name=DAZN-Combat#sport"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/8/83/DAZN_2019_logo.svg/revision/latest/scale-to-width-down/200?cb=20210824002335",
            "epg_id": "",
            "epg_source": "",
        },
        "Red Bull TV": {
            "url": ["https://www.parsatv.com/name=Red-Bull-TV#sport"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/international/red-bull-tv-int.png",
            "epg_id": "Red.Bull.TV.cz",
            "epg_source": "CZ1",
        },
        "Fuel TV": {
            "url": ["https://www.parsatv.com/name=Fuel-TV#sport"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/portugal/fueltv-pt.png",
            "epg_id": "",
            "epg_source": "",
        },
        "SportItalia": {
            "url": ["https://www.parsatv.com/name=Sportitalia#sport"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/italy/hd/sportitalia-hd-it.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Super Tennis": {
            "url": ["https://www.parsatv.com/name=Super-Tennis#sport"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/italy/super-tennis-it.png",
            "epg_id": "SuperTennis.HD.it",
            "epg_source": "IT1",
        },
        "beIN Sports Xtra": {
            "url": ["https://www.parsatv.com/name=beIN-Sports-Xtra#sport"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/bein-sports-xtra-us.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Fifa +": {
            "url": ["https://www.parsatv.com/name=FIFA-Plus#sport"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/9/9c/FIFA%2B_%282025%29.svg/revision/latest/scale-to-width-down/300?cb=20250521135758",
            "epg_id": "",
            "epg_source": "",
        },
        "NHL TV": {
            "url": ["https://www.parsatv.com/name=NHL-TV"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/nhl-network-us.png",
            "epg_id": "NHL.Network.HD.us2",
            "epg_source": "US2",
        },
        "Canal Motor": {
            "url": ["https://www.parsatv.com/name=Canal-Motor#sport"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/8/8e/Motors_TV.svg/revision/latest/scale-to-width-down/300?cb=20100330070517",
            "epg_id": "",
            "epg_source": "",
        },
        "RTA Sport": {
            "url": ["https://www.parsatv.com/name=RTA-Sport#afghan"],
            "url_hd": "",
            "image": "https://i.postimg.cc/6qDg2JN8/rtasport.png",
            "epg_id": "",
            "epg_source": "",
        },
        "KTV Sport 2": {
            "url": ["https://www.parsatv.com/name=KTV-Sport-2#google_vignette"],
            "url_hd": "",
            "image": "https://i.imgur.com/l4oX0gf.png",
            "epg_id": "",
            "epg_source": "",
        },
        "KTV Sport": {
            "url": ["https://www.parsatv.com/name=KTV-Sport#google_vignette"],
            "url_hd": "",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQa6mip7K-sKyWYmM_8hE6hSUFIzk1fkz4PCw&s",
            "epg_id": "",
            "epg_source": "",
        },
        "NBA TV": {
            "url": ["https://freetv.studio/channel/NBATV.us"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/nba-tv-us.png",
            "epg_id": "NBA.TV.HD.us2",
            "epg_source": "US2",
        },
    },
    "Movie": {
        "AMC": {
            "url": ["https://www.gledaitv.fan/amc-live-tv.html", "https://www.gledaitv.fan/amc-alternative-live-tv.html", "https://www.gledaitv.live/watch-tv/66/amc-online"],
            "url_hd": "https://www.gledaitv.fan/amc-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/amc-us.png",
            "epg_id": "AMC.bg",
            "epg_source": "BG1",
        },
        "AXN": {
            "url": [
                "https://www.gledaitv.fan/axn-live-tv.html",
                "https://www.gledaitv.fan/axn-alternative-live-tv.html",
                "https://www.gledaitv.live/watch-tv/59/axn-online",
                "https://www.seirsanduk.online/?player=11&id=axn&pass=",
                "https://www.seirsanduk.online/?player=12&id=axn&pass=",
                "https://www.seirsanduk.online/?player=13&id=axn&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/axn-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/serbia/axn-rs.png",
            "epg_id": "AXN.bg",
            "epg_source": "BG1",
        },
        "AXN Black": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=axn-black&pass=",
                "https://www.seirsanduk.online/?player=12&id=axn-black&pass=",
                "https://www.seirsanduk.online/?player=13&id=axn-black&pass=",
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/romania/axn-black-ro.png",
            "epg_id": "AXN.Black.bg",
            "epg_source": "BG1",
        },
        "AXN White": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=axn-white&pass=",
                "https://www.seirsanduk.online/?player=12&id=axn-white&pass=",
                "https://www.seirsanduk.online/?player=13&id=axn-white&pass=",
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/romania/axn-white-ro.png",
            "epg_id": "AXN.White.bg",
            "epg_source": "BG1",
        },
        "bTV Action": {
            "url": [
                "https://www.gledaitv.fan/btv-action-live-tv.html", 
                "https://www.gledaitv.fan/btv-action-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-btv-action-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-btv-action-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-btv-action-hd&pass=",
                ],
            "url_hd": "https://www.gledaitv.fan/btv-action-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/btv-action-bg.png",
            "epg_id": "bTV.Action.bg",
            "epg_source": "BG1",
        },
        "bTV Cinema": {
            "url": [
                "https://www.gledaitv.fan/btv-cinema-live-tv.html", 
                "https://www.gledaitv.fan/btv-cinema-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=btv-cinema&pass=",
                "https://www.seirsanduk.online/?player=12&id=btv-cinema&pass=",
                "https://www.seirsanduk.online/?player=13&id=btv-cinema&pass=",
                    ],
            "url_hd": "https://www.gledaitv.fan/btv-cinema-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/btv-cinema-bg.png",
            "epg_id": "bTV.Cinema.bg",
            "epg_source": "BG1",
        },
        "bTV Comedy": {
            "url": [
                "https://www.gledaitv.fan/btv-comedy-live-tv.html", 
                "https://www.gledaitv.fan/btv-comedy-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-btv-comedy-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-btv-comedy-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-btv-comedy-hd&pass=",
                    ],
            "url_hd": "https://www.gledaitv.fan/btv-comedy-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/btv-comedy-bg.png",
            "epg_id": "bTV.Comedy.bg",
            "epg_source": "BG1",
        },
        "bTV Lady": {
            "url": [
                "https://www.gledaitv.fan/btv-lady-live-tv.html",
                "https://www.gledaitv.fan/btv-lady-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=btv-story&pass=",
                "https://www.seirsanduk.online/?player=12&id=btv-story&pass=",
                "https://www.seirsanduk.online/?player=13&id=btv-story&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/btv-lady-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/btv-lady-bg.png",
            "epg_id": "bTV.Story.bg",
            "epg_source": "BG1",
        },
        "Diema": {
            "url": [
                "https://www.gledaitv.fan/diema-live-tv.html",
                "https://www.gledaitv.fan/diema-alternative-live-tv.html",
                "https://www.gledaitv.live/watch-tv/52/diema-online",
                "https://www.seirsanduk.online/?player=11&id=hd-diema-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-diema-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-diema-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/diema-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/diema-bg.png",
            "epg_id": "Диема.bg",
            "epg_source": "BG1",
        },
        "Diema Family": {
            "url": [
                "https://www.gledaitv.fan/diema-family-live-tv.html",
                "https://www.gledaitv.fan/diema-family-alternative-live-tv.html",
                "https://www.gledaitv.live/watch-tv/51/diema-family-online",
                "https://www.seirsanduk.online/?player=11&id=hd-diema-family-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-diema-family-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-diema-family-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/diema-family-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/diema-family-bg.png",
            "epg_id": "Диема.Фемили.bg",
            "epg_source": "BG1",
        },
        "Epic Drama": {
            "url": [
                "https://www.gledaitv.fan/epic-drama-live-tv.html",
                "https://www.gledaitv.fan/epic-drama-alternative-live-tv.html",
                "https://www.gledaitv.live/watch-tv/75/epic-drama-online",
                "https://www.seirsanduk.online/?player=11&id=hd-epic-drama-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-epic-drama-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-epic-drama-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/epic-drama-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/serbia/epic-drama-rs.png",
            "epg_id": "Epic.Drama.bg",
            "epg_source": "BG1",
        },
        "FilmBox Extra": {
            "url": ["https://www.gledaitv.fan/filmbox-extra-live-tv.html", "https://www.gledaitv.fan/filmbox-extra-alternative-live-tv.html", "https://www.gledaitv.live/watch-tv/49/film-box-extra-online"],
            "url_hd": "https://www.gledaitv.fan/filmbox-extra-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/international/filmbox-extra-int.png",
            "epg_id": "FilmBox.Extra.HD.bg",
            "epg_source": "BG1",
        },
        "FilmBox Stars": {
            "url": ["https://www.gledaitv.fan/filmbox-stars-live-tv.html", "https://www.gledaitv.fan/filmbox-stars-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/filmbox-stars-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/international/filmbox-stars-int.png",
            "epg_id": "FilmBox.Stars.bg",
            "epg_source": "BG1",
        },
        "FilmBox Plus": {
            "url": [],
            "url_hd": "https://www.gledaitv.live/watch-tv/48/film-box-plus-online",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/international/filmbox-plus-int.png",
            "epg_id": "FilmBox.bg",
            "epg_source": "BG1",
        },
        "ID Xtra": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=hd-id-xtra-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-id-xtra-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-id-xtra-hd&pass=",
            ],
            "url_hd": "",
            "image": "https://ngimg.siol.tv/sioltv/logo/color/discidx.png?height=60",
            "epg_id": "ID.Xtra.HD.rs",
            "epg_source": "RS1",
        },
        "Kino Nova": {
            "url": [
                "https://www.gledaitv.fan/kino-nova-live-tv.html",
                "https://www.gledaitv.fan/kino-nova-alternative-live-tv.html",
                "https://www.gledaitv.live/watch-tv/44/kino-nova-online",
                "https://www.seirsanduk.online/?player=11&id=hd-kino-nova-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-kino-nova-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-kino-nova-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/kino-nova-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/kino-nova-bg.png",
            "epg_id": "KinoNova.bg",
            "epg_source": "BG1",
        },
        "Movie Star": {
            "url": ["https://www.gledaitv.fan/movie-star-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/movie-star-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/movie-star-bg.png",
            "epg_id": "MovieSTAR.bg",
            "epg_source": "BG1",
        },
        "STAR Channel": {
            "url": [
                "https://www.gledaitv.fan/star-channel-alternative-live-tv.html",
                "https://www.gledaitv.fan/star-channel-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-star-channel-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-star-channel-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-star-channel-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/star-channel-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/star-channel-bg.png",
            "epg_id": "StarChannel.bg",
            "epg_source": "BG1",
        },
        "Star Crime": {
            "url": [
                "https://www.gledaitv.fan/star-crime-alternative-live-tv.html",
                "https://www.gledaitv.fan/star-crime-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-star-crime-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-star-crime-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-star-crime-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/star-crime-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/star-crime-bg.png",
            "epg_id": "StarCrime.bg",
            "epg_source": "BG1",
        },
        "Star Life": {
            "url": [
                "https://www.gledaitv.fan/star-tv-live-tv.html",
                "https://www.gledaitv.fan/star-life-alternative-live-tv.html",
                "https://www.gledaitv.live/watch-tv/46/fox-life-online",
                "https://www.seirsanduk.online/?player=11&id=hd-star-life-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-star-life-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-star-life-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/star-life-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/star-life-bg.png",
            "epg_id": "StarLife.bg",
            "epg_source": "BG1",
        },
    },
    "Science": {
        "Food Network": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=hd-food-network-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-food-network-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-food-network-hd&pass=",
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/food-network-us.png",
            "epg_id": "Food.Network.HD.bg",
            "epg_source": "BG1",
        },
        "Animal Planet": {
            "url": ["https://www.gledaitv.fan/animal-planet-live-tv.html", "https://www.gledaitv.fan/animal-planet-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/animal-planet-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/animal-planet-us.png",
            "epg_id": "Animal.Planet.bg",
            "epg_source": "BG1",
        },
        "Discovery Channel": {
            "url": [
                "https://www.gledaitv.fan/discovery-channel-alternative-live-tv.html",
                "https://www.gledaitv.fan/discovery-channel-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-discovery-channel-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-discovery-channel-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-discovery-channel-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/discovery-channel-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/discovery-channel-us.png",
            "epg_id": "Discovery.Channel.bg",
            "epg_source": "BG1",
        },
        "DMAX": {
            "url": ["https://www.gledaitv.fan/dmax-live-tv.html", "https://www.gledaitv.fan/dmax-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/dmax-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/spain/dmax-es.png",
            "epg_id": "DMAX.es",
            "epg_source": "ES1",
        },
        "DocuBox": {
            "url": ["https://www.gledaitv.fan/docubox-live-tv.html", "https://www.gledaitv.fan/docubox-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/docubox-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/docubox-bg.png",
            "epg_id": "DocuBox.hr",
            "epg_source": "HR1",
        },
        "History Channel": {
            "url": [""
                    "https://www.gledaitv.fan/test-h-live-tv.html", "https://www.gledaitv.fan/test-h-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/test-h-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/history-channel-us.png",
            "epg_id": "History.bg",
            "epg_source": "BG1",
        },
        "Investigation Discovery": {
            "url": [
                "https://www.gledaitv.fan/investigation-discovery-live-tv.html",
                "https://www.gledaitv.fan/investigation-discovery-alternative-live-tv.html",
            ],
            "url_hd": "https://www.gledaitv.fan/investigation-discovery-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/international/investigation-discovery-int.png",
            "epg_id": "Investigation.Discovery.bg",
            "epg_source": "BG1",
        },
        "Nat Geo Wild": {
            "url": [
                "https://www.gledaitv.fan/nat-geo-wild-live-tv.html",
                "https://www.gledaitv.fan/nat-geo-wild-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-nat-geo-wild-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-nat-geo-wild-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-nat-geo-wild-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/nat-geo-wild-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/nat-geo-wild-us.png",
            "epg_id": "Nat.Geo.Wild.bg",
            "epg_source": "BG1",
        },
        "National Geographic": {
            "url": [
                "https://www.gledaitv.fan/national-geographic-live-tv.html",
                "https://www.gledaitv.fan/national-geographic-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-nat-geo-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-nat-geo-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-nat-geo-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/national-geographic-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/national-geographic-us.png",
            "epg_id": "National.Geographic.Channel.bg",
            "epg_source": "BG1",
        },
        "TLC": {
            "url": [
                "https://www.gledaitv.fan/tlc-live-tv.html",
                "https://www.gledaitv.fan/tlc-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=tlc&pass=",
                "https://www.seirsanduk.online/?player=12&id=tlc&pass=",
                "https://www.seirsanduk.online/?player=13&id=tlc&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/tlc-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/international/tlc-int.png",
            "epg_id": "TLC.Balkans.bg",
            "epg_source": "BG1",
        },
        "TRT Belgesel": {
            "url": ["https://www.gledaitv.fan/trt-belgesel-live-tv.html", "https://www.gledaitv.fan/trt-belgesel-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/trt-belgesel-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/trt-belgesel-tr.png",
            "epg_id": "TRT.BELGESEL.tr",
            "epg_source": "TR1",
        },
        "Viasat Explore": {
            "url": [
                "https://www.gledaitv.fan/viasat-explore-live-tv.html",
                "https://www.gledaitv.fan/viasat-explore-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-viasat-explore-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-viasat-explore-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-viasat-explore-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/viasat-explore-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/romania/viasat-explore-ro.png",
            "epg_id": "Viasat.Explorer.bg",
            "epg_source": "BG1",
        },
        "Viasat History": {
            "url": ["https://www.gledaitv.fan/viasat-history-live-tv.html", "https://www.gledaitv.fan/viasat-history-alternative-live-tv.html"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/romania/viasat-history-ro.png",
            "epg_id": "Viasat.History.bg",
            "epg_source": "BG1",
        },
        "Viasat Nature": {
            "url": ["https://www.gledaitv.fan/viasat-nature-live-tv.html", "https://www.gledaitv.fan/viasat-nature-alternative-live-tv.html"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/romania/viasat-nature-ro.png",
            "epg_id": "Viasat.Nature.bg",
            "epg_source": "BG1",
        },
        "Yaban Tv": {
            "url": ["https://www.gledaitv.fan/yaban-tv-live-tv.html", "https://www.gledaitv.fan/yaban-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/yaban-tv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/yaban-tr.png",
            "epg_id": "",
            "epg_source": "",
        },
    },
    "News": {
        "Bulgaria ON AIR Tv": {
            "url": [
                "https://www.gledaitv.fan/bulgaria-on-air-tv-live-tv.html",
                "https://www.gledaitv.fan/bulgaria-on-air-tv-alternative-live-tv.html"
            ],
            "url_hd": "https://www.gledaitv.fan/bulgaria-on-air-tv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/bulgaria-on-air-bg.png",
            "epg_id": "България.он.еър.bg",
            "epg_source": "BG1",
        },
        "EuroNews Bulgaria": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=hd-euronews-bulgaria-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-euronews-bulgaria-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-euronews-bulgaria-hd&pass=",
            ],
            "url_hd": "",
            "image": "https://www.predavatel.com/bg/tv/cable-sat_img/euronews.svg",
            "epg_id": "",
            "epg_source": "",
        },
        "Nova News": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=hd-nova-news-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-nova-news-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-nova-news-hd&pass=",
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/nova-news-bg.png",
            "epg_id": "NOVANEWS.bg",
            "epg_source": "BG1",
        },
        "Kanal 3": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=kanal-3&pass=",
                "https://www.seirsanduk.online/?player=12&id=kanal-3&pass=",
                "https://www.seirsanduk.online/?player=13&id=kanal-3&pass=",
            ],
            "url_hd": "",
            "image": "https://www.predavatel.com/bg/6/dobrich_img/tv-kanal3.png",
            "epg_id": "",
            "epg_source": "",
        },
        "BNT 1": {
            "url": [
                "https://www.gledaitv.fan/bnt-1-live-tv.html",
                "https://www.gledaitv.fan/bnt-1-alternative-live-tv.html",
                "https://tv.bnt.bg/bnt1",
                "https://www.seirsanduk.online/?player=11&id=hd-bnt-1-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-bnt-1-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-bnt-1-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/bnt-1-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/bnt-1-bg.png",
            "epg_id": "БНТ1.bg",
            "epg_source": "BG1",
        },
        "BNT 2": {
            "url": [
                "https://www.gledaitv.fan/bnt-2-live-tv.html",
                "https://www.gledaitv.fan/bnt-2-alternative-live-tv.html",
                "https://tv.bnt.bg/bnt2",
                "https://www.seirsanduk.online/?player=11&id=bnt-2&pass=",
                "https://www.seirsanduk.online/?player=12&id=bnt-2&pass=",
                "https://www.seirsanduk.online/?player=13&id=bnt-2&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/bnt-2-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/bnt-2-bg.png",
            "epg_id": "БНТ2.bg",
            "epg_source": "BG1",
        },
        "BNT 3": {
            "url": [
                "https://www.gledaitv.fan/bnt-3-live-tv.html",
                "https://www.gledaitv.fan/bnt-3-alternative-live-tv.html",
                "https://tv.bnt.bg/bnt3",
                "https://www.seirsanduk.online/?player=11&id=bnt-3&pass=",
                "https://www.seirsanduk.online/?player=12&id=bnt-3&pass=",
                "https://www.seirsanduk.online/?player=13&id=bnt-3&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/bnt-3-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/bnt-3-bg.png",
            "epg_id": "БНТ 3 HD.bg",
            "epg_source": "GLOBETV2",
        },
        "BNT 4": {
            "url": [
                "https://www.gledaitv.fan/bnt-4-live-tv.html",
                "https://www.gledaitv.fan/bnt-4-alternative-live-tv.html",
                "https://tv.bnt.bg/bnt4",
                "https://www.seirsanduk.online/?player=11&id=bnt-4&pass=",
                "https://www.seirsanduk.online/?player=12&id=bnt-4&pass=",
                "https://www.seirsanduk.online/?player=13&id=bnt-4&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/bnt-4-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/bnt-4-bg.png",
            "epg_id": "БНТ 4 HD.bg",
            "epg_source": "GLOBETV2",
        },
        "bTV": {
            "url": [
                "https://www.gledaitv.fan/btv-live-tv.html",
                "https://www.gledaitv.fan/btv-alternative-live-tv.html",
                "https://btvplus.bg/live/",
                "https://www.seirsanduk.online/?player=11&id=hd-btv-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-btv-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-btv-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/btv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/btv-bg.png",
            "epg_id": "bTV.bg",
            "epg_source": "BG1",
        },
        "BLOOMBERG TV": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=bloomberg-tv&pass=",
                "https://www.seirsanduk.online/?player=12&id=bloomberg-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=bloomberg-tv&pass=",
            ],
            "url_hd": "https://www.bloombergtv.bg/video",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/bloomberg-tv-bulgaria-bg.png",
            "epg_id": "Bloomberg.TV.Bulgaria.bg",
            "epg_source": "BG1",
        },
        "VTK": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=vtk&pass=",
                "https://www.seirsanduk.online/?player=12&id=vtk-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=vtk-tv&pass=",
            ],
            "url_hd": "",
            "image": "https://www.predavatel.com/bg/tv/cable-sat_img/vtk.svg",
            "epg_id": "VTK.bg",
            "epg_source": "GLOBETV2",
        },
        "SKAT": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=skat&pass=",
                "https://www.seirsanduk.online/?player=12&id=skat-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=skat-tv&pass=",
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/skat-bg.png",
            "epg_id": "СКАТ.bg",
            "epg_source": "GLOBETV2",
        },
        "7/8 TV": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=hd-78-tv-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-78-tv-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-78-tv-hd&pass=",
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/7-8-tv-bg.png",
            "epg_id": "7/8 TV HD.bg",
            "epg_source": "GLOBETV2",
        },
        "Evrokom": {
            "url": [
                "https://eurocom.bg/live",
                "https://www.seirsanduk.online/?player=11&id=evrokom&pass=",
                "https://www.seirsanduk.online/?player=12&id=evrokom&pass=",
                "https://www.seirsanduk.online/?player=13&id=evrokom&pass=",
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/evrokom-bg.png",
            "epg_id": "Евроком.НКТВ.bg",
            "epg_source": "BG1",
        },
        "Nova": {
            "url": [
                "https://www.gledaitv.fan/nova-live-tv.html",
                "https://www.gledaitv.fan/nova-alternative-live-tv.html",
                "https://nova.bg/live",
                "https://www.seirsanduk.online/?player=11&id=hd-nova-tv-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-nova-tv-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-nova-tv-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/nova-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/nova-bg.png",
            "epg_id": "Нова.телевизия.bg",
            "epg_source": "BG1",
        },
    },
    "Kids": {
        "Cartoon Network": {
            "url": [
                "https://www.gledaitv.fan/cartoon-network-live-tv.html",
                "https://www.gledaitv.fan/cartoon-network-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=cartoon-network&pass=",
                "https://www.seirsanduk.online/?player=12&id=cartoon-network&pass=",
                "https://www.seirsanduk.online/?player=13&id=cartoon-network&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/cartoon-network-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/cartoon-network-us.png",
            "epg_id": "Cartoon.Network.bg",
            "epg_source": "BG1",
        },
        "E Kids": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=e-kids&pass=",
                "https://www.seirsanduk.online/?player=12&id=e-kids&pass=",
                "https://www.seirsanduk.online/?player=13&id=e-kids&pass=",
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/ekids-bg.png",
            "epg_id": "EKids.bg",
            "epg_source": "IPTVEPG_BG",
        },
        "Cartoonito": {
            "url": [
                "https://www.gledaitv.fan/cartoonito-live-tv.html",
                "https://www.gledaitv.fan/cartoonito-alternative-live-tv.html",
            ],
            "url_hd": "https://www.gledaitv.fan/cartoonito-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/italy/cartoonito-it.png",
            "epg_id": "Cartoonito.it",
            "epg_source": "IT1",
        },
        "Disney Channel": {
            "url": ["https://www.gledaitv.fan/disney-channel-live-tv.html",
                    "https://www.gledaitv.fan/disney-channel-alternative-live-tv.html",
                    "https://www.seirsanduk.online/?player=11&id=disney-channel&pass=",
                    "https://www.seirsanduk.online/?player=12&id=disney-channel&pass=",
                    "https://www.seirsanduk.online/?player=13&id=disney-channel&pass=",
                    ],
            "url_hd": "https://www.gledaitv.fan/disney-channel-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/disney-channel-us.png",
            "epg_id": "Disney.Channel.bg",
            "epg_source": "BG1",
        },
        "Nick Jr.": {
            "url": [
                "https://www.gledaitv.fan/nick-jr-live-tv.html",
                "https://www.gledaitv.fan/nick-jr-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=nick-jr&pass=",
                "https://www.seirsanduk.online/?player=12&id=nick-jr&pass=",
                "https://www.seirsanduk.online/?player=13&id=nick-jr&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/nick-jr-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/nick-jr-us.png",
            "epg_id": "Nick.Jr..bg",
            "epg_source": "BG1",
        },
        "Nick Toons": {
            "url": [
                "https://www.gledaitv.fan/nick-toons-live-tv.html",
                "https://www.gledaitv.fan/nick-toons-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=nicktoons&pass=",
                "https://www.seirsanduk.online/?player=12&id=nicktoons&pass=",
                "https://www.seirsanduk.online/?player=13&id=nicktoons&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/nick-toons-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/nick-toons-us.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Nickelodeon": {
            "url": [
                "https://www.gledaitv.fan/nickelodeon-live-tv.html",
                "https://www.gledaitv.fan/nickelodeon-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=nickelodeon&pass=",
                "https://www.seirsanduk.online/?player=12&id=nickelodeon&pass=",
                "https://www.seirsanduk.online/?player=13&id=nickelodeon&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/nickelodeon-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/nickelodeon-us.png",
            "epg_id": "Nickelodeon.bg",
            "epg_source": "BG1",
        },
        "Trt Çocuk": {
            "url": ["https://www.gledaitv.fan/trt-cocuk-live-tv.html",
                    "https://www.gledaitv.fan/trt-cocuk-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/trt-cocuk-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/trt-cocuk-tr.png",
            "epg_id": "TRT.ÇOCUK.tr",
            "epg_source": "TR1",
        },
    },
    "Worldwide": {
        "24 Kitchen": {
            "url": [
                "https://www.gledaitv.fan/24-kitchen-live-tv.html",
                "https://www.gledaitv.fan/24-kitchen-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-24-kitchen-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-24-kitchen-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-24-kitchen-hd&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/24-kitchen-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/24-kitchen-bg.png",
            "epg_id": "24kitchen.bg",
            "epg_source": "BG1",
        },
        "AGRO": {
            "url": ["https://www.gledaitv.fan/agro-live-tv.html", "https://www.gledaitv.fan/agro-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/agro-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/agro-tv-bg.png",
            "epg_id": "Agro.TV.rs",
            "epg_source": "RS1",
        },
        "bTV Action": {
            "url": ["https://www.gledaitv.fan/btv-action-live-tv.html",
                    "https://www.gledaitv.fan/btv-action-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/btv-action-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/btv-action-bg.png",
            "epg_id": "bTV.Action.bg",
            "epg_source": "BG1",
        },
        "Bulgaria ON AIR": {
            "url": ["https://www.gledaitv.fan/bulgaria-on-air-live-tv.html",
                    "https://www.gledaitv.fan/bulgaria-on-air-alternative-live-tv.html",
                    "https://www.seirsanduk.online/?player=11&id=bulgaria-on-air&pass=",
                    "https://www.seirsanduk.online/?player=12&id=bulgaria-on-air&pass=",
                    "https://www.seirsanduk.online/?player=13&id=bulgaria-on-air&pass=",
                    ],
            "url_hd": "https://www.gledaitv.fan/bulgaria-on-air-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/bulgaria-on-air-bg.png",
            "epg_id": "България.он.еър.bg",
            "epg_source": "BG1",
        },
        "Byeaz Tv": {
            "url": ["https://www.gledaitv.fan/byeaz-tv-live-tv.html",
                    "https://www.gledaitv.fan/byeaz-tv-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/byeaz-tv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/beyaz-tv-tr.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Code Fashion": {
            "url": ["https://www.gledaitv.fan/code-fashion-live-tv.html",
                    "https://www.gledaitv.fan/code-fashion-alternative-live-tv.html",
                    "https://www.seirsanduk.online/?player=11&id=hd-code-fashion-tv-hd&pass=",
                    "https://www.seirsanduk.online/?player=12&id=hd-code-fashion-tv-hd&pass=",
                    "https://www.seirsanduk.online/?player=13&id=hd-code-fashion-tv-hd&pass=",
                    ],
            "url_hd": "https://www.gledaitv.fan/code-fashion-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/code-fashion-bg.png",
            "epg_id": "CodeFashionTV.bg",
            "epg_source": "IPTVEPG_BG",
        },
        "Code Health": {
            "url": ["https://www.gledaitv.fan/code-health-live-tv.html",
                    "https://www.gledaitv.fan/code-health-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/code-health-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/code-health-bg.png",
            "epg_id": "CodeHealthTV.bg",
            "epg_source": "IPTVEPG_BG",
        },
        "Kanal 0": {
            "url": ["https://www.gledaitv.fan/kanal-0-live-tv.html",
                    "https://www.gledaitv.fan/kanal-0-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/kanal-0-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/kabal/images/3/39/Site-community-image/revision/latest/thumbnail-down/width/500/height/320?cb=20240516211240",
            "epg_id": "",
            "epg_source": "",
        },
        "Kanal D": {
            "url": ["https://www.gledaitv.fan/kanal-d-live-tv.html",
                    "https://www.gledaitv.fan/kanal-d-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/kanal-d-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/kanal-d-tr.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Show Tv": {
            "url": ["https://www.gledaitv.fan/show-tv-live-tv.html",
                    "https://www.gledaitv.fan/show-tv-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/show-tv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/show-tr.png",
            "epg_id": "Show.TV.cz",
            "epg_source": "CZ1",
        },
        "TLC BG": {
            "url": ["https://www.gledaitv.fan/tlc-bg-live-tv.html",
                    "https://www.gledaitv.fan/tlc-bg-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/tlc-bg-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/serbia/tlc-rs.png",
            "epg_id": "TLC.Balkans.bg",
            "epg_source": "BG1",
        },
        "Travel Channel": {
            "url": [
                "https://www.gledaitv.fan/travel-channel-live-tv.html",
                "https://www.gledaitv.fan/travel-channel-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-travel-channel-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-travel-channel-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-travel-channel-hd&pass="
            ],
            "url_hd": "https://www.gledaitv.fan/travel-channel-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/international/travel-channel-int.png",
            "epg_id": "Travel.Channel.bg",
            "epg_source": "BG1",
        },
        "Travel TV": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=travel-tv&pass=",
                "https://www.seirsanduk.online/?player=12&id=travel-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=travel-tv&pass="
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/travel-tv-bg.png",
            "epg_id": "Travel TV.bg",
            "epg_source": "GLOBETV2",
        },
        "TVN": {
            "url": ["https://www.gledaitv.fan/tvn-live-tv.html", "https://www.gledaitv.fan/tvn-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/tvn-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/poland/tvn-pl.png",
            "epg_id": "TVN.cz",
            "epg_source": "CZ1",
        },
        "1 HD TV": {
            "url": ["https://www.gledaitv.fan/1-hd-tv-live-tv.html", "https://www.gledaitv.fan/1-hd-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/1-hd-tv-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/5/5e/1tvhd_2.png/revision/latest/scale-to-width-down/250?cb=20160627072930",
            "epg_id": "",
            "epg_source": "",
        },
        "ARD": {
            "url": ["https://www.gledaitv.fan/ard-live-tv.html", "https://www.gledaitv.fan/ard-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/ard-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/germany/ard-de.png",
            "epg_id": "ARD.nl",
            "epg_source": "NL1",
        },
        "ATV": {
            "url": ["https://www.gledaitv.fan/atv-live-tv.html", "https://www.gledaitv.fan/atv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/atv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/atv-tr.png",
            "epg_id": "ATV.es",
            "epg_source": "ES1",
        },
        "Bayerischer Rundfunk": {
            "url": ["https://www.gledaitv.fan/bayerischer-rundfunk-live-tv.html", "https://www.gledaitv.fan/bayerischer-rundfunk-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/bayerischer-rundfunk-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/germany/br-de.png",
            "epg_id": "",
            "epg_source": "",
        },
        "BEK SPORTS": {
            "url": ["https://www.gledaitv.fan/bek-sports-live-tv.html", "https://www.gledaitv.fan/bek-sports-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/bek-sports-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/bek-sports-us.png",
            "epg_id": "",
            "epg_source": "",
        },
        "BFM": {
            "url": ["https://www.gledaitv.fan/bfm-live-tv.html", "https://www.gledaitv.fan/bfm-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/bfm-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/france/bfm-tv-fr.png",
            "epg_id": "BFM.TV.fr",
            "epg_source": "FR1",
        },
        "C8 FR": {
            "url": ["https://www.gledaitv.fan/c8-fr-live-tv.html", "https://www.gledaitv.fan/c8-fr-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/c8-fr-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/france/c8-fr.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Carousel": {
            "url": ["https://www.gledaitv.fan/carousel-live-tv.html", "https://www.gledaitv.fan/carousel-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/carousel-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/c/c3/Carousel_%28food%29.png/revision/latest/scale-to-width-down/250?cb=20200701151859",
            "epg_id": "Carousel.cz",
            "epg_source": "CZ1",
        },
        "DEUTSCHE WELLE": {
            "url": ["https://www.gledaitv.fan/deutsche-welle-live-tv.html", "https://www.gledaitv.fan/deutsche-welle-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/deutsche-welle-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/germany/dw-de.png",
            "epg_id": "Deutsche.Welle.hr",
            "epg_source": "HR1",
        },
        "FITE": {
            "url": ["https://www.gledaitv.fan/fite-live-tv.html", "https://www.gledaitv.fan/fite-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/fite-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/international/fite-tv-int.png",
            "epg_id": "",
            "epg_source": "",
        },
        "France 24": {
            "url": ["https://www.gledaitv.fan/france-24-live-tv.html", "https://www.gledaitv.fan/france-24-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/france-24-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/france/france-24-fr.png",
            "epg_id": "France.24.fr",
            "epg_source": "FR1",
        },
        "History Channel RU": {
            "url": ["https://www.gledaitv.fan/history-channel-ru-live-tv.html", "https://www.gledaitv.fan/history-channel-ru-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/history-channel-ru-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/history-channel-us.png",
            "epg_id": "History.Channel.cz",
            "epg_source": "CZ1",
        },
        "Nick Jr. RU": {
            "url": ["https://www.gledaitv.fan/nick-jr-ru-live-tv.html", "https://www.gledaitv.fan/nick-jr-ru-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/nick-jr-ru-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/nick-jr-us.png",
            "epg_id": "Nick.Jr..bg",
            "epg_source": "BG1",
        },
        "Nickelodeon RU": {
            "url": ["https://www.gledaitv.fan/nickelodeon-ru-live-tv.html", "https://www.gledaitv.fan/nickelodeon-ru-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/nickelodeon-ru-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-states/nickelodeon-us.png",
            "epg_id": "Nickelodeon.it",
            "epg_source": "IT1",
        },
        "PRO 7": {
            "url": ["https://www.gledaitv.fan/pro-7-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/pro-7-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/germany/pro-sieben-de.png",
            "epg_id": "Pro.7.ro",
            "epg_source": "RO1",
        },
        "RTL": {
            "url": ["https://www.gledaitv.fan/rtl-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/rtl-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/germany/rtl-de.png",
            "epg_id": "RTL.ro",
            "epg_source": "RO1",
        },
        "RU TV": {
            "url": ["https://www.gledaitv.fan/ru-tv-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/ru-tv-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/5/5b/RU.TV_%282023%29.webp/revision/latest/scale-to-width-down/200?cb=20240620152821",
            "epg_id": "",
            "epg_source": "",
        },
        "Russia 1": {
            "url": ["https://www.gledaitv.fan/russia-1-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/russia-1-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/b6/Russia_1_2012.svg/revision/latest/scale-to-width-down/250?cb=20210123160619",
            "epg_id": "",
            "epg_source": "",
        },
        "Sila": {
            "url": ["https://www.gledaitv.fan/sila-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/sila-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/f/fc/Sila_%28Tricolor%29.svg/revision/latest/scale-to-width-down/200?cb=20250326094942",
            "epg_id": "",
            "epg_source": "",
        },
        "TRT 1": {
            "url": ["https://www.gledaitv.fan/trt-1-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/trt-1-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/trt-1-tr.png",
            "epg_id": "TRT.1.tr",
            "epg_source": "TR1",
        },
        "TV5 Monde": {
            "url": ["https://www.gledaitv.fan/tv5-monde-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/tv5-monde-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/france/tv5-monde-fr.png",
            "epg_id": "TV5.Monde.hr",
            "epg_source": "HR1",
        },
        "WDR": {
            "url": ["https://www.gledaitv.fan/wdr-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/wdr-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/germany/wdr-de.png",
            "epg_id": "WDR.nl",
            "epg_source": "NL1",
        },
        "ZDF": {
            "url": ["https://www.gledaitv.fan/zdf-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/zdf-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/germany/zdf-de.png",
            "epg_id": "ZDF.nl",
            "epg_source": "NL1",
        },
    },
    "Music": {
        "Balkanika Tv": {
            "url": ["https://www.gledaitv.fan/balkanika-tv-live-tv.html", "https://www.gledaitv.fan/balkanika-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/balkanika-tv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/balkanika-music-television-bg.png",
            "epg_id": "Балканика HD.bg",
            "epg_source": "GLOBETV2",
        },
        "Rodina Tv": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=rodina-tv&pass=",
                "https://www.seirsanduk.online/?player=12&id=rodina-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=rodina-tv&pass=",
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/tv-rodina-bg.png",
            "epg_id": "Rodina TV.bg",
            "epg_source": "GLOBETV2",
        },
        "DSTV": {
            "url": [
                "https://www.gledaitv.fan/dstv-live-tv.html",
                "https://www.gledaitv.fan/dstv-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=dstv&pass=",
                "https://www.seirsanduk.online/?player=12&id=dstv&pass=",
                "https://www.seirsanduk.online/?player=13&id=dstv&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/dstv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/dstv-bg.png",
            "epg_id": "DSTV.bg",
            "epg_source": "GLOBETV2",
        },
        "City Tv": {
            "url": [
                "https://www.gledaitv.fan/city-tv-live-tv.html",
                "https://www.gledaitv.fan/city-tv-alternative-live-tv.html",
                "https://freetv.studio/channel/CityTV.bg",
                "https://www.seirsanduk.online/?player=11&id=city-tv&pass=",
                "https://www.seirsanduk.online/?player=12&id=city-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=city-tv&pass=",
            ],
            "url_hd": "https://www.gledaitv.fan/city-tv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/city-tv-bg.png",
            "epg_id": "TV.City.rs",
            "epg_source": "RS1",
        },
        "Fen TV": {
            "url": ["https://www.gledaitv.fan/fen-tv-live-tv.html", "https://www.gledaitv.fan/fen-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/fen-tv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/fen-folk-tv-bg.png",
            "epg_id": "ФЕН ТВ HD.bg",
            "epg_source": "GLOBETV2",
        },
        "Kral Pop Tv": {
            "url": ["https://www.gledaitv.fan/kral-pop-tv-live-tv.html", "https://www.gledaitv.fan/kral-pop-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/kral-pop-tv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/kral-pop-tr.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Planeta Folk": {
            "url": [
                "https://www.gledaitv.fan/planeta-folk-live-tv.html",
                "https://www.gledaitv.fan/planeta-folk-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=planeta-folk&pass=",
                "https://www.seirsanduk.online/?player=12&id=planeta-folk&pass=",
                "https://www.seirsanduk.online/?player=13&id=planeta-folk&pass="
            ],
            "url_hd": "https://www.gledaitv.fan/planeta-folk-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/planeta-folk-bg.png",
            "epg_id": "Планета Фолк HD.bg",
            "epg_source": "GLOBETV2",
        },
        "Folklor TV": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=folklor-tv&pass=",
                "https://www.seirsanduk.online/?player=12&id=folklor-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=folklor-tv&pass=",
            ],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/folklor-tv-bg.png",
            "epg_id": "Folklor.bg",
            "epg_source": "GLOBETV2",
        },
        "Planeta HD BG": {
            "url": [
                "https://www.gledaitv.fan/planeta-hd-bg-live-tv.html",
                "https://www.gledaitv.fan/planeta-hd-bg-alternative-live-tv.html",
                "https://www.seirsanduk.online/?player=11&id=hd-planeta-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-planeta-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-planeta-hd&pass="
            ],
            "url_hd": "https://www.gledaitv.fan/planeta-hd-bg-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/planeta-bg.png",
            "epg_id": "Планета HD.bg",
            "epg_source": "GLOBETV2",
        },
        "Power Türk": {
            "url": ["https://www.gledaitv.fan/power-turk-live-tv.html", "https://www.gledaitv.fan/power-turk-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/power-turk-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/powerturk-tr.png",
            "epg_id": "Power.Turk.al",
            "epg_source": "AL1",
        },
        "Tatlıses Tv": {
            "url": ["https://www.gledaitv.fan/tatlises-tv-live-tv.html", "https://www.gledaitv.fan/tatlises-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/tatlises-tv-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/tatlises-tv-tr.png",
            "epg_id": "",
            "epg_source": "",
        },
        "The Voice": {
            "url": [
                "https://www.gledaitv.fan/the-voice-live-tv.html",
                "https://www.gledaitv.fan/the-voice-alternative-live-tv.html",
                "https://freetv.studio/channel/TheVoice.bg",
                "https://www.seirsanduk.online/?player=11&id=the-voice&pass=",
                "https://www.seirsanduk.online/?player=12&id=the-voice&pass=",
                "https://www.seirsanduk.online/?player=13&id=the-voice&pass="
            ],
            "url_hd": "https://www.gledaitv.fan/the-voice-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/the-voice-bg.png",
            "epg_id": "The.Voice.bg",
            "epg_source": "BG1",
        },
        "Trt Müzik": {
            "url": ["https://www.gledaitv.fan/trt-muzik-live-tv.html", "https://www.gledaitv.fan/trt-muzik-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/trt-muzik-hd-live-tv.html",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/turkey/trt-muzik-tr.png",
            "epg_id": "TRT.MÜZİK.tr",
            "epg_source": "TR1",
        },
        "Tiankov TV": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=tiankov-tv&pass=",
                "https://www.seirsanduk.online/?player=12&id=tiankov-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=tiankov-tv&pass=",
            ],
            "url_hd": "",
            "image": "https://www.predavatel.com/bg/3/asenovgrad_img/tv-tiankov-folk.png",
            "epg_id": "Тянков Фолк.bg",
            "epg_source": "GLOBETV2",
        },
        "V2Beat TV": {
            "url": ["https://www.parsatv.com/name=V2Beat-TV#music"],
            "url_hd": "",
            "image": "https://www.vibee.tv/wp-content/uploads/2025/06/viib-v2beat-logo-neon-1280-x-720.jpg",
            "epg_id": "",
            "epg_source": "",
        },
        "Magic TV": {
            "url": ["https://www.parsatv.com/name=Magic-TV#music"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/bulgaria/magic-tv-bg.png",
            "epg_id": "Magic.TV.ro",
            "epg_source": "RO1",
        },
        "Retro Music": {
            "url": ["https://www.parsatv.com/name=Retro-Music#music"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/b9/Retro_Music_Television_2013.svg/revision/latest/scale-to-width-down/250?cb=20210627161000",
            "epg_id": "RETRO.Music.TV.sk",
            "epg_source": "SK1",
        },
        "Rock TV": {
            "url": ["https://www.rockfm.ro/rocktv"],
            "url_hd": "https://freetv.studio/channel/RockTV.ro",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/romania/rock-tv-ro.png",
            "epg_id": "Rock.TV.ro",
            "epg_source": "RO1",
        },
        "Rock Zone": {
            "url": ["https://rockzone.life/#live-broadcast"],
            "url_hd": "",
            "image": "https://rockzone.life/wp-content/uploads/2025/04/logo.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Pulse Rock": {
            "url": ["https://www.pulserocktv.com/tvversion.htm"],
            "url_hd": "",
            "image": "https://www.pulserocktv.com/logos/pulsesmall.jpg",
            "epg_id": "",
            "epg_source": "",
        },
        "Deejay TV": {
            "url": ["https://www.parsatv.com/name=Deejay-TV#music"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/italy/deejay-tv-it.png",
            "epg_id": "Deejay.TV.it",
            "epg_source": "IT1",
        },
        "NRG 91": {
            "url": ["https://www.parsatv.com/name=NRG-91-Music"],
            "url_hd": "",
            "image": "https://nrg91.gr/wp-content/uploads/2017/07/originalNRG.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Baraza TV": {
            "url": ["https://www.parsatv.com/name=Baraza-TV#music"],
            "url_hd": "https://freetv.studio/channel/BarazaTV.gr",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfuMSWQhsui8E03WEq9BPJkKXqE6aM2H2LGg&s",
            "epg_id": "",
            "epg_source": "",
        },
        "RadioU TV": {
            "url": ["https://www.parsatv.com/name=RadioU-TV#music"],
            "url_hd": "",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmp5eCElIFY5taK8C8KECn3Ulccgb0K1h44w&s",
            "epg_id": "",
            "epg_source": "",
        },
        "Radio Capital TV": {
            "url": ["https://www.parsatv.com/name=Radio-Capital-TV#music"],
            "url_hd": "",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRaO8FqtQU8sCq2rpalZGuShoxXBgszUVmqOw&s",
            "epg_id": "",
            "epg_source": "",
        },
        "Activa TV": {
            "url": ["https://www.parsatv.com/name=Activa-TV#music"],
            "url_hd": "",
            "image": "https://www.conectabalear.com/tv/logos/original/149.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Baraza TV Deep House": {
            "url": ["https://freetv.studio/channel/BarazaTVDeepHouse.gr"],
            "url_hd": "",
            "image": "https://i.imgur.com/TZ1unwF.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Baraza TV Relaxing": {
            "url": ["https://freetv.studio/channel/BarazaTVRelaxing.gr"],
            "url_hd": "",
            "image": "https://i.imgur.com/TZ1unwF.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Ellinikos FM": {
            "url": ["https://freetv.studio/channel/EllinikosFM.gr"],
            "url_hd": "",
            "image": "https://i.ibb.co/y0ydCNB/unnamed-4.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Messatida TV": {
            "url": ["https://freetv.studio/channel/MessatidaTV.gr"],
            "url_hd": "",
            "image": "https://i.imgur.com/WEYrIrC.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Panik TV": {
            "url": ["https://freetv.studio/channel/PanikTV.gr"],
            "url_hd": "",
            "image": "https://i.imgur.com/13C3CPr.png",
            "epg_id": "Panik.TV.gr",
            "epg_source": "GR1",
        },
        "Lamore Rock Show WebTV": {
            "url": ["https://freetv.studio/channel/LamoreRockShowWebTV.br"],
            "url_hd": "",
            "image": "https://www.lamorerockshowwebtv.com.br/wp-content/uploads/2024/11/logo_rockshow.avif",
            "epg_id": "",
            "epg_source": "",
        },
        "Stingray Rock Alternative": {
            "url": ["https://freetv.studio/channel/StingrayRockAlternative.ca"],
            "url_hd": "",
            "image": "https://i.imgur.com/mt8ulVX.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Vantage Rock": {
            "url": ["https://freetv.studio/channel/VantageRock.ee"],
            "url_hd": "",
            "image": "https://vantagetv.eu/vantage_rock.png",
            "epg_id": "Vantage.Rock.cz",
            "epg_source": "CZ1",
        },
        "XITE Rock x Metal": {
            "url": ["https://freetv.studio/channel/XITERockxMetal.nl"],
            "url_hd": "",
            "image": "https://i.imgur.com/szDM09P.png",
            "epg_id": "",
            "epg_source": "",
        },
        "NOW Rock": {
            "url": ["https://freetv.studio/channel/NOWRock.uk"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-kingdom/now-rock-uk.png",
            "epg_id": "Now.Rock.uk",
            "epg_source": "UK1",
        },
        "XITE 90's Throwback": {
            "url": ["https://freetv.studio/channel/XITE90sThrowback.us"],
            "url_hd": "",
            "image": "https://i.imgur.com/vwpOzuz.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Metaleitor TV": {
            "url": ["https://freetv.studio/channel/MetaleitorTV.us"],
            "url_hd": "",
            "image": "https://new.opencaster.com/uploads/logos/logo_14_1752798826.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Now 90s00s": {
            "url": ["https://freetv.studio/channel/Now90s00s.uk"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-kingdom/now-90s-uk.png",
            "epg_id": "NOW.90s00s.uk",
            "epg_source": "UK1",
        },
        "70-80 TV": {
            "url": ["https://freetv.studio/channel/7080TV.it"],
            "url_hd": "",
            "image": "https://i.imgur.com/y4kNV3Q.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Now 80s": {
            "url": ["https://freetv.studio/channel/Now80s.uk"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-kingdom/now-80s-uk.png",
            "epg_id": "NOW.80s.uk",
            "epg_source": "UK1",
        },
        "Totalmusic 80s": {
            "url": ["https://freetv.studio/channel/Totalmusic80s.uk"],
            "url_hd": "",
            "image": "https://static.elektamedia.com/ch/tmc_80s.png",
            "epg_id": "",
            "epg_source": "",
        },
        "Now 70s": {
            "url": ["https://freetv.studio/channel/Now70s.uk"],
            "url_hd": "",
            "image": "https://github.com/tv-logo/tv-logos/raw/main/countries/united-kingdom/now-70s-uk.png",
            "epg_id": "NOW.70s.uk",
            "epg_source": "UK1",
        },
    },
}


def remove_proxy_from_link(url: list) -> list:
    clean_url = url[0]
    if "/?url=" in clean_url:
        clean_url = clean_url.split("/?url=")[-1]

    return clean_url


def sort_channels_and_lowercase_keys(channels_dict):
    sorted_channels = {}
    for main_key, inner_dict in sorted(channels_dict.items()):
        sorted_inner_items = sorted(
            inner_dict.items(), key=lambda item: item[0].upper()
        )
        lower_cased_inner_dict = {}

        for channel_name, details in sorted_inner_items:
            lower_cased_inner_dict[channel_name.upper()] = details

        sorted_channels[main_key] = lower_cased_inner_dict

    return sorted_channels


ALL_CHANNELS = sort_channels_and_lowercase_keys(ALL_CHANNELS_NOT_SORTED)


def extract_m3u8_from_text(html_content):
    """Try to extract m3u8 URL from HTML content"""
    pattern = re.compile(r'"(?P<video_url>https?://[^"]*m3u8[^"]*)"')
    matches = pattern.findall(html_content)
    return matches[0]


def extract_video_url_default(url):
    """Extract video URL by first checking HTML in responses, then network requests"""
    captured_urls = []

    def handle_response(response):
        if captured_urls:
            return

        try:
            content = response.text()
            if ".m3u8" in content:
                m3u8 = extract_m3u8_from_text(content)
                captured_urls.append(m3u8)
                # page.close()
                return
        except:
            pass

        try:
            # Only check response URL if not found in HTML
            if response.status == 200 and any(
                m3u8 in response.url for m3u8 in ("index.m3u8", ".m3u8")
            ):
                print(f"Found m3u8 URL in network: {response.url}")
                captured_urls.append(response.url)
                # page.close()
                return

        except Exception as e:
            print(f"Error processing response: {e}")

    with sync_playwright() as p:
        # chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        chrome_path = r"/usr/bin/google-chrome"

        browser = p.chromium.launch(headless=True, executable_path=chrome_path)
        page = browser.new_page()

        page.on("response", handle_response)

        try:
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector(
                'p:has-text("Не давам съгласие")', timeout=1000)
            page.click('p:has-text("Не давам съгласие")')

            page.wait_for_selector('a:has-text("Player 1")', timeout=1000)
            page.click('a:has-text("Player 1")')

            if not captured_urls:
                page.wait_for_timeout(5000)

        except Exception as e:
            print(f"Error during extraction: {e}")
        finally:
            browser.close()

    return captured_urls


async def extract_video_url_gledai_tv(url):
    """Extract video URL and return immediately when found using nodriver"""
    captured_urls = []

    # Start nodriver
    # expert=True allows some debugging features and patches
    browser = await uc.start()

    # We'll use a tab
    page = await browser.get('about:blank')

    async def response_handler(event: uc.cdp.network.ResponseReceived):
        # If we already found one, stop processing
        if captured_urls:
            return

        response_url = event.response.url

        try:
            # 1. Check if the response URL itself is the m3u8
            if event.response.status == 200 and any(ext in response_url for ext in ("index.m3u8", ".m3u8")):
                if "token=" in response_url:
                    print(f"DEBUG: Found M3U8 in URL: {response_url}")
                    captured_urls.append(response_url)
                    return

            # 2. Check if the response body contains the link (deep search)
            # nodriver allows getting body via CDP
            mime = event.response.mime_type
            if "javascript" in mime or "html" in mime or "json" in mime:
                # We need to wait a bit or use get_response_body
                try:
                    body_data = await browser.connection.send(
                        uc.cdp.network.get_response_body(event.request_id)
                    )
                    content = body_data[0]  # The actual body text

                    if ".m3u8" in content:
                        m3u8 = await extract_m3u8_from_text(content)
                        if m3u8:
                            print(
                                f"DEBUG: Found M3U8 in response body: {m3u8}")
                            captured_urls.append(m3u8)
                            return
                except:
                    pass
        except Exception as e:
            pass

    # Add handler to page's connection
    # Note: in nodriver, handlers are often added to the browser connection or explicitly
    page.add_handler(uc.cdp.network.ResponseReceived, response_handler)

    try:
        # --- START NAV ---
        print(f"Navigating to {url}...")
        await page.get(url)

        # Give some time for Cloudflare Turnstile automated/manual solve
        print("Waiting for possible Cloudflare challenge / Loading...")

        # --- POLLING LOOP (Wait for Network) ---
        print("Polling for M3U8 URL...")
        for _ in range(50):  # Max 10 seconds (50 * 200ms)
            if captured_urls:
                print(f"URL found! Returning immediately.")
                break

            # --- TRY CLICK ON "I AM HUMAN" if visible ---
            # Nodriver often bypasses automatically, but sometimes needs a push

            # --- CLICK CONSENT ---
            try:
                consent_btn = await page.find('Не давам съгласие', best_match=True)
                if consent_btn:
                    await consent_btn.click()
            except:
                pass

            # --- CLICK PLAYER 1 ---
            try:
                player_btn = await page.find('Player 1', best_match=True)
                if player_btn:
                    await player_btn.click()
            except:
                pass

            await asyncio.sleep(0.2)

    except Exception as e:
        print(f"Error during extraction: {e}")
    finally:
        try:
            await browser.stop()
        except:
            pass
    return captured_urls
