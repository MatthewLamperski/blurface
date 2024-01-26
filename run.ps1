
# Clone the GitHub repository
$repo = "https://github.com/MatthewLamperski/blurface.git"
git clone $repo

$repoName = Split-Path $repo -Leaf
$repoName = $repoName.Replace('.git','')
cd $repoName

# Check if Python is installed, otherwise download and install Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {

    # Specify the Python version to download
    $pythonVersion = "3.10.0"
    $pythonInstaller = "python-$pythonVersion-amd64.exe"
    $pythonDownloadUrl = "https://www.python.org/ftp/python/$pythonVersion/$pythonInstaller"

    # Download Python installer
    Invoke-WebRequest -Uri $pythonDownloadUrl -Outfile $pythonInstaller

    # Install python
    Start-Process .\$pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
}

$envName = "venv"
python -m venv $envName

$venvScript = ".\$envName\Scripts\Activate.ps1"
. $venvScript

pip install -r requirements.txt

$scriptName = "video_capture_widget.py"

deactivate