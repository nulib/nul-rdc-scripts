import csv
import os

proj_number=input("What is the project number?")
proj_4dig=input("What is the four letter id?")
box_other=input('Are there boxes and folders? y for Yes and n for No')
field_names = ['Spreadsheet Row Number', 'work_image' , 'structure' , 'role' , 'work_type' , 'work_accession_number' , 'file_accession_number' , 'filename' , 'label' , 'description' , 'Capture date' , 'Staff Initials' , 'Container number ex. Box Number' , 'folder number' , 'Width (cm.)' , 'Height (cm.)' , 'Date (Year+Month+Day)' , 'project_job_number' , 'Notes about album page or photo', 'Production Notes', 'Creator' , 'Source' , 'Copyright Notice']


file_number=1
new_bOrf=0
# Whether or not there are box and folders
if box_other=='y': # will run box folder version
        box_number=input("What is the box number?")
        folder_number=input("What is the folder number?")
        box_number=str(box_number).zfill(2)
        folder_number=str(folder_number).zfill(2)
        folder_files=int(input("How many files?")) #number to loop by
        with open ('inventory.csv','a', newline='') as csvfile:
                writer=csv.DictWriter(csvfile,fieldnames=field_names)
                writer.writeheader()
                
                while file_number <= folder_files: # runs while the file number is less than or equal to the number of files that you need
                        lz_filenumber=str(file_number).zfill(4) 
                        lz_filenumber=str(lz_filenumber)
                        inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+lz_filenumber+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+lz_filenumber+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
                        file_number=int(file_number)+1
                        for data in inventory:
                                writer.writerows(inventory)

                # Below increments the row and file up by one
             
                        def ask_new_bOrf():
                                new_bOrf=input('Do you want to add - y for yes, n for no which will open the CSV ')
       
                                if new_bOrf =='y':

                                        file_number=1
                                        box_number=input("What is the box number?")
                                        folder_number=input("What is the folder number?")
                                        box_number=str(box_number).zfill(2)
                                        folder_number=str(folder_number).zfill(2)
                                        folder_files=int(input("How many files?")) #number to loop by
                                        while file_number <= folder_files: # runs while the file number is less than or equal to the number of files that you need
                                                lz_filenumber=str(file_number).zfill(4) 
                                                lz_filenumber=str(lz_filenumber)
                                                inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+lz_filenumber+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+lz_filenumber+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
                                                writer.writerows(inventory)
                                                file_number=int(file_number)+1

                                        ask_new_bOrf()
                                        
                                elif new_bOrf == 'no':
                                        os.system("start EXCEL.exe inventory.csv")
               
                ask_new_bOrf()


elif box_other=='n':  #will run choose your own adventure
    work_info=input("What is your work info ex. v for volume") #takes the place of the Box and Folder # information
    number_files=input("How many files?") # number to loop by
    

    with open ('inventory.csv','a', newline='') as csvfile:
                writer=csv.DictWriter(csvfile,fieldnames=field_names)
                writer.writeheader()
    while file_number<=number_files: # runs while the file number is less than or equal to the number of files that you need
                file_number=str(file_number).zfill(5)
                inventory=[{'Spreadsheet Row Number':row_number,'work_accession_number': proj_number+'_'+proj_4dig+'_'+work_info, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':'N/A', 'folder number':'N/A', 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]


                for data in inventory:
                        writer.writerows(inventory)
                

                # Below increments the row and file up by one
                file_number=int(file_number)+1
                row_number=row_number+1

    os.system("start EXCEL.exe inventory.csv")
else:
    print("Try again with Y for YES or N for NO")