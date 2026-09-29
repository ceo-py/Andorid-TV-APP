from playwright.sync_api import sync_playwright
import nodriver as uc
import asyncio
import re


ALL_CHANNELS_NOT_SORTED = {
    "Sport": {
        "MATCH! Futbol 3": {
            "url": ["https://www.gledaitv.fan/match-futbol-3-live-tv.html", "https://www.gledaitv.fan/match-futbol-3-alternative-live-tv.html", "https://www.gledaitv.fan/match-futbol-3-hd-live-tv.html"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/bf/NTV-Plus_Futbol_3_%282014%2C_prototype%29.svg/revision/latest/scale-to-width-down/250?cb=20201017144338",
            "epg_id": "",
            "epg_source": "",
        },
        "MATCH! Futbol 2": {
            "url": ["https://www.gledaitv.fan/match-futbol-2-alternative-live-tv.html", "https://www.gledaitv.fan/match-futbol-2-live-tv.html", "https://www.gledaitv.fan/match-futbol-2-hd-live-tv.html"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/1/15/NTV-Plus_Futbol_2_%282014%2C_prototype%29.svg/revision/latest/scale-to-width-down/250?cb=20201017143828",
            "epg_id": "",
            "epg_source": "",
        },
        "MATCH! Futbol 1": {
            "url": ["https://www.gledaitv.fan/match-futbol-1-live-tv.html"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/9/98/NTV-Plus_Futbol_1_%282014%2C_prototype%29.svg/revision/latest/scale-to-width-down/250?cb=20201017143436",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/4/45/Diema_Sport_HD.svg/revision/latest/scale-to-width-down/300?cb=20250505001930",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/3/36/Diema_Sport_2_HD.svg/revision/latest/scale-to-width-down/300?cb=20250505001624",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/1/17/Diema_Sport_3_HD.svg/revision/latest/scale-to-width-down/300?cb=20250505000657",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/e/e7/Eurosport_1_2022.svg/revision/latest/scale-to-width-down/300?cb=20220806090310",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/1/16/Eurosport_2_2022.svg/revision/latest/scale-to-width-down/300?cb=20220417183127",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/5/5e/Max_Sport_1_HD.svg/revision/latest/scale-to-width-down/300?cb=20250505002452",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/a/ac/Max_Sport_2_HD.svg/revision/latest/scale-to-width-down/300?cb=20250505002701",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/6/61/Max_Sport_3_HD.svg/revision/latest/scale-to-width-down/300?cb=20250505002837",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/6/62/Max_Sport_4_HD.svg/revision/latest/scale-to-width-down/300?cb=20250505003011",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/9/9e/Nova_Sport_2010_flat.svg/revision/latest/scale-to-width-down/150?cb=20240731175840",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/0/03/Ring.svg/revision/latest/scale-to-width-down/200?cb=20210516104914",
            "epg_id": "RING.BG.bg",
            "epg_source": "BG1",
        },
        "TJK Tv": {
            "url": ["https://www.gledaitv.fan/tjk-tv-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/tjk-tv-hd-live-tv.html",
            "image": "https://about.me/cdn-cgi/image/q=80,dpr=1,f=auto,fit=cover,w=1024,h=512,gravity=auto/https://assets.about.me/background/users/t/j/k/tjktvizle_1595702475_756.jpg",
            "epg_id": "",
            "epg_source": "",
        },
        "Trt Spor": {
            "url": ["gledaitv.fan/trt-spor-alternative-live-tv.html", "https://www.gledaitv.fan/trt-spor-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/trt-spor-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/9/92/TRT_Spor_logo_%282022%29.svg/revision/latest/scale-to-width-down/300?cb=20220107231944",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/3/3c/Red_Bull_TV.svg/revision/latest/scale-to-width-down/250?cb=20180423100712",
            "epg_id": "",
            "epg_source": "",
        },
        "Fuel TV": {
            "url": ["https://www.parsatv.com/name=Fuel-TV#sport"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/6/6a/Fuel_TV.svg/revision/latest/scale-to-width-down/150?cb=20100323111006",
            "epg_id": "",
            "epg_source": "",
        },
        "SportItalia": {
            "url": ["https://www.parsatv.com/name=Sportitalia#sport"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/4/4a/Logo_si.JPG/revision/latest/scale-to-width-down/200?cb=20161118191326",
            "epg_id": "",
            "epg_source": "",
        },
        "Super Tennis": {
            "url": ["https://www.parsatv.com/name=Super-Tennis#sport"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/4/4e/Super_Tennis_2016.svg/revision/latest/scale-to-width-down/250?cb=20201227003011",
            "epg_id": "",
            "epg_source": "",
        },
        "beIN Sports Xtra": {
            "url": ["https://www.parsatv.com/name=beIN-Sports-Xtra#sport"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/0/0b/BeIN_Xtra.PNG/revision/latest/scale-to-width-down/300?cb=20201108180437",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/3/3a/05_NHL_Shield.svg/revision/latest/scale-to-width-down/200?cb=20191208162044",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d2/NBA_TV.svg/960px-NBA_TV.svg.png",
            "epg_id": "",
            "epg_source": "",
        },
    },
    "Movie": {
        "AMC": {
            "url": ["https://www.gledaitv.fan/amc-live-tv.html", "https://www.gledaitv.fan/amc-alternative-live-tv.html", "https://www.gledaitv.live/watch-tv/66/amc-online"],
            "url_hd": "https://www.gledaitv.fan/amc-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/a/ad/AMC_Networks_S21.svg/revision/latest/scale-to-width-down/200?cb=20220820072921",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/d/dc/2016_AXN_logo.svg/revision/latest/scale-to-width-down/300?cb=20201126064846",
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
            "image": "https://www.predavatel.com/bg/tv/cable-sat_img/axn-black2.png",
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
            "image": "https://www.predavatel.com/bg/tv/cable-sat_img/axn-white2.png",
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
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRS6YU0bglnotgXBthpeCCGK6bGRLRA09gwYg&s",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/f/f5/BTV_Cinema_%282016%29.svg/revision/latest/scale-to-width-down/300?cb=20200125184619",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/9/9f/BTV_Comedy_HD.jpg/revision/latest?cb=20240319192449",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/5/51/BTV_Lady_%282016%29.svg/revision/latest/scale-to-width-down/250?cb=20200125184015",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/b2/Diema.png/revision/latest/scale-to-width-down/150?cb=20170315162656",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/7/71/Diema_Family_2019.svg/revision/latest/scale-to-width-down/150?cb=20240731170629",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/1/1e/Epic_Drama_2018.svg/revision/latest/scale-to-width-down/200?cb=20191113170018",
            "epg_id": "Epic.Drama.bg",
            "epg_source": "BG1",
        },
        "FilmBox Extra": {
            "url": ["https://www.gledaitv.fan/filmbox-extra-live-tv.html", "https://www.gledaitv.fan/filmbox-extra-alternative-live-tv.html", "https://www.gledaitv.live/watch-tv/49/film-box-extra-online"],
            "url_hd": "https://www.gledaitv.fan/filmbox-extra-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/2/2c/FilmBox_Extra_HD.svg/revision/latest/scale-to-width-down/250?cb=20171210164807",
            "epg_id": "FilmBox.Extra.HD.bg",
            "epg_source": "BG1",
        },
        "FilmBox Stars": {
            "url": ["https://www.gledaitv.fan/filmbox-stars-live-tv.html", "https://www.gledaitv.fan/filmbox-stars-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/filmbox-stars-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/6/6e/FilmBox_Stars.svg/revision/latest/scale-to-width-down/250?cb=20200901135021",
            "epg_id": "FilmBox.Stars.bg",
            "epg_source": "BG1",
        },
        "FilmBox Plus": {
            "url": [],
            "url_hd": "https://www.gledaitv.live/watch-tv/48/film-box-plus-online",
            "image": "",
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
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/a/a6/Kinonova_re.svg/revision/latest/scale-to-width-down/250?cb=20260101161359",
            "epg_id": "KinoNova.bg",
            "epg_source": "BG1",
        },
        "Movie Star": {
            "url": ["https://www.gledaitv.fan/movie-star-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/movie-star-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/3/30/Movie_Starz_Video_Logo_%28Fixed%29.svg/revision/latest/scale-to-width-down/300?cb=20230605025253",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/c/cd/Star_Channel_2023.svg/revision/latest/scale-to-width-down/250?cb=20231209070650",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/4/40/Star_Crime_2023.svg/revision/latest/scale-to-width-down/250?cb=20231208002839",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/b9/Star_Life_2023.svg/revision/latest/scale-to-width-down/250?cb=20231209041522",
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
            "image": "",
            "epg_id": "Food.Network.HD.bg",
            "epg_source": "BG1",
        },
        "Animal Planet": {
            "url": ["https://www.gledaitv.fan/animal-planet-live-tv.html", "https://www.gledaitv.fan/animal-planet-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/animal-planet-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/e/e3/Animal_Planet_2018.svg/revision/latest/scale-to-width-down/250?cb=20210825085349",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/a/a8/Discovery_Channel_2019.svg/revision/latest/scale-to-width-down/300?cb=20210519155203",
            "epg_id": "Discovery.Channel.bg",
            "epg_source": "BG1",
        },
        "DMAX": {
            "url": ["https://www.gledaitv.fan/dmax-live-tv.html", "https://www.gledaitv.fan/dmax-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/dmax-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/c/c0/DMAX_%282026%29.svg/revision/latest/scale-to-width-down/250?cb=20260113020915",
            "epg_id": "",
            "epg_source": "",
        },
        "DocuBox": {
            "url": ["https://www.gledaitv.fan/docubox-live-tv.html", "https://www.gledaitv.fan/docubox-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/docubox-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/0/02/DocuBox_%282013%29.svg/revision/latest/scale-to-width-down/250?cb=20171210215646",
            "epg_id": "",
            "epg_source": "",
        },
        "History Channel": {
            "url": [""
                    "https://www.gledaitv.fan/test-h-live-tv.html", "https://www.gledaitv.fan/test-h-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/test-h-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/e/e8/History_2021.png/revision/latest/scale-to-width-down/200?cb=20240302050750",
            "epg_id": "History.bg",
            "epg_source": "BG1",
        },
        "Investigation Discovery": {
            "url": [
                "https://www.gledaitv.fan/investigation-discovery-live-tv.html",
                "https://www.gledaitv.fan/investigation-discovery-alternative-live-tv.html",
            ],
            "url_hd": "https://www.gledaitv.fan/investigation-discovery-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/0/0b/ID-2020.svg/revision/latest/scale-to-width-down/250?cb=20200413032314",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/d/d9/National_Geographic_Wild_2018.svg/revision/latest/scale-to-width-down/200?cb=20180903172554",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/c/c6/National_Geographic_2008.svg/revision/latest/scale-to-width-down/250?cb=20170701154034",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/b1/TLC_%282021%29.svg/revision/latest/scale-to-width-down/250?cb=20220703193228",
            "epg_id": "TLC.Balkans.bg",
            "epg_source": "BG1",
        },
        "TRT Belgesel": {
            "url": ["https://www.gledaitv.fan/trt-belgesel-live-tv.html", "https://www.gledaitv.fan/trt-belgesel-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/trt-belgesel-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/5/5e/TRT_Belgesel_%282019%29.svg/revision/latest/scale-to-width-down/300?cb=20210205141825",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/e/ec/Viasat_Explore_2022.svg/revision/latest/scale-to-width-down/150?cb=20220119212514",
            "epg_id": "Viasat.Explorer.bg",
            "epg_source": "BG1",
        },
        "Viasat History": {
            "url": ["https://www.gledaitv.fan/viasat-history-live-tv.html", "https://www.gledaitv.fan/viasat-history-alternative-live-tv.html"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/b7/Viasat_History_2022.svg/revision/latest/scale-to-width-down/150?cb=20220119212113",
            "epg_id": "Viasat.History.bg",
            "epg_source": "BG1",
        },
        "Viasat Nature": {
            "url": ["https://www.gledaitv.fan/viasat-nature-live-tv.html", "https://www.gledaitv.fan/viasat-nature-alternative-live-tv.html"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/b5/Viasat_Nature_2022.svg/revision/latest/scale-to-width-down/150?cb=20220119211909",
            "epg_id": "Viasat.Nature.bg",
            "epg_source": "BG1",
        },
        "Yaban Tv": {
            "url": ["https://www.gledaitv.fan/yaban-tv-live-tv.html", "https://www.gledaitv.fan/yaban-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/yaban-tv-hd-live-tv.html",
            "image": "https://yt3.googleusercontent.com/ytc/AIdro_ml4Ec8YVG61pHTn1Q1zwpbDv_6RmPPPtFe2e4ysRhBAoo=s900-c-k-c0x00ffffff-no-rj",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/5/5f/Bgonair-new2.png/revision/latest/scale-to-width-down/210?cb=20160102175130",
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
            "image": "https://www.predavatel.com/bg/tv/nova_images/nova-news.svg",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/6/6f/BNT_1_2018.svg/revision/latest/scale-to-width-down/300?cb=20180909194302",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/1/1f/BNT_2_2018.svg/revision/latest/scale-to-width-down/300?cb=20180909194412",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/3/32/BNT_3_2018.svg/revision/latest/scale-to-width-down/300?cb=20180909194740",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/e/e9/BNT_4_2018.svg/revision/latest/scale-to-width-down/300?cb=20180909194558",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/e/e6/BTV_Bulgaria_2025.svg/revision/latest/scale-to-width-down/250?cb=20250701093143",
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
            "image": "https://www.predavatel.com/bg/tv/bgonair_img/bloomberg.svg",
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
            "epg_id": "",
            "epg_source": "",
        },
        "SKAT": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=skat&pass=",
                "https://www.seirsanduk.online/?player=12&id=skat-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=skat-tv&pass=",
            ],
            "url_hd": "",
            "image": "https://www.predavatel.com/bg/5/burgas-radiotv_img/tv-skat2.png",
            "epg_id": "СКАТ.bg",
            "epg_source": "BG1",
        },
        "7/8 TV": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=hd-78-tv-hd&pass=",
                "https://www.seirsanduk.online/?player=12&id=hd-78-tv-hd&pass=",
                "https://www.seirsanduk.online/?player=13&id=hd-78-tv-hd&pass=",
            ],
            "url_hd": "",
            "image": "https://www.predavatel.com/bg/tv/images/78.png",
            "epg_id": "ТВ.78.bg",
            "epg_source": "BG1",
        },
        "Evrokom": {
            "url": [
                "https://eurocom.bg/live",
                "https://www.seirsanduk.online/?player=11&id=evrokom&pass=",
                "https://www.seirsanduk.online/?player=12&id=evrokom&pass=",
                "https://www.seirsanduk.online/?player=13&id=evrokom&pass=",
            ],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/a/a5/Eurokom_1996.png/revision/latest/scale-to-width-down/300?cb=20170802171200",
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
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTOGhFKRgJ9roOiXry-ysDZreZQzVYuyjXwGw&s",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/e/ee/Cartoon_Network_2010.svg/revision/latest/scale-to-width-down/250?cb=20210726224754",
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
            "image": "https://www.predavatel.com/bg/tv/cable-sat_img/ekids.svg",
            "epg_id": "EKids.bg",
            "epg_source": "BG1",
        },
        "Cartoonito": {
            "url": [
                "https://www.gledaitv.fan/cartoonito-live-tv.html",
                "https://www.gledaitv.fan/cartoonito-alternative-live-tv.html",
            ],
            "url_hd": "https://www.gledaitv.fan/cartoonito-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/e/ee/Cartoon_Network_2010.svg/revision/latest/scale-to-width-down/250?cb=20210726224754",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/f/f0/DISNEYCHANNEL-2025.svg/revision/latest/scale-to-width-down/300?cb=20251113064305",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/5/55/Nick_Jr..svg/revision/latest/scale-to-width-down/250?cb=20251017154510",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/6/69/Nicktoons_2023_Logo.svg/revision/latest/scale-to-width-down/300?cb=20240724194938",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/0/07/Nickelodeon_%282009%29.svg/revision/latest/scale-to-width-down/350?cb=20180306141612",
            "epg_id": "Nickelodeon.bg",
            "epg_source": "BG1",
        },
        "Trt Çocuk": {
            "url": ["https://www.gledaitv.fan/trt-cocuk-live-tv.html",
                    "https://www.gledaitv.fan/trt-cocuk-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/trt-cocuk-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/1/1a/TRT_%C3%87ocuk_logo_%282021%29.svg/revision/latest/scale-to-width-down/300?cb=20211101143853",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/2/29/24_kitchen_2022_Portugal.svg/revision/latest/scale-to-width-down/300?cb=20230117133430",
            "epg_id": "24kitchen.bg",
            "epg_source": "BG1",
        },
        "AGRO": {
            "url": ["https://www.gledaitv.fan/agro-live-tv.html", "https://www.gledaitv.fan/agro-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/agro-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/b0/Agro-RedeGlobo.JPG/revision/latest/scale-to-width-down/400?cb=20160723011224",
            "epg_id": "",
            "epg_source": "",
        },
        "bTV Action": {
            "url": ["https://www.gledaitv.fan/btv-action-live-tv.html",
                    "https://www.gledaitv.fan/btv-action-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/btv-action-hd-live-tv.html",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRS6YU0bglnotgXBthpeCCGK6bGRLRA09gwYg&s",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/5/5f/Bgonair-new2.png/revision/latest/scale-to-width-down/210?cb=20160102175130",
            "epg_id": "България.он.еър.bg",
            "epg_source": "BG1",
        },
        "Byeaz Tv": {
            "url": ["https://www.gledaitv.fan/byeaz-tv-live-tv.html",
                    "https://www.gledaitv.fan/byeaz-tv-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/byeaz-tv-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/9/96/Beyaz_tv_2012-2022.png/revision/latest/scale-to-width-down/250?cb=20250720181730",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/6/60/Fashion.png/revision/latest/scale-to-width-down/200?cb=20241104092044",
            "epg_id": "",
            "epg_source": "",
        },
        "Code Health": {
            "url": ["https://www.gledaitv.fan/code-health-live-tv.html",
                    "https://www.gledaitv.fan/code-health-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/code-health-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/0/00/Health_2025.png/revision/latest/scale-to-width-down/200?cb=20250117165029",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/8/86/Kanal_D_Logo_%282011-present%29_-HD-.png/revision/latest/scale-to-width-down/200?cb=20171227122658",
            "epg_id": "",
            "epg_source": "",
        },
        "Show Tv": {
            "url": ["https://www.gledaitv.fan/show-tv-live-tv.html",
                    "https://www.gledaitv.fan/show-tv-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/show-tv-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/4/4b/Show_TV.svg/revision/latest/scale-to-width-down/250?cb=20161114192209",
            "epg_id": "",
            "epg_source": "",
        },
        "TLC BG": {
            "url": ["https://www.gledaitv.fan/tlc-bg-live-tv.html",
                    "https://www.gledaitv.fan/tlc-bg-alternative-live-tv.html"
                    ],
            "url_hd": "https://www.gledaitv.fan/tlc-bg-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/b1/TLC_%282021%29.svg/revision/latest/scale-to-width-down/250?cb=20220703193228",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/8/85/Travel_Channel_2018.svg/revision/latest/scale-to-width-down/250?cb=20241104144156",
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
            "image": "https://www.predavatel.com/bg/tv/cable-sat_img/traveltv.png",
            "epg_id": "Travel.TV.bg",
            "epg_source": "BG1",
        },
        "TVN": {
            "url": ["https://www.gledaitv.fan/tvn-live-tv.html", "https://www.gledaitv.fan/tvn-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/tvn-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/6/66/TVN_Poland.svg/revision/latest/scale-to-width-down/200?cb=20170730155409",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/f/fc/ARD_2019.svg/revision/latest/scale-to-width-down/250?cb=20191203202109",
            "epg_id": "",
            "epg_source": "",
        },
        "ATV": {
            "url": ["https://www.gledaitv.fan/atv-live-tv.html", "https://www.gledaitv.fan/atv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/atv-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/7/72/%D0%90%D0%A2%D0%921.jpg/revision/latest?cb=20130316004926",
            "epg_id": "",
            "epg_source": "",
        },
        "Bayerischer Rundfunk": {
            "url": ["https://www.gledaitv.fan/bayerischer-rundfunk-live-tv.html", "https://www.gledaitv.fan/bayerischer-rundfunk-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/bayerischer-rundfunk-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/1/17/Bayerischer_Rundfunk_2024.svg/revision/latest/scale-to-width-down/200?cb=20241116232723",
            "epg_id": "",
            "epg_source": "",
        },
        "BEK SPORTS": {
            "url": ["https://www.gledaitv.fan/bek-sports-live-tv.html", "https://www.gledaitv.fan/bek-sports-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/bek-sports-hd-live-tv.html",
            "image": "https://media.licdn.com/dms/image/v2/C4E1BAQEWKuXkkKFlUA/company-background_10000/company-background_10000/0/1584254146512/bek_sports_network_cover?e=2147483647&v=beta&t=ZqpJpPhI6yrEWZ3Ynn8iEoFF5viyH2wblydV4qDXxxU",
            "epg_id": "",
            "epg_source": "",
        },
        "BFM": {
            "url": ["https://www.gledaitv.fan/bfm-live-tv.html", "https://www.gledaitv.fan/bfm-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/bfm-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/9/91/BFM_Business_2025.svg/revision/latest/scale-to-width-down/300?cb=20251217115352",
            "epg_id": "",
            "epg_source": "",
        },
        "C8 FR": {
            "url": ["https://www.gledaitv.fan/c8-fr-live-tv.html", "https://www.gledaitv.fan/c8-fr-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/c8-fr-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/4/47/C8_logo.jpg/revision/latest/scale-to-width-down/250?cb=20160917134013",
            "epg_id": "",
            "epg_source": "",
        },
        "Carousel": {
            "url": ["https://www.gledaitv.fan/carousel-live-tv.html", "https://www.gledaitv.fan/carousel-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/carousel-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/c/c3/Carousel_%28food%29.png/revision/latest/scale-to-width-down/250?cb=20200701151859",
            "epg_id": "",
            "epg_source": "",
        },
        "DEUTSCHE WELLE": {
            "url": ["https://www.gledaitv.fan/deutsche-welle-live-tv.html", "https://www.gledaitv.fan/deutsche-welle-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/deutsche-welle-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/7/75/Deutsche_Welle_symbol_2012.svg/revision/latest/scale-to-width-down/250?cb=20120227170040",
            "epg_id": "",
            "epg_source": "",
        },
        "FITE": {
            "url": ["https://www.gledaitv.fan/fite-live-tv.html", "https://www.gledaitv.fan/fite-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/fite-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/ucp-internal-test-starter-commons/images/1/1a/Fandom_wiki_image_placeholder.jpg/revision/latest/thumbnail-down/width/500/height/320?cb=20210813082201",
            "epg_id": "",
            "epg_source": "",
        },
        "France 24": {
            "url": ["https://www.gledaitv.fan/france-24-live-tv.html", "https://www.gledaitv.fan/france-24-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/france-24-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/0/02/France_24_2013.svg/revision/latest/scale-to-width-down/200?cb=20210115151030",
            "epg_id": "",
            "epg_source": "",
        },
        "History Channel RU": {
            "url": ["https://www.gledaitv.fan/history-channel-ru-live-tv.html", "https://www.gledaitv.fan/history-channel-ru-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/history-channel-ru-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/e/e8/History_2021.png/revision/latest/scale-to-width-down/200?cb=20240302050750",
            "epg_id": "",
            "epg_source": "",
        },
        "Nick Jr. RU": {
            "url": ["https://www.gledaitv.fan/nick-jr-ru-live-tv.html", "https://www.gledaitv.fan/nick-jr-ru-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/nick-jr-ru-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/5/55/Nick_Jr..svg/revision/latest/scale-to-width-down/250?cb=20251017154510",
            "epg_id": "",
            "epg_source": "",
        },
        "Nickelodeon RU": {
            "url": ["https://www.gledaitv.fan/nickelodeon-ru-live-tv.html", "https://www.gledaitv.fan/nickelodeon-ru-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/nickelodeon-ru-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/0/07/Nickelodeon_%282009%29.svg/revision/latest/scale-to-width-down/350?cb=20180306141612",
            "epg_id": "",
            "epg_source": "",
        },
        "PRO 7": {
            "url": ["https://www.gledaitv.fan/pro-7-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/pro-7-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/2/23/ProSieben.svg/revision/latest/scale-to-width-down/200?cb=20180720004109",
            "epg_id": "",
            "epg_source": "",
        },
        "RTL": {
            "url": ["https://www.gledaitv.fan/rtl-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/rtl-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/7/7f/RTL_%282021%29_II.svg/revision/latest/scale-to-width-down/300?cb=20210821210002",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/8/85/TRT_1_logo_%282021-%29.svg/revision/latest/scale-to-width-down/250?cb=20210205115406",
            "epg_id": "",
            "epg_source": "",
        },
        "TV5 Monde": {
            "url": ["https://www.gledaitv.fan/tv5-monde-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/tv5-monde-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/d/db/TV5Monde_2025.svg/revision/latest/scale-to-width-down/300?cb=20251010001858",
            "epg_id": "",
            "epg_source": "",
        },
        "WDR": {
            "url": ["https://www.gledaitv.fan/wdr-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/wdr-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/1/14/WDR_2012.svg/revision/latest/scale-to-width-down/250?cb=20210104151500",
            "epg_id": "",
            "epg_source": "",
        },
        "ZDF": {
            "url": ["https://www.gledaitv.fan/zdf-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/zdf-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/c/c1/ZDF_logo.svg/revision/latest/scale-to-width-down/200?cb=20230702131102",
            "epg_id": "",
            "epg_source": "",
        },
    },
    "Music": {
        "Balkanika Tv": {
            "url": ["https://www.gledaitv.fan/balkanika-tv-live-tv.html", "https://www.gledaitv.fan/balkanika-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/balkanika-tv-hd-live-tv.html",
            "image": "https://balkanika.tv/wp-content/uploads/2018/07/logo_Balkanika_kvadrat.png",
            "epg_id": "Balkanika.MTV.bg",
            "epg_source": "BG1",
        },
        "Rodina Tv": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=rodina-tv&pass=",
                "https://www.seirsanduk.online/?player=12&id=rodina-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=rodina-tv&pass=",
            ],
            "url_hd": "",
            "image": "https://www.predavatel.com/bg/2/blagoevgrad_img/tv-rodina.png",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/0/03/DStv_2023.svg/revision/latest/scale-to-width-down/300?cb=20240206012331",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://www.city.bg/theme_assets/city/images/sharing/radio_default_banner.jpg",
            "epg_id": "",
            "epg_source": "",
        },
        "Fen TV": {
            "url": ["https://www.gledaitv.fan/fen-tv-live-tv.html", "https://www.gledaitv.fan/fen-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/fen-tv-hd-live-tv.html",
            "image": "https://fentv.bg/wp-content/uploads/2020/12/Logo_FENTV_Tvoyata_Muzika.png",
            "epg_id": "Фен.ТВ.bg",
            "epg_source": "BG1",
        },
        "Kral Pop Tv": {
            "url": ["https://www.gledaitv.fan/kral-pop-tv-live-tv.html", "https://www.gledaitv.fan/kral-pop-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/kral-pop-tv-hd-live-tv.html",
            "image": "https://img-puhutv.mncdn.com/media/img/content/23-01/26/kral.png",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/5/53/Ggggggggggg.png/revision/latest/scale-to-width-down/180?cb=20200921161244",
            "epg_id": "Планета.Фолк.bg",
            "epg_source": "BG1",
        },
        "Folklor TV": {
            "url": [
                "https://www.seirsanduk.online/?player=11&id=folklor-tv&pass=",
                "https://www.seirsanduk.online/?player=12&id=folklor-tv&pass=",
                "https://www.seirsanduk.online/?player=13&id=folklor-tv&pass=",
            ],
            "url_hd": "",
            "image": "https://www.predavatel.com/bg/tv/cable-sat_img/folklor.png",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/1/13/Phd1.png/revision/latest/scale-to-width-down/180?cb=20200517141118",
            "epg_id": "Планета.HD.bg",
            "epg_source": "BG1",
        },
        "Power Türk": {
            "url": ["https://www.gledaitv.fan/power-turk-live-tv.html", "https://www.gledaitv.fan/power-turk-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/power-turk-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/1/19/PowerTurk_TV.png/revision/latest/scale-to-width-down/250?cb=20220108110609",
            "epg_id": "",
            "epg_source": "",
        },
        "Tatlıses Tv": {
            "url": ["https://www.gledaitv.fan/tatlises-tv-live-tv.html", "https://www.gledaitv.fan/tatlises-tv-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/tatlises-tv-hd-live-tv.html",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLH7L5oWqFnXwW03mdTGsxG-4KPbAR3lAaoA&s",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/2/2b/The_Voicen_logo.svg/revision/latest/scale-to-width-down/250?cb=20150311194437",
            "epg_id": "",
            "epg_source": "",
        },
        "Trt Müzik": {
            "url": ["https://www.gledaitv.fan/trt-muzik-live-tv.html", "https://www.gledaitv.fan/trt-muzik-alternative-live-tv.html"],
            "url_hd": "https://www.gledaitv.fan/trt-muzik-hd-live-tv.html",
            "image": "https://static.wikia.nocookie.net/logopedia/images/f/f2/TRT_M%C3%BCzik_logo.svg/revision/latest/scale-to-width-down/300?cb=20210827231942",
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
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/8/81/Magic_TV_BG.svg/revision/latest/scale-to-width-down/250?cb=20210516105635",
            "epg_id": "",
            "epg_source": "",
        },
        "Retro Music": {
            "url": ["https://www.parsatv.com/name=Retro-Music#music"],
            "url_hd": "",
            "image": "https://static.wikia.nocookie.net/logopedia/images/b/b9/Retro_Music_Television_2013.svg/revision/latest/scale-to-width-down/250?cb=20210627161000",
            "epg_id": "",
            "epg_source": "",
        },
        "Rock TV": {
            "url": ["https://www.rockfm.ro/rocktv"],
            "url_hd": "https://freetv.studio/channel/RockTV.ro",
            "image": "https://static.wikia.nocookie.net/logopedia/images/6/6e/Rock_TV_2.svg/revision/latest/scale-to-width-down/150?cb=20220626120305",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://static.wikia.nocookie.net/logopedia/images/d/d7/NOVE_TV_LOGO_2016.png/revision/latest/scale-to-width-down/200?cb=20160806153837",
            "epg_id": "",
            "epg_source": "",
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
            "epg_id": "",
            "epg_source": "",
        },
        "Lamore Rock Show WebTV": {
            "url": ["https://freetv.studio/channel/LamoreRockShowWebTV.br"],
            "url_hd": "",
            "image": "",
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
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://i.imgur.com/GuM4GnX.png",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://images.pluto.tv/channels/660c209e19ca71000846cf38/colorLogoPNG.png",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://i.imgur.com/YyPnMeB.png",
            "epg_id": "",
            "epg_source": "",
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
            "image": "https://i.imgur.com/qiCCX5X.png",
            "epg_id": "",
            "epg_source": "",
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
