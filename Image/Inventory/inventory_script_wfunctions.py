import os
import csv



proj_number=input("What is the project number?    ")
proj_4dig=input("What is the four letter id?    ")
box_other=input('Are there boxes and folders? y for Yes and n for No')
field_names = ['Spreadsheet Row Number', 'work_image' , 'structure' , 'role' , 'work_type' , 'work_accession_number' , 'file_accession_number' , 'filename' , 'label' , 'description' , 'Capture date' , 'Staff Initials' , 'Container number ex. Box Number' , 'folder number' , 'Width (cm.)' , 'Height (cm.)' , 'Date (Year+Month+Day)' , 'project_job_number' , 'Notes about album page or photo', 'Production Notes', 'Creator' , 'Source' , 'Copyright Notice']

#defining functions

def ask_new_bOrf():
    new_bOrf=input('Do you want to add - y for yes, n for no which will open the CSV ')

    if new_bOrf =='y':

            file_number=1
            box_number=input("What is the box number?")
            folder_number=input("What is the folder number?")
            
            #Leading Zeros
            box_number=str(box_number).zfill(2)
            folder_number=str(folder_number).zfill(2)
            #Leading Zeros

            folder_files=int(input("How many files?")) #number to loop by
            while file_number <= folder_files: # runs while the file number is less than or equal to the number of files that you need

                    #Leading Zeros
                    lz_filenumber=str(file_number).zfill(4) 
                    lz_filenumber=str(lz_filenumber)
                    #Leading Zeros

                    inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+lz_filenumber+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+lz_filenumber+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
                    writer.writerows(inventory)
                    file_number=int(file_number)+1

            ask_new_bOrf()
            
    elif new_bOrf == 'n':
                new_pages=input('Do you want to add a work with more than one page - y for Yes and n for No    ')
                if new_pages =='y':
                        page_path()
                else:
                        os.system("start EXCEL.exe inventory.csv")
                        
def page_path():
    box_number=str(box_number).zfill(2)
    folder_number=str(folder_number).zfill(2)
    #Leading Zeros
    file=input('What is your file number?   ')
    pages=int(input("How many pages in the work?")) #number to loop by
    with open ('inventory.csv','a', newline='') as csvfile:
            writer=csv.DictWriter(csvfile,fieldnames=field_names)
            writer.writeheader()
            
            while page_number <= pages: # runs while the file number is less than or equal to the number of files that you need

                    #Leading Zeros
                    page_number=str(page_number).zfill(4)
                    #Leading Zeros

                    inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number +''+file+'_', 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file+'_'+page_number+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file+'_'+page_number+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
                    file_number=int(file_number)+1
                    for data in inventory:
                        writer.writerows(inventory)
                        ask_new_bOrf()


#setting variables up to be used


page_number=1
file_number=1
new_bOrf=0




if box_other=='y': # will run box folder version
        box_number=input("What is the box number?    ")
        folder_number=input("What is the folder number?   ")
        pages_yn=input("Does your folder have works with multiple pages? (ex. a letter) y for Yes and n for No    ")
        if pages_yn=='y': #Leading Zeros
                page_path()

        elif pages_yn =='n':

                #Leading Zeros
                box_number=str(box_number).zfill(2)
                folder_number=str(folder_number).zfill(2)
                #Leading Zeros

                folder_files=int(input("How many files?")) #number to loop by
                with open ('inventory.csv','a', newline='') as csvfile:
                        writer=csv.DictWriter(csvfile,fieldnames=field_names)
                        writer.writeheader()
                        
                        while file_number <= folder_files: # runs while the file number is less than or equal to the number of files that you need

                                #Leading Zeros
                                lz_filenumber=str(file_number).zfill(4) 
                                lz_filenumber=str(lz_filenumber)
                                #Leading Zeros

                                inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+lz_filenumber, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+lz_filenumber+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+lz_filenumber+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
                                file_number=int(file_number)+1
                                for data in inventory:
                                        writer.writerows(inventory)

                        # Below increments the file up by one
                                        file_number=int(file_number)+1
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
    print("Try again with y for YES or n for NO")