# Description
lei-airfoil-cfd, for CFD analysis of Leading Edge Inflatable (LEI) kite airfoils.

## :gear: Installation

### Dependencies

- OpenFoam need to be installed. See https://openfoam.org/download/11-ubuntu/ 

### User Installation

Navigate to you run/ folder in your OpenFoam directory and clone the repo

```bash
run
git clone https://github.com/corentintran/lei-airfoil-cfd.git
cd lei-airfoil-cfd/
```

## :eyes: Usage
The script src/main_compute_polars run the cfd analysis. There you can specify the caracteristics of the airfoil to analyze.

The script will 
  (a) create the desired LEI airfoil geometry 
  (b) generate the mesh and store it in data/ 
  (c) run openfoam on this mesh for the desired AOAs
  (d) generate polars plots and values and store these in the results folder.

## :wave: Contributing (optional)

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## :warning: License and Waiver

Specify the license under which your software is distributed, and include the copyright notice:

> Beyond The Sea hereby disclaims all copyright interest in the program “lei-airfoil-cfd” (one line description of the content or function) written by the Author(s).
>
> Copyright (c) [2024] [TRAN Corentin].
