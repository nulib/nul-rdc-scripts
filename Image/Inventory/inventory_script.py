import csv
import os

proj_number=input("What is the project number?")
proj_4dig=input("What is the four letter id?")
box_other=input('Are there boxes and folders? Y for Yes and N for No')
field_names = ['Spreadsheet Row Number', 'work_image' , 'structure' , 'role' , 'work_type' , 'work_accession_number' , 'file_accession_number' , 'filename' , 'label' , 'description' , 'Capture date' , 'Staff Initials' , 'Container number ex. Box Number' , 'folder number' , 'Width (cm.)' , 'Height (cm.)' , 'Date (Year+Month+Day)' , 'project_job_number' , 'Notes about album page or photo', 'Production Notes', 'Creator' , 'Source' , 'Copyright Notice']
row_number=1
file_number=1

# Whether or not there are box and folders
if box_other=='Y': # will run box folder version
    box_number=input("What is the box number?")
    folder_number=input("What is the folder number?")
    folder_files=int(input("How many files?")) #number to loop by
    
    with open ('inventory.csv','a') as csvfile:
                writer=csv.DictWriter(csvfile,fieldnames=field_names)
                writer.writeheader()
                while file_number <= folder_files: # runs while the file number is less than or equal to the number of files that you need
                        file_number=str(file_number) 
                        inventory=[{'Spreadsheet Row Number':row_number,'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]

                        for data in inventory:
                                writer.writerows(inventory)

                        # Below increments the row and file up by one
                        file_number=int(file_number)+1
                        row_number=row_number+1
    os.system("start EXCEL.exe inventory.csv")

elif box_other=='N':  #will run choose your own adventure
    work_info=input("What is your work info ex. (v for volume)") #takes the place of the Box and Folder # information
    number_files=input("How many files?") # number to loop by
    

    with open ('inventory.csv','a') as csvfile:
                writer=csv.DictWriter(csvfile,fieldnames=field_names)
                writer.writeheader()
    while file_number<=number_files: # runs while the file number is less than or equal to the number of files that you need
            inventory=[{'Spreadsheet Row Number':row_number,'work_accession_number': proj_number+'_'+proj_4dig+'_'+work_info, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':'N/A', 'folder number':'N/A', 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
        

            for data in inventory:
                writer.writerows(inventory)
            

            # Below increments the row and file up by one
            file_number=int(file_number)+1
            row_number=row_number+1

    os.system("start EXCEL.exe inventory.csv")
else:
    print("Try again with Y for YES or N for NO")
