import sys
import glob

if __name__ == "__main__":
    customLibs = glob.glob('/content/drive/MyDrive/simpleZooniverse/customLibraries/*')
    for lib in customLibs:
        if not lib in sys.path:
            sys.path.insert(1, lib)
    print('Set custom PATHs')
