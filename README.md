# Phylo Island

<img src="https://raw.githubusercontent.com/gabe-foley-thesis/Phylo_Island/main/images/gui.png" width="800">

# Installation

1. Clone the repo and install requirements.

Recommend to do this inside a conda environment or virtual environment


```
git clone github.com/gabe-foley-thesis/PhyloIsland
pip install -r pi/install/requirements.txt
```

2. Install MongoDB

https://docs.mongodb.com/manual/installation/

You can set the name of the database you want to create in `pi/configs/mongoconfig.py` and then when you run the application it will create this for you.


3. Load example data
The easiest way to load genomic data is via the command line interface, which can then be viewed in the GUI

Load the example genomes

```
python pi/phyloisland_cmd.py --load_genomes pi/example_data/morganella_morganii

```

Load and search with the example profile HMMs
```
python pi/phyloisland_cmd.py -p "pi/example_data/full_profiles" -u

```

4. View the GUI

```
python pi/phyloisland.py

```

You can now open a web browser and navigate to http://127.0.0.1:5000/ and you will see the Phylo Island GUI.

5. Register as a new user (there is no email validation needed in the current version)


6. Go to Genome Records to see the database view of the hits for each genome

7. Go to Genome Diagrams to see the interactive diagram view of the hits for each genome.


# Workflow

<img src="https://raw.githubusercontent.com/gabe-foley-thesis/Phylo_Island/main/images/Phylo_island_overview_2021.png" width="800">



# Notes

- Phylo Island uses session data to store certain data to help loading pages. If you run into a 404 Error try logging out and in again.

