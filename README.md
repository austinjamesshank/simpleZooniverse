# simpleZooniverse

Simplifying the Zooniverse Panoptes API functions for wider public use.

For those using Google Colab, use the script below to quickly clone this repo to your Drive:

- [Cloning script](https://colab.research.google.com/drive/18lzHK9njUxmhF9xt5jITV87mxpSDFATi#scrollTo=AItpzHuHRfmI)

For those using SciServer, modify the command below to include your username in place of {user} and run it in a new terminal in SciServer to clone this repository to your SciServer drive.

    git clone https://github.com/austinjamesshank/simpleZooniverse.git /home/idies/workspace/Storage/{user}/persistent/simpleZooniverse

---

---

# Contact Information

The best way to reach us with questions is via email to any of the following (in order of relevance):

- austinjamesshank@gmail.com
- blundgre@unca.edu
- ashank@alumni.unca.edu

# Documentation 

- [YouTube tutorial playlist](https://youtube.com/playlist?list=PL6W2skmjHTC4heOIfVFbtEYI-kZi7w5nB)
- Written documentation: NEED LINK

---

# Setup for Google Colab

**To use this repo with Google Colab, follow the steps below:**
1. Go to this link: https://colab.research.google.com/drive/18lzHK9njUxmhF9xt5jITV87mxpSDFATi#scrollTo=AItpzHuHRfmI
2. Follow the steps provided in the subsequent Jupyter Notebook to clone this repo to your Google Drive.
3. Navigate to your Google Drive and open the "simpleZooniverse" folder.
4. If you have not installed Google Colaboratory, follow the steps below. Otherwise, skip to step 5.

    a. Double-click on the "basicNotebook.ipynb".
    
    b. Click on "Open with" at the top of the screen.
    
    c. Click the "+ Connect more apps" button to add another apps.
    
    d. Find the search bar at the top of the page and search "colaboratory" and hit the "enter" key.
    
    e. Click on the Google Colaboratory icon and hit the blue "install" button. 
    
    f. Hit "continue" on the pop-up menu to allow Google Colaboratory to install in your browser, then choose the Google account you want to install it for.
    
    g. Wait for the install to complete, stay on the current page, and continue to step 6.
    
5. Click on "Open with" at the top of the screen, then choose Colaboratory. You will now be viewing the basic notebook for Simple Zooniverse. 
6. From here, simply follow the steps in the basic notebook to create a Zooniverse project with your images. If you have further questions, please refer to the documentation links at the top of this readme.

---

# Setup for SciServer

**To use this repo with SciServer, follow the steps below:**

These Jupyter notebooks are designed to be run from the SciServer Compute environment (http://www.sciserver.org/tools/compute/). SciServer provides a web-based platform for interacting with the vast database of astronomical imaging and spectroscopy from the Sloan Digital Sky Survey (SDSS; York et al. 2000). All of the computing is done in the cloud, so there's no need to download anything to a local computer. The only thing required to get started exploring the universe is a web browser!

If you set up a SciServer account and upload these notebooks into a new “container”, they should compile without error. There are two versions of each of the python notebooks in this repository. One has all of the output cleared, and one is fully compiled with worked solutions for each provided prompt.

1. Open your preferred SciServer container.
2. Click "switch to JupyterLab"
3. Click on "terminal" in the other section to open a new terminal.
4. Enter the following command (BE SURE TO CHANGE THE {user} IN THE COMMAND TO YOUR SCISERVER USERNAME: 
    
        git clone https://github.com/austinjamesshank/simpleZooniverse.git /home/idies/workspace/Storage/{user}/persistent/simpleZooniverse
    
5. The repository will now be cloned into your persistent storage folder in SciServer. Navigate to this folder and open the SciServer jupyter notebooks to begin creating a project.

---

Have fun!
