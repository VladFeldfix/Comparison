# Download SmartConsole.py from: https://github.com/VladFeldfix/Smart-Console/blob/main/SmartConsole.py
from SmartConsole import *

class main:
    # constructor
    def __init__(self):
        # load smart console
        self.ver = "2.0"
        self.sc = SmartConsole("Comparison",self.ver)

        # set-up main memu
        self.sc.add_main_menu_item("RUN", self.run)

        # get settings
        self.path_folder1 = self.sc.get_setting("Folder 1")
        self.path_folder2 = self.sc.get_setting("Folder 2")
        self.path_output = self.sc.get_setting("Output")
        self.formats = self.sc.get_setting("Formats").split(",")

        # display main menu
        self.sc.start()

    
    def run(self):
        # test output path
        self.sc.test_path(self.path_output)

        # get folder 1
        self.path_folder1 = self.sc.input("Insert folder 1 [Default: "+self.path_folder1+"]") or self.path_folder1
        self.sc.test_path(self.path_folder1)

        # get folder 2
        self.path_folder2 = self.sc.input("Insert folder 2 [Default: "+self.path_folder2+"]") or self.path_folder2
        self.sc.test_path(self.path_folder2)
        self.save()

        # start
        self.strat_timestamp = self.sc.today()+" "+self.sc.now()
        self.sc.print("START: "+self.strat_timestamp)
        self.compare()
        self.generate_html()

        # end
        end_timestamp = self.sc.today()+" "+self.sc.now()
        self.sc.print("END: "+end_timestamp)

        # restart
        self.sc.restart()
    
    def compare(self):
        # get all files from folder 1
        self.folder1 = {} # filename: location
        self.folder1_keys = [] # filename, filename, filename, ...
        for root, folders, files in os.walk(self.path_folder1):
            for file in files:
                file_format = file.split(".")
                if len(file_format) > 1:
                    file_format = file_format[1]
                else:
                    file_format = ".file"
                if file_format in self.formats:
                    if not file in self.folder1:
                        self.folder1[file] = root
                        self.folder1_keys.append(file)
                    else:
                        choice = self.sc.choose("Which file would you like to add to the comparison list?",(root+"/"+file, self.folder1[file]+"/"+file))
                        if choice == root+"/"+file:
                            self.folder1[file] = root

        # get all files from folder 2
        self.folder2 = {} # filename: location
        self.folder2_keys = [] # filename, filename, filename, ...
        for root, folders, files in os.walk(self.path_folder2):
            for file in files:
                file_format = file.split(".")
                if len(file_format) > 1:
                    file_format = file_format[1]
                else:
                    file_format = ".file"
                if file_format in self.formats:
                    if not file in self.folder2:
                        self.folder2[file] = root
                        self.folder2_keys.append(file)
                    else:
                        if file in self.folder1:
                            choice = self.sc.choose("Which file would you like to add to the comparison list?",(root+"/"+file, self.folder2[file]+"/"+file))
                            if choice == root+"/"+file:
                                self.folder2[file] = root
        
        # get a list of unique files
        self.unique_files = self.diff(self.folder1_keys,self.folder2_keys)

        # get a list of similar files for comparison
        self.similars = self.intersection(self.folder1_keys,self.folder2_keys)

        # go over each file in similar files and compare the two
        self.comparison_log = {} # file: [ [in folder1] , [in folder2] ]
        self.faild = []

        for file in self.similars:
            compare = True
            # get file 1
            try:
                f1 = open(self.folder1[file]+"/"+file, "r", encoding='utf-8')
                f1_lines = f1.readlines()
                f1.close()
            except:
                self.sc.error("Cannot read file: "+self.folder1[file]+"/"+file)
                compare = False
                self.faild.append(self.folder1[file]+"/"+file)
            
            # get file 2
            try:
                f2 = open(self.folder2[file]+"/"+file, "r", encoding='utf-8')
                f2_lines = f2.readlines()
                f2.close()
            except:
                self.sc.error("Cannot read file: "+self.folder2[file]+"/"+file)
                compare = False
                self.faild.append(self.folder2[file]+"/"+file)
            
            # compare files
            if compare:
                compare_results = self.compare_files(f1_lines, f2_lines)
                if len(compare_results[0]) > 0:
                    self.comparison_log[file] = compare_results
    
    def diff(self, list1, list2):
        return list(set(list1).symmetric_difference(set(list2)))

    def intersection(self, list1, list2):
        return list(set(list1).intersection(set(list2)))

    def compare_files(self, list1, list2):
        diff = self.diff(list1, list2)
        result = [[],[]]
        if len(diff) > 0:
            i = 0
            while i < max(len(list1), len(list2)):
                Aerror = False
                Berror = False
                if i > len(list1)-1:
                    a = " "
                else:
                    a = list1[i]
                if i > len(list2)-1:
                    b = " "
                else:
                    b = list2[i]
                if a != b:
                    if len(list1) < len(list2):
                        list1.insert(i, " ")
                        a = list1[i]
                        Berror = True
                    else:
                        list2.insert(i, " ")
                        b = list2[i]
                        Aerror = True
                add = False
                if len(a) > 0 and a != " " and a != "" and a !="\n":
                    add = True
                if len(b) > 0 and b != " " and b != "" and b !="\n":
                    add = True
                if add:
                    result[0].append((a,Aerror))
                    result[1].append((b,Berror))
                i += 1
        return result

    def generate_html(self):
        html_filename = self.strat_timestamp.replace(" ","").replace(":","").replace("-","")
        html = self.path_output+"/"+html_filename+".html"
        f = open(html, 'w', encoding='utf-8')
        f.write('<html>\n')
        f.write('    <head>\n')
        f.write('        <style>\n')
        f.write('            table, tr, td, th{\n')
        f.write('                border: 1px solid black;\n')
        f.write('                border-collapse: collapse;\n')
        f.write('            }\n')
        f.write('            .red{\n')
        f.write('                background-color: red;\n')
        f.write('                color: white;\n')
        f.write('            }\n')
        f.write('        </style>\n')
        f.write('    </head>\n')
        f.write('    <body>\n')
        f.write('        <h1>Comparison test results</h1>\n')
        f.write('        <p>Comparison software version: '+self.ver+'</p>\n')
        f.write('        <p>Date: '+self.strat_timestamp+'</p>\n')
        f.write('        <p>Folder 1: '+self.path_folder1+' ('+str(len(self.folder1_keys))+' files tested)</p>\n')
        f.write('        <p>Folder 2: '+self.path_folder2+' ('+str(len(self.folder2_keys))+' files tested)</p>\n')
        f.write('        <p>Tested formats: '+','.join(self.formats)+'\n')
        if len(self.comparison_log) == 0:
            f.write('        <p><b> - NO DIFFERENCES HAVE BEEN FOUND! - </b></p>\n')
        else:
            f.write('        <h2>Found differences in ('+str(len(self.comparison_log))+') files:</h2>\n')
            for file, log in self.comparison_log.items():
                f.write('        <p><b>'+file+':</b></p>\n')
                f.write('        <table>\n')
                f.write('            <tr>\n')
                f.write('                <th>'+self.folder1[file]+'/'+file+'</th>\n')
                f.write('                <th>'+self.folder2[file]+'/'+file+'</th>\n')
                f.write('            </tr>\n')
                i = 0
                while i < len(log[0]):
                    f.write('            <tr>\n')
                    Aerror = ""
                    if log[0][i][1]:
                        Aerror = ' class = "red"'
                    Berror = ""
                    if log[1][i][1]:
                        Berror = ' class = "red"'
                    f.write('                <td'+Aerror+'>'+log[0][i][0].replace("<","&lt;").replace(">","&gt;").replace(" ","&nbsp;")+'</td>\n')
                    f.write('                <td'+Berror+'>'+log[1][i][0].replace("<","&lt;").replace(">","&gt;").replace(" ","&nbsp;")+'</td>\n')
                    f.write('            </tr>\n')
                    i += 1
                f.write('        </table>\n')
        
        # Both folders have
        f.write('        <p>Both folders have ('+str(len(self.similars))+' files):</p>\n')
        f.write('        <ol>\n')
        for file in self.similars:
            f.write('            <li>'+file+'</li>\n')
        f.write('        </ol>\n')
        
        # Only one folder have 
        f.write('        <p>Only one folder have ('+str(len(self.unique_files))+' files):</p>\n')
        f.write('        <ol>\n')
        for file in self.unique_files:
            path = ""
            if file in self.folder1:
                path = self.folder1[file]+"/"+file
            else:
                path = self.folder2[file]+"/"+file
            f.write('            <li>'+path+'</li>\n')
        f.write('        </ol>\n')
        
        # Failed to read
        f.write('        <p>Failed to read ('+str(len(self.faild))+' files):</p>\n')
        f.write('        <ol>\n')
        for file in self.faild:
            f.write('            <li>'+file+'</li>\n')
        f.write('        </ol>\n')

        f.write('    </body>\n')
        f.write('</html>\n')
        os.startfile(html)

    def save(self):
        file = open("settings.txt", 'w', encoding='utf-8')
        file.write("Folder 1 > "+self.path_folder1+"\n")
        file.write("Folder 2 > "+self.path_folder2+"\n")
        file.write("Output > "+self.path_output+"\n")
        file.write("Formats > "+','.join(self.formats)+"\n")
        file.close()

main()