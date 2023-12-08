# Setting up

Make a virtual environment with
```
python -m venv venv
```

# To activate the virtual environment
## Windows
### Powershell
```
.\venv\Scripts\Activate.ps1
```
### CMD
```
.\venv\Scripts\activate.bat
```
# Linux
```
source ./venv/Scripts/activate  
```

# Warning!
Make sure the virtual environment is active before installing packages!

tip: Look for the (venv) tag, eg.
```
(venv) PS C:\Users\Roney\Desktop\Stock Prediction>
```

# Install Packages
```
pip install -r requirements.txt
```

# Run the app

If 
```
python3 app.py
```
doesn't work, use 
```
python -m flask run
```