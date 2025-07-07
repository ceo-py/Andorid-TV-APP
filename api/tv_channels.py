from playwright.sync_api import sync_playwright



ALL_CHANNELS = {
        'sportni-channels': {
            "Bein Sports": {
                "url": "https://www.gledaitv.fan/bein-sports-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_bein-sports-logo_20240623012954.jpg"
            },
            "Diema Sport": {
                "url": "https://www.gledaitv.fan/diema-sport-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/diema-sport-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_diema-sport-logo_20240819161622.png"
            },
            "Diema Sport 2": {
                "url": "https://www.gledaitv.fan/diema-sport-2-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/diema-sport-2-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_diema-sport-2-logo_20240819161729.png"
            },
            "Diema Sport 3": {
                "url": "https://www.gledaitv.fan/diema-sport-3-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/diema-sport-3-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_diema-sport-3-logo_20240819161836.png"
            },
            "Eurosport 1 BG": {
                "url": "https://www.gledaitv.fan/eurosport-1-bg-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/eurosport-1-bg-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_eurosport-1-logo_20240820133202.png"
            },
            "Eurosport 2 BG": {
                "url": "https://www.gledaitv.fan/eurosport-2-bg-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/eurosport-2-bg-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_eurosport-2-logo_20240820133425.png"
            },
            "Max Sport 1": {
                "url": "https://www.gledaitv.fan/max-sport-1-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/max-sport-1-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_max-sport-1-logo_20240820143530.png"
            },
            "Max Sport 2": {
                "url": "https://www.gledaitv.fan/max-sport-2-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/max-sport-2-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_max-sport-2-logo_20240820143632.png"
            },
            "Max Sport 3": {
                "url": "https://www.gledaitv.fan/max-sport-3-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/max-sport-3-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_max-sport-3-logo_20240820143807.png"
            },
            "Max Sport 4": {
                "url": "https://www.gledaitv.fan/max-sport-4-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/max-sport-4-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_max-sport-4-logo_20240820143917.png"
            },
            "Nova Sport": {
                "url": "https://www.gledaitv.fan/nova-sport-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/nova-sport-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_nova-sport-logo_20240820145156.png"
            },
            "Ring BG": {
                "url": "https://www.gledaitv.fan/ring-bg-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/ring-bg-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_ring-bg-logo_20240820145459.png"
            },
            "Sports Tv": {
                "url": "https://www.gledaitv.fan/sports-tv-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_sports-tv-logo_20240623013238.jpg"
            },
            "TJK Tv": {
                "url": "https://www.gledaitv.fan/tjk-tv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/tjk-tv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_tjk-tv-logo_20240623013628.jpg"
            },
            "Trt Spor": {
                "url": "https://www.gledaitv.fan/trt-spor-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/trt-spor-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_trt-spor-logo_20240623010112.jpg"
            }
        },
        'filmi-channels': {
            "AMC": {
                "url": "https://www.gledaitv.fan/amc-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_amc-logo_20240819212349.png"
            },
            "AXN": {
                "url": "https://www.gledaitv.fan/axn-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_axn-logo_20240819212646.png"
            },
            "bTV Cinema": {
                "url": "https://www.gledaitv.fan/btv-cinema-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/btv-cinema-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_btv-cinema-logo_20240819213838.png"
            },
            "bTV Comedy": {
                "url": "https://www.gledaitv.fan/btv-comedy-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/btv-comedy-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_btv-comedy-logo_20240819214203.png"
            },
            "bTV Lady": {
                "url": "https://www.gledaitv.fan/btv-lady-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/btv-lady-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_btv-lady-logo_20240819214517.png"
            },
            "Diema": {
                "url": "https://www.gledaitv.fan/diema-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_diema-logo_20240820131916.png"
            },
            "Diema Family": {
                "url": "https://www.gledaitv.fan/diema-family-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_diema-family-logo_20240820132057.png"
            },
            "Epic Drama": {
                "url": "https://www.gledaitv.fan/epic-drama-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_epic-drama-logo_20240820132902.png"
            },
            "FilmBox Extra": {
                "url": "https://www.gledaitv.fan/filmbox-extra-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/filmbox-extra-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_filmbox-extra-logo_20240820133950.png"
            },
            "FilmBox Stars": {
                "url": "https://www.gledaitv.fan/filmbox-stars-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/filmbox-stars-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_filmbox-stars-logo_20240820142839.png"
            },
            "Fox Life": {
                "url": "https://www.gledaitv.fan/fox-life-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/fox-life-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_fox-life-logo_20240820143156.png"
            },
            "Kino Nova": {
                "url": "https://www.gledaitv.fan/kino-nova-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_kino-nova-logo_20240911200018.png"
            },
            "Movie Star": {
                "url": "https://www.gledaitv.fan/movie-star-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/movie-star-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_movie-star-logo_20240820144115.png"
            },
            "Scream": {
                "url": "https://www.gledaitv.fan/scream-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_scream-logo_20241018104926.png"
            },
            "STAR Channel": {
                "url": "https://www.gledaitv.fan/star-channel-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/star-channel-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_star-logo_20240820142504.png"
            },
            "Star Crime": {
                "url": "https://www.gledaitv.fan/star-crime-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/star-crime-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_star-crime-logo_20240820143035.png"
            }
        },
        'nauka-channels': {
            "Animal Planet": {
                "url": "https://www.gledaitv.fan/animal-planet-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/animal-planet-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_animal-planet-logo_20240819212508.png"
            },
            "Discovery Channel": {
                "url": "https://www.gledaitv.fan/discovery-channel-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/discovery-channel-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_discovery-channel-logo_20240820132208.png"
            },
            "DMAX": {
                "url": "https://www.gledaitv.fan/dmax-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/dmax-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_dmax-logo_20240623013500.jpg"
            },
            "DocuBox": {
                "url": "https://www.gledaitv.fan/docubox-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/docubox-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_docubox-logo_20240827155005.png"
            },
            "History Channel": {
                "url": "https://www.gledaitv.fan/history-channel-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/history-channel-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_history-channel-logo_20240820143404.png"
            },
            "Investigation Discovery": {
                "url": "https://www.gledaitv.fan/investigation-discovery-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/investigation-discovery-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_investigation-discovery-logo_20240827154313.png"
            },
            "Nat Geo Wild": {
                "url": "https://www.gledaitv.fan/nat-geo-wild-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/nat-geo-wild-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_nat-geo-wild-logo_20240820144252.png"
            },
            "National Geographic": {
                "url": "https://www.gledaitv.fan/national-geographic-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/national-geographic-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_national-geographic-channel-logo_20240820144345.png"
            },
            "TLC": {
                "url": "https://www.gledaitv.fan/tlc-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/tlc-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_tlc-logo_20240623013349.jpg"
            },
            "TRT Belgesel": {
                "url": "https://www.gledaitv.fan/trt-belgesel-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/trt-belgesel-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_trt-belgesel-logo_20240623013851.jpg"
            },
            "Viasat Explore": {
                "url": "https://www.gledaitv.fan/viasat-explore-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/viasat-explore-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_viasat-explore-logo_20240820150649.png"
            },
            "Viasat History": {
                "url": "https://www.gledaitv.fan/viasat-history-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_viasat-history-logo_20240820150752.png"
            },
            "Viasat Nature": {
                "url": "https://www.gledaitv.fan/viasat-nature-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_viasat-nature-logo_20240820150835.png"
            },
            "Yaban Tv": {
                "url": "https://www.gledaitv.fan/yaban-tv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/yaban-tv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_yaban-tv-logo_20190705173443.jpg"
            }
        },
        'novini-channels': {
            "Bulgaria ON AIR Tv": {
                "url": "https://www.gledaitv.fan/bulgaria-on-air-tv-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_bulgaria-on-air-tv-logo_20241014173407.png"
            },
            "BNT 1": {
                "url": "https://www.gledaitv.fan/bnt-1-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_bnt-1-online-logo_20240819155745.png"
            },
            "BNT 2": {
                "url": "https://www.gledaitv.fan/bnt-2-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_bnt-2-logo_20240819160058.png"
            },
            "BNT 3": {
                "url": "https://www.gledaitv.fan/bnt-3-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_bnt-3-logo_20240819160336.png"
            },
            "BNT 4": {
                "url": "https://www.gledaitv.fan/bnt-4-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_bnt-4-logo_20240819160919.png"
            },
            "bTV": {
                "url": "https://www.gledaitv.fan/btv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/btv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_btv-logo_20240819213348.png"
            },
            "Bulgaria 24": {
                "url": "https://www.gledaitv.fan/bulgaria-24-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_bulgaria-24-logo_20241014172429.png"
            },
            "Evrokom": {
                "url": "https://www.gledaitv.fan/evrokom-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_evrokom-logo_20240820133731.png"
            },
            "Kanal 3": {
                "url": "https://www.gledaitv.fan/kanal-3-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_kanal-3-logo_20241014173941.png"
            },
            "Nova": {
                "url": "https://www.gledaitv.fan/nova-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/nova-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_nova-tv-logo_20240820145031.png"
            },
            "Pervyy kanal": {
                "url": "https://www.gledaitv.fan/pervyy-kanal-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/pervyy-kanal-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_--logo_20241018103804.png"
            },
            "VTK": {
                "url": "https://www.gledaitv.fan/vtk-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_vtk-logo_20241014171657.png"
            }
        },
        'obshti-channels': {
            "24 Kitchen": {
                "url": "https://www.gledaitv.fan/24-kitchen-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/24-kitchen-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_24-kitchen-logo_20240819212026.png"
            },
            "AGRO": {
                "url": "https://www.gledaitv.fan/agro-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_agro-logo_20241014171951.png"
            },
            "bTV Action": {
                "url": "https://www.gledaitv.fan/btv-action-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/btv-action-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_btv-action-logo_20240819213614.png"
            },
            "Bulgaria ON AIR": {
                "url": "https://www.gledaitv.fan/bulgaria-on-air-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_bulgaria-on-air-logo_20240819214715.png"
            },
            "Byeaz Tv": {
                "url": "https://www.gledaitv.fan/byeaz-tv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/byeaz-tv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_byeaz-tv-logo_20240623011637.jpg"
            },
            "Code Fashion": {
                "url": "https://www.gledaitv.fan/code-fashion-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_code-fashion-logo_20241014171352.png"
            },
            "Code Health": {
                "url": "https://www.gledaitv.fan/code-health-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_code-health-logo_20241014171123.png"
            },
            "Kanal 0": {
                "url": "https://www.gledaitv.fan/kanal-0-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_kanal-0-logo_20241014172146.png"
            },
            "Kanal D": {
                "url": "https://www.gledaitv.fan/kanal-d-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/kanal-d-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_kanal-d-logo_20240623012430.jpg"
            },
            "Show Tv": {
                "url": "https://www.gledaitv.fan/show-tv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/show-tv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_show-tv-logo_20240623012328.jpg"
            },
            "Star Tv": {
                "url": "https://www.gledaitv.fan/star-tv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/star-tv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_star-tv-logo_20240623012157.jpg"
            },
            "TLC BG": {
                "url": "https://www.gledaitv.fan/tlc-bg-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_tlc-bg-logo_20240820145759.png"
            },
            "Travel Channel": {
                "url": "https://www.gledaitv.fan/travel-channel-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/travel-channel-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_travel-channel-logo_20240820150556.png"
            },
            "TVN": {
                "url": "https://www.gledaitv.fan/tvn-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_tvn-logo_20241014165058.png"
            }
        },
        'detski-channels': {
            "Cartoon Network": {
                "url": "https://www.gledaitv.fan/cartoon-network-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_cartoon-network-logo_20240819214852.png"
            },
            "Disney Channel": {
                "url": "https://www.gledaitv.fan/disney-channel-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_disney-channel-logo_20240820132440.png"
            },
            "Nick Jr.": {
                "url": "https://www.gledaitv.fan/nick-jr-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_nick-jr-logo_20240820144650.png"
            },
            "Nick Toons": {
                "url": "https://www.gledaitv.fan/nick-toons-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_nick-toons-logo_20240820151114.png"
            },
            "Nickelodeon": {
                "url": "https://www.gledaitv.fan/nickelodeon-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_nickelodeon-logo_20240820144449.png"
            },
            "Trt Çocuk": {
                "url": "https://www.gledaitv.fan/trt-cocuk-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/trt-cocuk-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_trt-cocuk-logo_20240623011311.jpg"
            }
        },
        'worldwide-channels': {
            "1 HD TV": {
                "url": "https://www.gledaitv.fan/1-hd-tv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/1-hd-tv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_1-hd-logo_20240822154318.png"
            },
            "ARD": {
                "url": "https://www.gledaitv.fan/ard-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/ard-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_ard-logo_20240827101910.png"
            },
            "ATV": {
                "url": "https://www.gledaitv.fan/atv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/atv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_atv-online-logo_20240819155302.png"
            },
            "Bayerischer Rundfunk": {
                "url": "https://www.gledaitv.fan/bayerischer-rundfunk-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/bayerischer-rundfunk-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_bayerischer-rundfunk-logo_20241018150811.png"
            },
            "BEK SPORTS": {
                "url": "https://www.gledaitv.fan/bek-sports-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_bek-sports-logo_20240823142135.png"
            },
            "BFM": {
                "url": "https://www.gledaitv.fan/bfm-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_bfm-logo_20240824144203.png"
            },
            "C8 FR": {
                "url": "https://www.gledaitv.fan/c8-fr-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_c8-fr-logo_20240824144631.png"
            },
            "Carousel": {
                "url": "https://www.gledaitv.fan/carousel-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/carousel-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_carousel-logo_20240822162847.png"
            },
            "DEUTSCHE WELLE": {
                "url": "https://www.gledaitv.fan/deutsche-welle-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/deutsche-welle-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_deutsche-welle-logo_20240823145944.png"
            },
            "FITE": {
                "url": "https://www.gledaitv.fan/fite-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_fite-logo_20240823142430.png"
            },
            "FOX TV": {
                "url": "https://www.gledaitv.fan/fox-tv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/fox-tv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_fox-tv-logo_20240819154846.png"
            },
            "France 24": {
                "url": "https://www.gledaitv.fan/france-24-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_france-24-logo_20240824144839.png"
            },
            "History Channel RU": {
                "url": "https://www.gledaitv.fan/history-channel-ru-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/history-channel-ru-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_history-channel-ru-logo_20250404121013.png"
            },
            "Nick Jr. RU": {
                "url": "https://www.gledaitv.fan/nick-jr-ru-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_nick-jr-ru-logo_20250404121512.png"
            },
            "Nickelodeon RU": {
                "url": "https://www.gledaitv.fan/nickelodeon-ru-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_nickelodeon-ru-logo_20250404121253.png"
            },
            "PRO 7": {
                "url": "https://www.gledaitv.fan/pro-7-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/pro-7-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_pro-7-logo_20240823144445.png"
            },
            "RTL": {
                "url": "https://www.gledaitv.fan/rtl-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/rtl-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_rtl-logo_20240823145302.png"
            },
            "RU TV": {
                "url": "https://www.gledaitv.fan/ru-tv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/ru-tv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_ru-tv-logo_20240822163725.png"
            },
            "Russia 1": {
                "url": "https://www.gledaitv.fan/russia-1-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/russia-1-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_russia-1-logo_20240822162221.png"
            },
            "Sila": {
                "url": "https://www.gledaitv.fan/sila-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_sila-logo_20240823142706.png"
            },
            "TRT 1": {
                "url": "https://www.gledaitv.fan/trt-1-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/trt-1-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_trt-1-logo_20240819154036.jpg"
            },
            "TV5 Monde": {
                "url": "https://www.gledaitv.fan/tv5-monde-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_tv5-monde-logo_20240824145159.png"
            },
            "WDR": {
                "url": "https://www.gledaitv.fan/wdr-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/wdr-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_wdr-logo_20241018145854.png"
            },
            "ZDF": {
                "url": "https://www.gledaitv.fan/zdf-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/zdf-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_zdf-logo_20240823145011.png"
            }
        },
        'muzikalni-channels': {
            "Balkanika Tv": {
                "url": "https://www.gledaitv.fan/balkanika-tv-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_balkanika-tv-logo_20240819212856.png"
            },
            "City Tv": {
                "url": "https://www.gledaitv.fan/city-tv-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_city-tv-logo_20240820131656.png"
            },
            "Fen TV": {
                "url": "https://www.gledaitv.fan/fen-tv-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_fen-tv-logo_20240820133830.png"
            },
            "Kral Pop Tv": {
                "url": "https://www.gledaitv.fan/kral-pop-tv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/kral-pop-tv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_kral-pop-tv-logo_20240623011836.jpg"
            },
            "MTV 00s": {
                "url": "https://www.gledaitv.fan/mtv-00s-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/mtv-00s-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_mtv-00s-logo_20250404120020.png"
            },
            "MTV Hits": {
                "url": "https://www.gledaitv.fan/mtv-hits-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/mtv-hits-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_mtv-hits-logo_20250404115742.png"
            },
            "Planeta Folk": {
                "url": "https://www.gledaitv.fan/planeta-folk-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_planeta-folk-logo_20240820145310.png"
            },
            "Planeta HD BG": {
                "url": "https://www.gledaitv.fan/planeta-hd-bg-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/planeta-hd-bg-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_planeta-hd-logo_20240820145401.png"
            },
            "Power Türk": {
                "url": "https://www.gledaitv.fan/power-turk-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/power-turk-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_power-turk-logo_20240623012030.jpg"
            },
            "Tatlıses Tv": {
                "url": "https://www.gledaitv.fan/tatlises-tv-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/tatlises-tv-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_tatlises-tv-logo_20240623012808.jpg"
            },
            "The Voice": {
                "url": "https://www.gledaitv.fan/the-voice-live-tv.html",
                "url_hd": "",
                "image": "https://www.gledaitv.fan/upload/tv/o_the-voice-logo_20240820145619.png"
            },
            "Trt Müzik": {
                "url": "https://www.gledaitv.fan/trt-muzik-live-tv.html",
                "url_hd": "https://www.gledaitv.fan/trt-muzik-hd-live-tv.html",
                "image": "https://www.gledaitv.fan/upload/tv/o_trt-muzik-logo_20240623012606.jpg"
            }
        },
    }

def extract_video_url(url):
    """Extract video URL by clicking player and capturing network requests"""
    captured_urls = []

    def handle_response(response):
        """Capture network responses containing m3u8"""
        if response.status == 200 and any(m3u8 in response.url for m3u8 in ('index.m3u8', '.m3u8')):
            print(f"Found m3u8 URL: {response.url}")
            captured_urls.append(response.url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", handle_response)

        try:
            page.goto(url, wait_until="networkidle")

        except Exception as e:
            print(f"Error during extraction: {e}")

        finally:
            browser.close()

    return captured_urls

