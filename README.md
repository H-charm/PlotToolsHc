Plotting scripts for H+c analysis.  
Input trees are produced using [NanoHc](https://github.com/H-charm/NanoHc.git) framework.  

Checkout  
---------------    
```bash  
git clone https://github.com/H-charm/PlotToolsHc.git
git checkout nikos
```  
Dependencies
---------------
A specific version of the cmsstyle package is required. Install it using:
```bash
pip install --user cmsstyle==0.4.3
```

Run  
-----------  
Before running the script change setting in `config.py`

```bash  
python3 makePlotsCMS.py (-d <PathToDataFiles>)  
```
