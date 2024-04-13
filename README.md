# pyrtty
Python 3 script/library for converting text to an rtty audio signal

## Step 0 Prep

### Linux (Required)
Ensure `PortAudio` is installed
```
$sudo apt-get install libportaudio2
```

### Venv (recommended)

Use a python venv to run this application in. I typically use a folder named `venv` in the same directory and have it excluded in the `.gitignore`
```
$python -m venv venv
$source venv/bin/activate
```
or
```
>python -m venv venv
>venv/bin/activate.cmd (or .ps if using powershell)
```
## Step 1 requirements.txt
```
pip -r requirements.txt
```

## Step 2 Run
For now, you can use this as just a invocable script
```
python pyrtty.py
```