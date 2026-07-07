# data_package.json

datapackage = [
  {
    "resources": [
      {
        "name": "deployments",
        "path": "deployments.csv",
        "profile": "tabular-data-resource",
        "format": "csv",
        "mediatype": "text/csv",
        "encoding": "utf-8",
        "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0.2/deployments-table-schema.json"
      },
      {
        "name": "media",
        "path": "media.csv",
        "profile": "tabular-data-resource",
        "format": "csv",
        "mediatype": "text/csv",
        "encoding": "utf-8",
        "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0.2/media-table-schema.json"
      },
      {
        "name": "observations",
        "path": "observations.csv",
        "profile": "tabular-data-resource",
        "format": "csv",
        "mediatype": "text/csv",
        "encoding": "utf-8",
        "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0.2/observations-table-schema.json"
      },
      {  #TODO: do we want a custom table?
        "name": "individuals",
        "description": "Custom table/resource not part of the Camtrap DP model. Included to showcase that extending with more resources is possible.",
        "data": [
          {
            "id": 1,
            "individualName": "Reinaert",
            "scientificName": "Vulpes vulpes"
          }
        ]
      }
    ],
    "profile": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0.2/camtrap-dp-profile.json",
    "name": "ukceh-ami-anguilla",
    "id": "7cca70f5-ef8c-4f86-85fb-8f070937d7ab", #TODO: Generate UUID. Deterministic or random?
    "created": "2023-02-06T11:23:03Z", #TODO: Automate creation timestamp
    "title": "Automated nocturnal insect imaging, Anguilla",
    "contributors": [
      { #TODO: Who should be listed as contributors?
        "title": "Axel Neukermans",
        "email": "axel.neukermans@inbo.be",
        "path": "https://orcid.org/0000-0003-0272-9180",
        "role": "contributor",
        "organization": "Research Institute for Nature and Forest (INBO)"
      },
      {
        "title": "Danny Van der beeck",
        "email": "daniel.vanderbeeck@gmail.com"
      },
      {
        "title": "Emma Cartuyvels",
        "email": "emma.cartuyvels@inbo.be",
        "role": "principalInvestigator",
        "organization": "Research Institute for Nature and Forest (INBO)"
      },
      {
        "title": "Peter Desmet",
        "email": "peter.desmet@inbo.be",
        "path": "https://orcid.org/0000-0002-8442-8025",
        "role": "contact",
        "organization": "Research Institute for Nature and Forest (INBO)"
      },
      {
        "title": "Research Institute for Nature and Forest (INBO)", #TODO: Who owns the data?
        "path": "https://inbo.be",
        "role": "rightsHolder"
      },
      {
        "title": "Research Institute for Nature and Forest (INBO)",
        "path": "https://inbo.be",
        "role": "publisher"
      }
    ],
    "description": "MICA - Muskrat and coypu camera trap observations in Belgium, the Netherlands and Germany is an occurrence dataset published by the Research Institute of Nature and Forest (INBO). It is part of the LIFE project MICA, in which innovative techniques are tested for a more efficient control of muskrat and coypu populations, both invasive species. This dataset is a sample of the original dataset and serves as an example of a Camera Trap Data Package (Camtrap DP).", #TODO: Add dataset description covering AMI and AMBER
    "version": "1.0.2",
    "keywords": [ #TODO: Add keywords, maybe from papers
      "camera traps",
      "moth"
    ],
    "image": "",
    "homepage": "https://camtrap-dp.tdwg.org/example/",
    "sources": [
      { #TODO: Update to show where we're hosting the media. CEDA?
        "title": "Agouti",
        "path": "https://www.agouti.eu",
        "email": "agouti@wur.nl",
        "version": "v3.21"
      }
    ],
    "licenses": [ #TODO: Check licensing for AMBER data
      {
        "name": "CC0-1.0",
        "scope": "data"
      },
      {
        "path": "http://creativecommons.org/licenses/by/4.0/",
        "scope": "media"
      }
    ],
    "bibliographicCitation": "Desmet P, Neukermans A, Van der beeck D, Cartuyvels E (2022). Sample from: MICA - Muskrat and coypu camera trap observations in Belgium, the Netherlands and Germany. Version 1.0.2. Research Institute for Nature and Forest (INBO). Dataset. https://camtrap-dp.tdwg.org/example/", #TODO: Update citation when title and contributors finalised
    "project": {
      "id": "86cabc14-d475-4439-98a7-e7b590bed60e", #TODO: Generate deterministic project ID for AMBER so AMBER datasets can be linked together
      "title": "AI-assisted Monitoring of Biodiversity using Edge-processing and Remote sensors",
      "acronym": "AMBER",
      "description": "Evidence is mounting of declines in wildlife across the globe, giving stark warnings for the perilous state of biodiversity. We critically lack data for insects despite the vital role they play in all ecosystems (for example, as food for birds and mammals, recycling nutrients, pollinating crops) and as indicators of climate change impacts; closing this knowledge gap for ‘the little things that run the world’ has never been more urgent. We will develop and test automated sensors, deep learning, bioacoustics and computer vision to help deliver more standardised monitoring of insects, bats and birds worldwide.", # From Alan Turing Institute website
      "samplingDesign": "targeted", #TODO: Check sampling design. Possibly targeted: non-random distribution optimized for capturing specific target species (often using various bait types)?
      "path": "https://www.ceh.ac.uk/our-science/projects/amber-automated-biodiversity-monitoring", #TODO: Link to CEH or ITA page for AMBER?
      "captureMethod": [
        "timeLapse"
      ],
      "individualAnimals": false,
      "observationLevel": [
        "media",
        "event" #TODO: Delete 'event' unless we find a way to include event-level observations
      ]
    },
    "coordinatePrecision": 0.001, #TODO: Automate as max() from coordinateUncertainty in deployments.csv
    "spatial": { #TODO: Automate as extent of coordinates from deployments.csv
      "type": "Polygon",
      "coordinates": [
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
    "temporal": { #TODO: Automate as min() and max() of deployments.csv start/end dates
      "start": "2020-05-30",
      "end": "2021-04-18"
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
      {
        "scientificName": "Anas strepera",
        "taxonID": "https://www.checklistbank.org/dataset/COL2023/taxon/DGPL",
        "taxonRank": "species",
        "vernacularNames": {
          "eng": "gadwall",
          "nld": "krakeend"
        }
      },
      {
        "scientificName": "Ardea",
        "taxonID": "https://www.checklistbank.org/dataset/COL2023/taxon/32FH",
        "taxonRank": "genus",
        "vernacularNames": {
          "eng": "great herons",
          "nld": "reigers"
        }
      },
      {
        "scientificName": "Ardea cinerea",
        "taxonID": "https://www.checklistbank.org/dataset/COL2023/taxon/GCHS",
        "taxonRank": "species",
        "vernacularNames": {
          "eng": "grey heron",
          "nld": "blauwe reiger"
        }
      },
      {
        "scientificName": "Aves",
        "taxonID": "https://www.checklistbank.org/dataset/COL2023/taxon/V2",
        "taxonRank": "class",
        "vernacularNames": {
          "eng": "bird sp.",
          "nld": "vogel"
        }
      },
      {
        "scientificName": "Homo sapiens",
        "taxonID": "https://www.checklistbank.org/dataset/COL2023/taxon/6MB3T",
        "taxonRank": "species",
        "vernacularNames": {
          "eng": "human",
          "nld": "mens"
        }
      },
      {
        "scientificName": "Martes foina",
        "taxonID": "https://www.checklistbank.org/dataset/COL2023/taxon/3Y9VW",
        "taxonRank": "species",
        "vernacularNames": {
          "eng": "beech marten",
          "nld": "steenmarter"
        }
      },
      {
        "scientificName": "Mustela putorius",
        "taxonID": "https://www.checklistbank.org/dataset/COL2023/taxon/44QYC",
        "taxonRank": "species",
        "vernacularNames": {
          "eng": "European polecat",
          "nld": "bunzing"
        }
      },
      {
        "scientificName": "Rattus norvegicus",
        "taxonID": "https://www.checklistbank.org/dataset/COL2023/taxon/4RM67",
        "taxonRank": "species",
        "vernacularNames": {
          "eng": "brown rat",
          "nld": "bruine rat"
        }
      },
      {
        "scientificName": "Vulpes vulpes",
        "taxonID": "https://www.checklistbank.org/dataset/COL2023/taxon/5BSG3",
        "taxonRank": "species",
        "vernacularNames": {
          "eng": "red fox",
          "nld": "vos"
        }
      }
    ],
    "relatedIdentifiers": [ #TODO: Add data paper here. Not sure about relationType.
      {
        "relationType": "IsDerivedFrom",
        "relatedIdentifier": "https://doi.org/10.15468/5tb6ze",
        "resourceTypeGeneral": "Dataset",
        "relatedIdentifierType": "DOI"
      },
      {
        "relationType": "IsSupplementTo",
        "relatedIdentifier": "https://inbo.github.io/camtrapdp/",
        "resourceTypeGeneral": "Software",
        "relatedIdentifierType": "URL"
      }
    ],
    "references": [ ]
  }
]

# Write to json
datapackage_json = json.dumps(datapackage, indent=2)

with open("../outputs/aia/datapackage.json", "w") as json_file:
    json_file.write(datapackage_json)