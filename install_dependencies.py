import subprocess #used for running shell commands (in this case pip install)
import sys #gives access to system variables
import pkg_resources #checks packages that are installed

def install_requirements(dependencies='dependencies.txt'):

    try:
        with open(dependencies) as d:
            required = [line.strip() for line in d if line.strip()] #array in which each element is one line (dependency) from the file
        installed = {pkg.key for pkg in pkg_resources.working_set} #all installed packages
        missing = [] #will hold dependencies from required that are not in installed
        
        for pkg in required:
            base_pkg = pkg.lower().split('==')[0] #checks only base name of the package (discards ==10.2.1)
            if base_pkg not in installed:
                missing.append(pkg) #add missing packages to the missing array

        if missing: #If missing array is not empty
            print(f"Installing missing packages: {missing}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing]) #execute the install function
        else:
            print("All required packages already installed.")

    except FileNotFoundError:
        print(f"{dependencies} not found.")
    except Exception as e:
        print("Could not install requirements automatically.")
        print(e)

