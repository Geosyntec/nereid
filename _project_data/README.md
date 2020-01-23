# How to data

```
├───_project_data (This folder is mounted as a volume to nereid/nereid/data during the build)
│       README.md (This file. YOU ARE HERE.)
│
├───nereid
│   ├───nereid
│   │   ├───api
│   │   │   ├───api_v1
│   │   │   │   ├───endpoints
│   │   │   │   └───models
│   │   │   └───templates
│   │   ├───core
│   │   ├───data
│   │   │   ├───project_data (This folder is where the '_project_data' contents are mounted.)
│   │   │   ├───default_data
│   │   │   │   │   README.md (Learn how to structure your own project data directory by reading this file.)
│   │   │   │   │
│   │   │   │   └───state
│   │   │   │       └───region
│   │   │   │       
│   │   │   └───test_data
│   │   ├───network
│   │   ├───static
│   │   └───tests
│   └───scripts
│   
└───scripts
```