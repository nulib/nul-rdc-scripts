import csv
import os


proj_number=input("What is the project number?")
proj_4dig=input("What is the four letter id?")
box_other=input('Are there boxes and folders?')
field_names = ['Spreadsheet Row Number', 'work_image' , 'structure' , 'role' , 'work_type' , 'work_accession_number' , 'file_accession_number' , 'filename' , 'label' , 'description' , 'Capture date' , 'Staff Initials' , 'Container number ex. Box Number' , 'folder number' , 'Width (cm.)' , 'Height (cm.)' , 'Date (Year+Month+Day)' , 'project_job_number' , 'Notes about album page or photo', 'Production Notes', 'Creator' , 'Source' , 'Copyright Notice']


box_number=input("What is the box number?")
folder_number=input("What is the folder number?")
folder_files=int(input("How many files?")) #number to loop by
file_number=1
row_number=1


with open ('inventory.csv','a') as csvfile:
                writer=csv.DictWriter(csvfile,fieldnames=field_names)
                writer.writeheader()
                while file_number <= folder_files:
                        file_number=str(file_number)
                        inventory=[{'Spreadsheet Row Number':row_number,'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]

                        for data in inventory:
                                writer.writerows(inventory)


                        file_number=int(file_number)+1
                        row_number=row_number+1

        
        
        
    
os.system("start EXCEL.exe inventory.csv")