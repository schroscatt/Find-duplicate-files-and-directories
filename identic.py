import argparse
import hashlib
import os.path
from collections import OrderedDict

type = 1   # c-1 n-2 cn-3 (default c)
typefd = 1     # f-1 d-2 (default file)
typesize = 0   # (default 0)
dict = {}   # dictionary which keeps 'HashValue' : Size(of the directory or file)
dict2 = {}  # dictionary which keeps 'HashValue' :  List of Paths(of the files or directories which have the same hash
# value)
dirDict = {}  # dictionary which keeps 'Path of a directory': [Its size, Its HashValue]
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
# flags -f and -d are mutually exclusive
# -f to find duplicate files
group.add_argument("-f", "--file", help="file", action="store_true",default=False)
# -d to find duplicate directories
group.add_argument("-d", "--directory", help="directory", action="store_true", default=False)
# -c to find identical contents
parser.add_argument("-c", "--content", help="content", action="store_true", default =False)
# - n to find identical names
parser.add_argument("-n", "--name", help="name", action="store_true", default=False)
# -s to read their sizes
parser.add_argument("-s", "--size", help="size", action="store_true", default=False)
# dirs keep given directories. default is current directory.
parser.add_argument("dirs", nargs="*", default=".", type=str)
args = parser.parse_args()
if args.file:
    typefd = 1  # set file
elif args.directory:
    typefd = 2  # set directory
if args.size:
    typesize = 1  # set size=1
if args.name and args.content is False:
    type = 2  # set name
    typesize = 0  # set size=0
if args.content:
    type = 1  # set content
if args.content and args.name:
    type = 3  # set content and name


# hashes the files according to their types

def hashFile(type, path):  # type= c-1 n-2 cn-3, path is the path of file
    final1 = 0
    final2 = 0
    if type == 1 or type == 3:   # if content is set
        fp = open(path, "rb")  # read file in byte form
        content = fp.read()
        final1 = hashlib.sha256(content).hexdigest()       # hash the content
        fp.close()        # close the file
        if type == 1:   # if type is only content return the hash value
            return  final1
    if type == 2 or type == 3:  # if name is set
        name = os.path.basename(path)  # take the name of the file
        final2 = hashlib.sha256(name.encode()).hexdigest()  # hash the name
        if type == 2:  # if type is only name return hash value
            return final2
    if type == 3:    # if content and name both are set return tuple of the hash values
        final = (final1, final2)
        return final


# hashes the directories according to their types

def hashDir(type, sum, path):   # type= c-1 n-2 cn-3, sum is the hashes of files and directories inside the directory
    # path is the path of directory

    final1 = 0
    final2 = 0
    emp = ""

    if type == 1 or type == 3:  # if content is set
        content = sum  # else hash the sum
        final1 = hashlib.sha256(content.encode()).hexdigest()

        if type == 1:  # if only content is set return
            return final1
    if type == 2 or type == 3:  # if name is set
        name = os.path.basename(path)  # take name of the directory
        nameHash = hashlib.sha256(name.encode()).hexdigest()  # hash the name
        totalHash = (nameHash + sum).encode()  # hash the namehash and sum
        final2 = hashlib.sha256(totalHash).hexdigest()
        if type == 2:  # if only name is set, return value
            return final2
    if type == 3:  # if content and name are set return tuple
        final = (final1, final2)
        return final


