Plotting scripts for H+c analysis.  
Input trees are produced using [NanoHc](https://github.com/yiannispar/NanoHc) framework.  

Checkout  
---------------    
```bash  
git clone git@github.com:yiannispar/PlotToolsHc.git    
```  

Run  
-----------  
```bash  
python3 makePlots (--type ["shape","stack"])  
```

Notes  
-----  
- You can change settings in config.py  
- You can add/remove samples in makePlots.py  
- If you want to plot branches not already present in the trees (eg DeltaR) you can calculate this by implementing C++ functions (cpp_functions.C)  