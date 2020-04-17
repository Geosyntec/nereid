# How to data

Welcome to the documentation about reference data! If you are reading this, it's because you need to be able to load project specific data into this tool. That is great, and it is fully supported by the both the development build pattern, and the production build pattern (forthcoming). 

You're reading this from the default data directory here:
```
├───default_data
│   │   README.md (this file. YOU ARE HERE.)
│   │
│   └───state
│       └───region
│               bmp_params.csv
│               ...etc.
```

The `state/region` directory should contain several files to be used as data templates for providing this tool with data of your own. But where should you put it? You're likely not in a state called "state" or a region called "region" and so you should not put your data here. This data lives within the git repository but your own personal data does not (and should not). 

You should place your data into a directory structure like so:
```
├───project_data (rename this as you please.)
│   └───{state} (rename this as you please.)
│       └───{region} (rename this as you please.)
│               bmp_params.csv (don't rename these, just insert your data in an identical format.)
│               ...other files etc.
│
├───...other directories etc.
```
Please take note that whatever you choose to enter as the name for the {state} directory and the {region} directory should also be used by your api client to fetch your custom reference data file.

For example, on my system I have reference data for South Orange County, California in a folder at the top level of my git repo directory.
```
├───_project_data (this is the default, but you can change it via an environment variable.)
│   └───ca
│       └───soc
│               bmp_params.csv (I have reference files in here.)
│               ...etc.
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
│   │   │   ├───default_data
│   │   │   │   └───state
│   │   │   │       └───region
│   │   │   └───test_data
│   │   ├───network
│   │   ├───static
│   │   └───tests
│   └───scripts
│   
└───scripts

```
I've also set the environment variables on my system like so:
```
$ cat .env
PROJECT_DATA_DIRECTORY=./_no_git_project_data
```
This `.env` file is read at build time by `docker-compose` and mounts the PROJECT_DATA_DIRECTORY as a volume at `nereid/nereid/data/project_data`.

This is great because once you have ayour own data you can use it by setting the query parameters to `state={yourstate}&region={yourregion}`. For example, I can get my data in json format from here:
`http://localhost:8080/api/v1/bmp/performance_data?state=ca&region=soc`. 

This is possible because I built the directory with a structure like `ca/soc` and I provided the build-time directory path in my .env file.

This means that if I ever want to support clients in Seattle, Washington and North Orange County, CA, I could add directories like so:
```
├───_no_git_project_data 
│   ├───ca
│   │   ├───soc
│   │   │       bmp_params.csv (my original South Orange County, CA reference files are here.)
│   │   │       ...etc.
│   │   │
│   │   └───noc
│   │           bmp_params.csv (my North Orange County, CA reference files are here.)
│   │           ...etc.
│   │
│   └───wa
│       └───sea
│               bmp_params.csv (my Seattle, WA reference files are here.)
│               ...etc.
```