for dir in args.dirs:  # in directories, traverse every directory
    dir = os.path.abspath(dir)  # if the directory is traversed before, do not traverse it.
    if dir in dirDict:
        continue
    for root, directories, files in os.walk(dir, topdown=False):  # traverse the directory tree bottom up
        root = os.path.abspath(root)  # take the root's full path
        currentDict = {}   # dictionary for current root which keeps 'HashValue' : Size(of the directory or file)
        currentDup = {}   # dictionary for current root which keeps 'HashValue' :  List of Paths(of the files or
        # directories which have the same hash
        for file in files:  # for every file in files
            path = os.path.join(root, file)   # take its path
            size = os.path.getsize(path)  # take its size
            hashValue = hashFile(type, path)  # find the hash of the file
            if typefd == 1:  # if we are looking for the files add hash values to the dictionaries where we keep all
                if hashValue in dict:  # if hash value is already in my dictionary
                    dict2[hashValue].append(path)  # append its path to the list of the hash value
                else:
                    dict[hashValue] = size  # else add it to the dictionaries
                    dict2[hashValue] = [path]
            if hashValue in currentDict:  # if hash value is in current dictionary
                currentDup[hashValue].append(size)  # append it to the duplicates
            else:
                currentDict[hashValue] = size  # else add it to current dictionary and duplicates.
                currentDup[hashValue] = [size]
        if typefd == 2:  # if we are looking for the directories
            for directory in directories:  # traverse all directories under the current root
                path = os.path.join(root, directory)  # take its path
                list = dirDict[path]  # take the [size,hash value] list from the directory dictionary
                size = list[0]
                hashValue = list[1]
                if hashValue in currentDict:  # if hash value in current dictionary append it to the duplicates else add
                    currentDup[hashValue].append(size)
                else:
                    currentDict[hashValue] = size
                    currentDup[hashValue] = [size]
        if typefd == 2:  # if we are looking for the directories
            currentDup = OrderedDict(sorted(currentDup.items()))
            # sort the hash values alphabetically
            newHash = ""
            newSize = 0
            if currentDup is not None:  # if the dictionary is not empty
                for hash, sizes in currentDup.items():
                    # hash takes the hash value and sizes takes the number of duplicates
                    count = len(sizes)  # number of duplicates
                    size = sizes[0]  # the size of hash
                    while count > 0:  # add the hash value and size as the number of duplicates
                        count -= 1
                        newHash += str(hash)
                        newSize += int(size)
            newHash = hashDir(type, newHash, root)  # take the hash of the directory
            if newHash in dict:  # if there is the same hash in dictionary
                dict2[newHash].append(root)  # append it
            else:
                dict[newHash] = newSize  # add it
                dict2[newHash] = [root]
            dirDict[root] = [newSize, newHash]  # add its size and hash to the directory dictionary
        else:
            dirDict[root] = [0, 0]


dicFinal = {}  # final dictionary to return paths
for hashh, duplicates in dict.items():  # traverse all hash values
    dict2[hashh].sort()  # sort the duplicates alphabetically
    size = dict[hashh]  # take their sizes
    dicFinal[hashh] = [size, dict2[hashh]]  # make a list [size, list of the duplicates] and add it to the hash value
dicFinal = OrderedDict(sorted(dicFinal.items(), key=lambda k: k[1][1][0]))
# sort final dictionary according to the first element of the list of the duplicates
if typesize == 1:  # if size flag is set sort final dictionary according to sizes in descending order
    dicFinal = OrderedDict(sorted(dicFinal.items(), key=lambda k: k[1][0], reverse=True))


# keeps the duplicate groups
groups = []
for hashval, listOf in dicFinal.items():  # traverse final dictionary
    pathlist = listOf[1]  # take the path list
    sizelist = len(pathlist)  # take the number of duplicates
    i=0
    size = str(listOf[0])  # take the size of paths
    if sizelist > 1:  # if there is duplicate
        group = ""
        for path in pathlist:
            if typesize == 1:  # if size flag is set
                if typefd == 2:  # if we are looking for directories
                    if path in dirDict:  # if the path in directory dictionary
                        group += path+ "\t"+ size+"\n"  # take its path and size add it to the current group
                else:
                    group += path+ "\t"+ size+"\n"  # else directly add it to the current group with its size
            else:  # if size flag is not set
                if typefd == 2:  # if we are looking for the directories
                    if path in dirDict:  # if path is in the directory dictionary
                        group += path+"\n"  # add path to the group
                else:
                    group += path+"\n"  # else directly add it to the group
        groups.append(group)  # append the current group to the groups

for group in groups:
    print(group)
# print every group

