# Copyright (c) 2013 Rackspace, Inc.
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

from oslo_log import log

from poppy.model.helpers import geo_zones

LOG = log.getLogger(__name__)

REGIONS = ['North America', 'South America', 'EMEA', 'Japan', 'India', 'APAC']

REGION_COUNTRY_MAPPING = {
    'North America': [
        'Antigua and Barbuda',
        'Aruba',
        'Bahamas',
        'Barbados',
        'Belize',
        'Bermuda',
        'British Virgin Islands',
        'Cayman Islands',
        'Cuba',
        'Dominica',
        'Dominican Republic',
        'El Salvador',
        'Greenland',
        'Grenada',
        'Guadeloupe',
        'Guatemala',
        'Haiti',
        'Honduras',
        'Jamaica',
        'Martinique',
        'Mexico',
        'Montserrat',
        'Netherlands Antilles',
        'Nicaragua',
        'USA',
        'Canada',
        'Panama',
        'Puerto Rico',
        'St Kitts and Nevis',
        'St Lucia', 'St Pierre and Miquelon',
        'St Vincent and The Grenadines', 'Trinidad and Tobago',
        'Turks and Caicos Islands', 'Virgin', 'St Tome and Principe'],

    'South America': [
        'Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia',
        'Costa Rica', 'Ecuador', 'Falkland Islands', 'French Guiana',
        'Guyana', 'Paraguay', 'Peru', 'South Georgia and South Sanwich',
        'Suriname', 'Uruguay', 'Venezuela',
    ],

    'EMEA(Europe, Middle East and Africa)': [
        'Albania', 'Algeria', 'Andorra', 'Angola', 'Austria', 'Bahrain',
        'Belarus', 'Belgium', 'Benin', 'Bosnia and Herzegovina', 'Botswana',
        'Bouvet Island', 'British Indian Ocean Territory', 'Bulgaria',
        'Burkina',
        'Burundi', 'Cameroon', 'Cape Verde', 'Central African Republic',
        'Chad',
        'Comoros', 'Congo', 'Cote D\'Ivoire', 'Croatia', 'Cyprus',
        'Czech Republic', 'Democratic Republic of Congo', 'Denmark',
        'Djibouti',
        'Egypt', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia',
        'Faeroe Islands', 'Finland', 'France',
        'Gabon', 'Gambia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Guinea',
        'Guinea Bissau', 'Hungary', 'Iceland', 'Iran', 'Iraq', 'Ireland',
        'Israel',
        'Italy', 'Jordan, Kenya', 'Kuwait', 'Latvia', 'Lebanon', 'Lesotho',
        'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg',
        'Macedonia', 'Madagascar', 'Malawi', 'Mali', 'Malta', 'Mauritania',
        'Mauritius', 'Mayotte', 'Moldavia', 'Monaco', 'Morocco', 'Mozambique',
        'Namibia', 'Netherlands', 'Niger', 'Nigeria', 'Norway', 'Oman',
        'Poland',
        'Portugal', 'Qatar', 'Reunion', 'Romania', 'Russia', 'Rwanda',
        'San Marino', 'Saudi Arabia', 'Senegal, Seychelles', 'Sierra Leone',
        'Slovakia', 'Slovenia', 'Somalia', 'South Africa', 'Spain',
        'St Helena', 'Sudan', 'Svalbard', 'Swaziland', 'Sweden', 'Switzerland',
        'Syria', 'Tanzania', 'Togo', 'Tunisia', 'Turkey', 'Uganda',
        'United Arab Emirates', 'United Kingdom', 'Vatican City',
        'Western Sahara', 'Yemen', 'Yugoslavia', 'Zambia', 'Zimbabwe',
    ],

    'Japan': [
        'Japan'
    ],

    'India': [
        'India'
    ],

    'Australia/NZ': [
        'Australia',
        'New Zealand'
    ],

    'Rest Of APAC': [
        'Afghanistan', 'American Samoa', 'Antarctica', 'Armenia', 'Azerbaijan',
        'Bangladesh', 'Bhutan', 'Brunei', 'Cambodia', 'Christmas Island',
        'Cocos', 'Cook Islands', 'East Timor', 'Fiji', 'French Polynesia',
        'French Southern Territories', 'Georgia', 'Guam',
        'Heard and McDonald Islands', 'Hong Kong', 'Indonesia', 'Kazakhstan',
        'Kiribati', 'Kyrgyzstan', 'Laos', 'Macau', 'Malaysia', 'Maldives',
        'Marshall Islands', 'Micronesia', 'Mongolia', 'Myanmar', 'Nauru',
        'Nepal', 'New Caledonia', 'Niue', 'Norfolk Island', 'North Korea',
        'Northern Mariana Islands', 'Pakistan', 'Palau', 'Papua New Guinea',
        'Philippines', 'Pitcairn'
    ]

}

