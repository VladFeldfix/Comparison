# Download SmartConsole.py from: https://github.com/VladFeldfix/Smart-Console/blob/main/SmartConsole.py
from SmartConsole import *
import os
import difflib
from datetime import datetime

class main:
    # constructor
    def __init__(self):
        # load smart console
        self.ver = "1.0"
        self.sc = SmartConsole("Comparison",self.ver)

        # set-up main memu
        self.sc.add_main_menu_item("RUN", self.run)

        # get settings
        self.path_folder1 = self.sc.get_setting("Folder 1")
        self.path_folder2 = self.sc.get_setting("Folder 2")
        self.path_output = self.sc.get_setting("Output")

        # display main menu
        self.sc.start()

    def run(self):
        # test paths
        self.sc.test_path(self.path_output)

        # get folder 1
        self.path_folder1 = self.sc.input("Insert folder 1 [Default: "+self.path_folder1+"]") or self.path_folder1
        # get folder 2
        self.path_folder2 = self.sc.input("Insert folder 2 [Default: "+self.path_folder2+"]") or self.path_folder2

        self.sc.test_path(self.path_folder1)
        self.sc.test_path(self.path_folder2)

        self.save(self.path_folder1)
        self.save(self.path_folder2)


        # run comparison between files
        start_time = datetime.now()
        start = start_time.strftime('%Y-%m-%d %H:%M:%S')
        self.started = start
        self.sc.print(f"Start: {start}")
        self.compare_folders(self.path_folder1, self.path_folder2)
        file_path = os.path.join(self.path_output, self.output_file)
        os.startfile(file_path)
        # End of the script
        end_time = datetime.now()
        self.sc.print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # restart
        self.sc.restart()

    def compare_folders(self, folder1, folder2):
        # Create sets to store file paths
        files1 = {}
        files2 = {}
        self.output_file = self.sc.today()+self.sc.right_now()+".html"
        self.output_file = self.output_file.replace(":","").replace("-","").replace(" ","")

        # Walk through folder1 and include subdirectories
        for root, _, files in os.walk(folder1):
            for file in files:
                # Create a relative path for comparison
                relative_path = os.path.relpath(os.path.join(root, file), folder1)
                files1[relative_path] = os.path.join(root, file)

        # Walk through folder2 and include subdirectories
        for root, _, files in os.walk(folder2):
            for file in files:
                # Create a relative path for comparison
                relative_path = os.path.relpath(os.path.join(root, file), folder2)
                files2[relative_path] = os.path.join(root, file)

        # Get common files based on relative paths
        common_files = set(files1.keys()).intersection(set(files2.keys()))
        
        compare_results = []

        for relative_filename in common_files:
            file1_path = files1[relative_filename]
            file2_path = files2[relative_filename]
            
            if os.path.isfile(file1_path) and os.path.isfile(file2_path):
                diff = self.compare_files(file1_path, file2_path)
                if diff is not None:  # Only add if there are differences
                    compare_results.append((relative_filename, diff))
            else:
                self.sc.print(f"Skipping {relative_filename}: one of them is not a file.")

        if compare_results:  # Only generate the report if there are differences found
            self.generate_html_log(compare_results, True)
        else:
            self.sc.warning("No differences were found between the compared files.")
            self.generate_html_log(compare_results, False)

    def compare_files(self, file1, file2):
        try:
            with open(file1, 'r') as f1, open(file2, 'r') as f2:
                f1_lines = f1.readlines()
                f2_lines = f2.readlines()
        except PermissionError as e:
            self.sc.error(f"PermissionError: {e}. Unable to open {file1} or {file2}.")
            return None  # Return None if failed to read files
        except Exception as e:
            self.sc.error(f"Failed to read files {file1} and {file2}: {e}")
            return None  # Return None if exception occurs
        
        d = difflib.Differ()
        diff = list(d.compare(f1_lines, f2_lines))
        
        # Check if there are any differences
        if any(line.startswith('- ') or line.startswith('+ ') for line in diff):
            return diff
        else:
            return None  # No differences found

    def generate_html_log(self, compare_results, there_are_differences):
        same_files, different_files = self.same_diff()
        with open(self.path_output+"/"+self.output_file, 'w', encoding='utf-8') as f:
            f.write('<html><head><style> .diff_add { background-color: #d4fcdc; } .diff_sub { background-color: #f8d7da; } </style></head><body>')
            f.write('<h1>Comparison test results</h1>')
            f.write('<p>Comparison software version: '+self.ver+'</p>')
            f.write('<p>Date: '+self.started+'</p>')
            f.write('<p>Folder 1: '+self.path_folder1+'</p>')
            f.write('<p>Folder 2: '+self.path_folder2+'</p>')
            if there_are_differences:
                for filename, diff in compare_results:
                    f.write(f'<h2>Comparing: {filename}</h2><table border="1"><tr><th>File 1</th><th>File 2</th></tr>')
                    for result in diff:
                        # Ignore empty lines
                        if result.strip():  # Only process non-empty lines
                            f.write('<tr>')
                            if result.startswith('- '):
                                f.write(f'<td class="diff_sub">{result[2:].strip()}</td><td></td>')
                            elif result.startswith('+ '):
                                f.write(f'<td></td><td class="diff_add">{result[2:].strip()}</td>')
                            else:
                                line = result[2:].strip()
                                f.write(f'<td>{line}</td><td>{line}</td>')
                            f.write('</tr>')
                f.write('</table><br/>')
            else:
                f.write('<p><b> - No differences have been detected! - </b></p>')
            
            f.write('<p><u>Both folders have:</u></p>')
            f.write('<ol>')
            for file in same_files:
                f.write('<li>'+file+'</il>')
            f.write('</ol>')
            
            f.write('<p><u>Only one folder have:</u></p>')
            f.write('<ol>')
            for file in different_files:
                f.write('<li>'+file+'</il>')
            f.write('</ol>')
            f.write('</body></html>')
    
    def get_all_files(self, folder):
        """Return a set of files (with their names) in the given folder and its subfolders."""
        files = set()
        for dirpath, _, filenames in os.walk(folder):
            for file in filenames:
                files.add(file)
        return files
    
    def same_diff(self):
        # Get all file names in both folders (including subfolders)
        files1 = self.get_all_files(self.path_folder1)
        files2 = self.get_all_files(self.path_folder2)
        
        # List of same name files (only names)
        same_name_files = list(files1.intersection(files2))
        
        # List of different name files with full paths
        different_name_files = []

        for file in files1.difference(files2):
            different_name_files.append(os.path.join(self.path_folder1, file))
            
        for file in files2.difference(files1):
            different_name_files.append(os.path.join(self.path_folder2, file))
        
        return same_name_files, different_name_files

    def save(self, path):
        file = open("settings.txt", 'w', encoding='utf-8')
        file.write("Folder 1 > "+self.path_folder1+"\n")
        file.write("Folder 2 > "+self.path_folder2+"\n")
        file.write("Output > "+self.path_output+"\n")
        file.close()
main()