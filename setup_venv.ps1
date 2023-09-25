
# redirect stderr into stdout
$p = &{py -V} 2>&1
# check if an ErrorRecord was returned
$version = if($p -is [System.Management.Automation.ErrorRecord])
{
    # grab the version string from the error message
    $p.Exception.Message
}
else
{
    # otherwise return complete Python list
    $ErrorActionPreference = 'SilentlyContinue'
    $PyVer = py --list
}

# deactivate any activated venvs
if ($PyVer -like "*venv*")
{
  deactivate # make sure we don't update the wrong venv
  $PyVer = py --list # update list
}

Write-Host "Python versions found are"
Write-Host ($PyVer | Out-String) # formatted output with line breaks
if (!($PyVer.length -ne 0)) {$p} # return Python --version String if py.exe is unavailable
if (!($PyVer -like "*3.11*") -and !($p -like "*3.11*")) # if 3.11 is not in any list
{
    Write-Host "Please install Python 3.11 and try again"
    exit 34
}   

if ($NULL -ne $PyVer) {py -3.11 -m venv .\pygame.venv\}
else {python -m venv .\pygame.venv\}
.\pygame.venv\Scripts\activate
python -m pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