COUNTRY_CODE_MAPPING = {
    # North America
    'Antigua and Barbuda': 'AG',
    'Aruba': 'AW',
    'Bahamas': 'BS',
    'Barbados': 'BB',
    'Belize': 'BZ',
    'Bermuda': 'BM',
    'British Virgin Islands': 'VG',
    'Cayman Islands': 'KY',
    'Cuba': 'CU',
    'Dominica': 'DM',
    'Dominican Republic': 'DO',
    'El Salvador': 'SV',
    'Greenland': 'GL',
    'Grenada': 'GD',
    'Guadeloupe': 'GP',
    'Guatemala': 'GT',
    'Haiti': 'HT',
    'Honduras': 'HN',
    'Jamaica': 'JM',
    'Martinique': 'MQ',
    'Mexico': 'MX',
    'Montserrat': 'MS',
    'Netherlands Antilles': '',
    'Nicaragua': 'NI',
    'USA': 'US',
    'Canada': 'CA',
    'Panama': 'PA',
    'Puerto Rico': 'PR',
    'St Kitts and Nevis': 'KN',
    'St Lucia': 'LC',
    'St Pierre and Miquelon': 'PM',
    'St Vincent and the  Grenadines': 'VC',
    'Trinidad and Tobago': 'TT',
    'Turks and Caicos Islands': 'TC',
    'Virgin': '',
    'St Tome and Principe': 'ST',

    # South America
    'Argentina': 'AR',
    'Bolivia': 'BO',
    'Brazil': 'BR',
    'Chile': 'CL',
    'Colombia': 'CO',
    'Costa Rica': 'CR',
    'Ecuador': 'EC',
    'Falkland Islands': 'FK',
    'French Guiana': 'GF',
    'Guyana': 'GY',
    'Paraguay': 'PY',
    'Peru': 'PE',
    'South Georgia and South Sandwich': 'GS',
    'Suriname': 'SR',
    'Uruguay': 'UY',
    'Venezuela': 'VE',

    # EMEA (Europe  Middle East and Africa)
    'Albania': 'AL',
    'Algeria': 'DZ',
    'Andorra': 'AD',
    'Angola': 'AO',
    'Austria': 'AT',
    'Bahrain': 'BH',
    'Belarus': 'BY',
    'Belgium': 'BE',
    'Benin': 'BJ',
    'Bosnia and Herzegovina': 'BA',
    'Botswana': 'BW',
    'Bouvet Island': 'BV',
    'British Indian Ocean Territory': 'IO',
    'Bulgaria': 'BG',
    'Burkina': 'BF',
    'Burundi': 'BI',
    'Cameroon': 'CM',
    'Cape Verde': '',
    'Central African Republic': 'CF',
    'Chad': 'TD',
    'Comoros': 'KM',
    'Congo': 'CG',
    'Cote d\'Ivoire': 'CI',
    'Croatia': 'HR',
    'Cyprus': 'CY',
    'Czech Republic': 'CZ',
    'Democratic Republic of Congo': 'CD',
    'Denmark': 'DK',
    'Djibouti': 'DJ',
    'Egypt': 'EG',
    'Equatorial Guinea': 'GQ',
    'Eritrea': 'ER',
    'Estonia': 'EE',
    'Ethiopia': 'ET',
    'Faeroe Islands': 'FO',
    'Finland': 'FI',
    'France': 'FR',
    'France (European Territory)': '',
    'Gabon': 'GA',
    'Gambia': 'GM',
    'Germany': 'DE',
    'Ghana': 'GH',
    'Gibraltar': 'GI',
    'Greece': 'GR',
    'Guinea': 'GN',
    'Guinea Bissau': 'GW',
    'Hungary': 'HU',
    'Iceland': 'IS',
    'Iran': 'IR',
    'Iraq': 'IQ',
    'Ireland': 'IE',
    'Israel': 'IL',
    'Italy': 'IT',
    'Jordan': 'JO',
    'Kenya': 'KE',
    'Kuwait': 'KW',
    'Latvia': 'LV',
    'Lebanon': 'LB',
    'Lesotho': 'LS',
    'Liberia': 'LR',
    'Libya': 'LY',
    'Liechtenstein': 'LI',
    'Lithuania': 'LT',
    'Luxembourg': 'LU',
    'Macedonia': 'MK',
    'Madagascar': 'MG',
    'Malawi': 'MW',
    'Mali': 'ML',
    'Malta': 'MT',
    'Mauritania': 'MR',
    'Mauritius': 'MU',
    'Mayotte': 'YT',
    # Moldavia has become Moldova
    # 'Moldavia': '',
    'Monaco': 'MC',
    'Morocco': 'MA',
    'Mozambique': 'MZ',
    'Namibia': 'NA',
    'Netherlands': 'NL',
    'Niger': 'NE',
    'Nigeria': 'NG',
    'Norway': 'NO',
    'Oman': 'OM',
    'Poland': 'PL',
    'Portugal': 'PT',
    'Qatar': 'QA',
    'Reunion': 'RE',
    'Romania': 'RO',
    'Russia': 'RU',
    'Rwanda': 'RW',
    'San Marino': 'SM',
    'Saudi Arabia': 'SA',
    'Senegal  Seychelles': 'SC',
    'Sierra Leone': 'SL',
    'Slovakia': 'SK',
    'Slovenia': 'SI',
    'Somalia': 'SO',
    'South Africa': 'ZA',
    'Spain': 'ES',
    'St Helena': 'SH',
    'Sudan': 'SD',
    'Svalbard': 'SJ',
    'Swaziland': 'SZ',
    'Sweden': 'SE',
    'Switzerland': 'CH',
    'Syria': 'SY',
    'Tanzania': 'TZ',
    'Togo': 'TG',
    'Tunisia': 'TN',
    'Turkey': 'TR',
    'Uganda': 'UG',
    'United Arab Emirates': 'AE',
    'United Kingdom': 'GB',
    'Vatican City': 'VA',
    'Western Sahara': 'EH',
    'Yemen': 'YE',
    # There is no Yugoslavia no more
    # 'Yugoslavia': '',
    'Zambia': 'ZM',
    'Zimbabwe': 'ZW',

    # Japan:
    'Japan': 'JP',

    # India
    'India': 'IN',

    # Australia
    'Australia': 'AU',
    'New Zealand': 'NZ',

    # Rest Of APAC:
    'Afghanistan': 'AF',
    'American Samoa': 'AS',
    'Antarctica': 'AQ',
    'Armenia': 'AM',
    'Azerbaijan': 'AZ',
    'Bangladesh': 'BD',
    'Bhutan': 'BT',
    'Brunei': 'BN',
    'Cambodia': 'KH',
    'Christmas Island': 'CX',
    'Cocos': 'CC',
    'Cook Islands': 'CK',
    'East Timor': 'TL',
    'Fiji': 'FJ',
    'French Polynesia': 'PF',
    'French Southern Territories': 'TF',
    'Georgia': 'GE',
    'Guam': 'GU',
    'Heard and Mcdonald  Islands': 'HM',
    'Hong Kong': 'HK',
    'Indonesia': 'ID',
    'Kazakhstan': 'KZ',
    'Kiribati': 'KI',
    'Kyrgyzstan': 'KG',
    'Laos': 'LA',
    'Macau': 'MO',
    'Malaysia': 'MY',
    'Maldives': 'MV',
    'Marshall Islands': 'MH',
    'Micronesia': 'FM',
    'Mongolia': 'MN',
    'Myanmar': 'MM',
    'Nauru': 'NR',
    'Nepal': 'NP',
    'New Caledonia': 'NC',
    'Niue': 'NU',
    'Norfolk Island': 'NF',
    'North Korea': 'KP',
    'Northern Mariana Islands': 'MP',
    'Pakistan': 'PK',
    'Palau': 'PW',
    'Papua New Guinea': 'PG',
    'Philippines': 'PH',
    'Pitcairn': 'PN'
}


for region in REGION_COUNTRY_MAPPING:
    if region not in geo_zones.GEO_REGION_ZONES:
        try:
            raise ValueError('Unsupported region config')
        except ValueError:
            LOG.warning('Unsupported region: %s in GEO zone mapping' % region)

# validate COUNTRY_CODE_MAPPING keys are in GEO_ZONES'
for country in COUNTRY_CODE_MAPPING:
    if country not in geo_zones.GEO_COUNTRY_ZONES:
        try:
            raise ValueError('Unsupported country config')
        except ValueError:
            LOG.warning(
                'Unsupported country: %s in GEO zone mapping' % country)
