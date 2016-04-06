# Copyright (c) 2015 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Root domains can not be used as a service domains, as most of the DNS
# providers does not allow setting a CNAME on a root domain. This file contains
# regular expressions used for checking if a domain is a root domain or not.

# regex for a generic country code based root domain
generic_cc_tld = r'''([^.]+\.(ac|biz|co|com|edu|gov|id|int|ltd|me|mil|mod|
    my|name|net|nhs|nic|nom|or|org|plc|sch|web)\.(ac|ad|ae|af|ag|ai|al|am|
    an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|
    bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cw|cx|
    cy|cz|de|dj|dk|dm|do|dz|ec|ee|eg|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gd|
    ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|
    ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|
    kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|
    mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|
    om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|
    sc|sd|se|sg|sh|si|sk|sl|sm|sn|so|sr|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|
    tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|
    vn|vu|wf|ws|ye|yt|za|zm|zw))$'''

# edge cases regexs for country codes based root domain
australia_tld = r'''([^.]+\.(act|asn|com|csiro|edu|gov|id|net|nsw|nt|org|oz|
    qld|sa|tas|vic|wa)\.au)$'''
austria_tld = r'''([^.]+\.(ac|co|gv|or|priv)\.at)$'''
france_tld = r'''([^.]+\.(aeroport|avocat|avoues|cci|chambagri|
    chirurgiens-dentistes|experts-comptables|geometre-expert|greta|
    huissier-justice|medecin|notaires|pharmacien|port|veterinaire)\.fr)$'''
hungary_tld = r'''([^.]+\.(co|2000|erotika|jogasz|sex|video|info|agrar|film|
    konyvelo|shop|org|bolt|forum|lakas|suli|priv|casino|games|media|szex|
    sport|city|hotel|news|tozsde|tm|erotica|ingatlan|reklam|utazas)\
    .hu)$'''
russia_tld = r'''([^.]+\.(ac|com|edu|int|net|org|pp|gov|mil|test|adygeya|
    bashkiria|ulan-ude|buryatia|dagestan|nalchik|kalmykia|kchr|ptz|karelia|
    komi|mari-el|joshkar-ola|mari|mordovia|yakutia|vladikavkaz|kazan|
    tatarstan|tuva|udmurtia|izhevsk|udm|khakassia|grozny|chuvashia|altai|
    kuban|krasnoyarsk|marine|vladivostok|stavropol|stv|khabarovsk|khv|amur|
    arkhangelsk|astrakhan|belgorod|bryansk|vladimir|volgograd|tsaritsyn|
    vologda|voronezh|vrn|cbg|ivanovo|irkutsk|koenig|kaluga|kamchatka|
    kemerovo|kirov|vyatka|kostroma|kurgan|kursk|lipetsk|magadan|mosreg|
    murmansk|nnov|nov|nsk|novosibirsk|omsk|orenburg|oryol|penza|perm|pskov|
    rnd|ryazan|samara|saratov|sakhalin|yuzhno-sakhalinsk|yekaterinburg|
    e-burg|smolensk|tambov|tver|tomsk|tsk|tom|tula|tyumen|simbirsk|
    chelyabinsk|chel|chita|yaroslavl|msk|spb|bir|jar|palana|dudinka|surgut|
    chukotka|yamal|amursk|baikal|cmw|fareast|jamal|kms|k-uralsk|kustanai|
    kuzbass|magnitka|mytis|nakhodka|nkz|norilsk|snz|oskol|pyatigorsk|
    rubtsovsk|syzran|vdonskzgrad)\.ru)$'''
south_africa_tld = r'''([^.]+\.(ac|gov|law|mil|net|nom|school)\.za)$'''
spain_tld = r'''([^.]+\.(gob|nom|org)\.es)$'''
turkey_tld = r'''([^.]+\.(av|bbs|bel|biz|com|dr|edu|gen|gov|info|k12|kep|
    name|net|org|pol|tel|tsk|tv|web)\.tr)$'''
uk_tld = r'''([^.]+\.(ac|co|gov|ltd|me|mod|net|nhs|org|plc|police|sch)
    \.uk)$'''
usa_tld = r'''([^.]+\.(al|ak|az|ar|as|ca|co|ct|de|dc|fl|ga|gu|hi|id|il|in|
    ia|ks|ky|la|me|md|ma|mi|mn|mp|ms|mo|mt|ne|nv|nh|nj|nm|ny|nc|nd|oh|ok|
    or|pa|pr|ri|sc|sd|tn|tx|um|ut|vt|va|vi|wa|wv|wi|wy)\.us)$'''

# regexs for two, three and four segments
two_segments = r'''^[^.]+\.[^.]+$'''
three_segments = r'''^[^.]+\.[^.]+\.[^.]+$'''
four_or_more_segments = r'''^[^.]+\.[^.]+\.[^.]+\.[^.]'''
