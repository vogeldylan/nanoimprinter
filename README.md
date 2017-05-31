# Nanoimprinter
Code library for the 2017 Nanoimprinter Summer project at NUS.
## Introduction
Code library for the project can be found at: https://github.com/vogeldylan/nanoimprinter.git

To get a local copy of the libraries onto your computer, you can install the GitHub desktop client and clone the files onto your machine.
Alternatively, if you're using either macOS or linux, you can open Terminal, navigate to the place where you want to clone the repository, and type:

``git clone https://github.com/vogeldylan/nanoimprinter``

This will download a copy of the repository into your current directory. In the future, you can navigate to the newly downloaded *nanoimprinter* folder and type `git pull` to pull the most recent updates.

To add code you've edited on your computer to the GitHub library, you can use Terminal to navigate to the *nanoimprinter* folder, type `git add .` to add your most recent changes, and type `git commit` to specify a commit message before uploading. You can then use `git push origin` to push to the master branch, or specify a branch using `git push <your branch>`.

If you encounter an error, git will tell you to pull the most recent changes from master and manually merge them. Open the conflicting file in question and find the section that git has highlighted. Manually merge the conflicting code and repeat the above process to push your merged files to the repository.

On the desktop app you can simply press *sync* to sync your most recent changes.

## Usage

The code should be run by executing the main.py script. The script will ask for a working temperature, pressure and imprinting time duration. The sample should already be positioned on the sample surface and be ready for imprinting. The script will immediately begin the heating process and bring the sample to the desired temperature. It will then apply pressure to the sample for the specified duration and cool the sample for removal.
