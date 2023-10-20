# Flatten
A script for flattening the file structue of single projects or folders of multiple projects

## Flags
`--input`, `-i` full path to input folder  
`--mode`, `-m` inputs include `single` for one project and `batch` for a folder of multiple project

## Usage
### Single Project
`path/to/run.py -i path/to/input/folder -m single`
#### Before
```
item (script input)
├── p
|   └── item_v01_p.wav
├── a
|   └── item_v01_a.wav
└── s
    └── item_v01_s.json
```
#### After
```
item (script input)
├── item_v01_p.wav
├── item_v01_a.wav
└── item_v01_s.json
```
### Batch of Projects
`path/to/run.py -i path/to/input/folder -m batch`
#### Before
```
project folder (script input)
├── item_1
│   ├── p
│   |   └── item_1_v01_p.wav
|   ├── a
|   |   └── item_1_v01_a.wav
|   └── s
|       └── item_1_v01_s.json
└── item_2
    ├── p
    |   └── item_2_v01_p.wav
    ├── a
    |   └── item_2_v01_a.wav
    └── s
        └── item_2_v01_s.json
```
#### After
```
project folder (script input)
├── item_1
│   ├── item_1_v01_p.wav
|   ├── item_1_v01_a.wav
|   └── item_1_v01_s.json
└── item_2
    ├── item_2_v01_p.wav
    ├── item_2_v01_a.wav
    └── item_2_v01_s.json