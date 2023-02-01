import csv

proj_number=input("What is the project number?")
proj_4dig=input("What is the four letter id?")
box_other=input('Are there boxes and folders?')
field_names = ['Spreadsheet Row Number', 'work_image' , 'structure' , 'role' , 'work_type' , 'work_accession_number' , 'file_accession_number' , 'filename' , 'label' , 'description' , 'Capture date' , 'Staff Initials' , 'Container number ex. Box Number' , 'folder number' , 'Width (cm.)' , 'Height (cm.)' , 'Date (Year+Month+Day)' , 'project_job_number' , 'Notes about album page or photo', 'Production Notes', 'Creator' , 'Source' , 'Copyright Notice']

# Whether or not there are box and folders
if box_other=='YES': # will run box folder version
    box_number=input("What is the box number?")
    folder_number=input("What is the folder number?")
    number_files=int(input("How many files?")) #number to loop by
    row_number=0
    for x in range (1,number_files) :
        file_number= 0
        file_number=file_number+1
        file_number=str(file_number)
        row_number=row_number+1
        if x!=number_files:
            inventory=[{'Spreadsheet Row Number':row_number,'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number},]
        else:
             inventory=[{'Spreadsheet Row Number':row_number,'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number': box_number, 'folder number':folder_number, 'role':'A', 'work_type': 'IMAGE','project_job_number':proj_number}]

    print(inventory)

    with open('inventory.csv', 'w') as csvfile:
            writer=csv.DictWriter(csvfile, fieldnames = field_names)
            for data in inventory:
                writer.writerows()

elif box_other('NO'):  #will run choose your own adventure
    work_info=input("What is your work info ex. (v for volume)") #takes the place of the Box and Folder # information
    number_files=input("How many files?") # number to loop by
    
    for x in number_files():
        file_number=file_number+1
        row_number=row_number+1
        if x!=number_files:
            inventory=[{'Spreadsheet Row Number':row_number,'work_accession_number': proj_number+'_'+proj_4dig+'_'+work_info, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':'N/A', 'folder number':'N/A', 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number},]
        else: # only difference between this and the direct above is that this does not put a comma at the end of the row designation so it demonstrates that all the files have run for that work
             inventory=[{'Spreadsheet Row Number':row_number,'work_accession_number': proj_number+'_'+proj_4dig+'_'+work_info, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':'N/A', 'folder number':'N/A', 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
    with open('inventory.csv', 'w', newline='') as csvfile: # writing to csv 
            writer=csv.DictWriter(csv,fieldnames=field_names)
            writer.writeheader()
            for data in inventory:
                writer.writerows()


else:
    print("Try again with YES or NO")
