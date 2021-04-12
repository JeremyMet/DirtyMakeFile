

import os
import re;
from shutil import copyfile;

class dirty_makefile(object):

    def __init__(self):
        self.filetree_dic = {};
        self.include_set = set();
        self.missing_set = set();

    def buildFileTree(self, path):
        list = os.listdir(path);
        file_list = [l for l in list if os.path.isfile(os.path.join(path, l))];
        folder_list = [l for l in list if os.path.isdir(os.path.join(path, l))];
        for l in file_list:
            tmp_path = os.path.join(path, l);
            self.filetree_dic[l] = tmp_path;
        for l in folder_list:
            tmp_path = os.path.join(path, l);
            self.buildFileTree(tmp_path);

    def getFileTree(self):
        return self.filetree_dic;

    def getIncludeList(self):
        return self.include_set;

    def getMissingList(self):
        return self.missing_set;

    def createLists(self, path):
        # Small Macros
        get_file = lambda x : x.split("\"")[1].split("\"")[0];
        clean_line = lambda x : x.replace(" ", "").replace("<", "\"").replace(">", "\"")[:-1];
        include_regex = re.compile("#include\".+\"", flags = re.IGNORECASE);
        new_includes = [];
        try:
            with open(path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = clean_line(line);
                    if include_regex.fullmatch(line):
                        new_includes.append(get_file(line));
        except IOError as e:
            raise Exception("IOError", "File {} does not exist".format(path));
        for include in new_includes:
            if include in self.filetree_dic:
                self.include_set.add(include);
                self.createLists(self.filetree_dic[include]);
            else:
                self.missing_set.add(include);

    def generateDirtyOutput(self, output_path):
        for include in self.include_set:
            tmp_output_path = os.path.join(output_path, include);
            copyfile(self.filetree_dic[include], tmp_output_path);


if __name__ == "__main__":
    path = "./my_folder";
    A = dirty_makefile();
    A.buildFileTree(path);
    print(A.getFileTree());
    A.createLists("./my_folder/main.c");
    print("Found Include Files: ", A.getIncludeList());
    print("Missing Include Files:", A.getMissingList());
    A.generateDirtyOutput("./OUTPUT")
