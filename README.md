# Capstone
All code files for adjustable pediatric socket, mainly code for pressure reading and visualization

# findPointOnMesh.py
use this tool to locate points on the leg model

# regionMapping.py
uses either the arduino ingested data or simulated data to put colour coded pressure mappings on the leg

# serialConnectTest.py
test serial connection to arduino

# SimPressureWPot.ino
basic arduino code to send data over serial, basic circuit just using potentiometer to simulate varying strain gauge (connected to A0)

## To setup env
run the following
```bash
pip install -e .
```
```bash
conda env create -f environment.yml
conda activate capstone
```
