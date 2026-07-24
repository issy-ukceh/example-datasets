### Notes =============================
# This script is a work in progress. Some of the content is from the Camtrap DP example dataset
# and needs to be filled in with AMI details (e.g. descriptions, contributors).
# 
# It will need to take in at least deployments.csv and observations.csv as arguments. This script will automatically
# extract details like geographical extent, coordinate uncertainty, deployment dates and taxonomic scope.

import json
import datetime

"id": "",  #TODO: Generate UUID. Deterministic or random?
"created":  datetime.datetime.now(
    datetime.timezone.utc
).strftime("%Y-%m-%dT%H:%M:%SZ"),
"project":  {
    "id": "86cabc14-d475-4439-98a7-e7b590bed60e"  #TODO: Generate deterministic project ID for AMBER so AMBER datasets can be linked together
},
"temporal": {  #TODO: Automate as min() and max() of deployments.csv start/end dates
    "start": "2020-05-30",
    "end": "2021-04-18"
},
"coordinatePrecision": "__AUTO__",  #TODO: Automate as max() from coordinateUncertainty in deployments.csv    
"spatial": {
  "type": "Polygon",
  "coordinates": [  #TODO: Automate as extent of coordinates from deployments.csv
    [
      [
        4.013,
        50.699
      ],
      [
        5.659,
        50.699
      ],
      [
        5.659,
        51.496
      ],
      [
        4.013,
        51.496
      ],
      [
        4.013,
        50.699
      ]
    ]
  ]
},
"taxonomic": [ #TODO: Automate as list of unique orders included in observations.csv
  {
    "scientificName": "Anas platyrhynchos",
    "taxonID": "https://www.checklistbank.org/dataset/COL2023/taxon/DGP6",
    "taxonRank": "species",
    "vernacularNames": {
      "eng": "mallard",
      "nld": "wilde eend"
    }
  },
  ...
]



# Write to json
datapackage_json = json.dumps(datapackage, indent=2)

with open("../outputs/aia/datapackage.json", "w") as json_file:
    json_file.write(datapackage_json)
    
    
    
    
