import os
import csv


#Asking the user questions to decide the workflow that is going to be used by the script
proj_number=input("What is the project number?    ")
proj_4dig=input("What is the four letter id?    ")
box_other=input('Are there boxes and folders? y for Yes and n for No     ')

#Building some of the intial variables that will be used
field_names = ['Spreadsheet Row Number', 'work_image' , 'structure' , 'role' , 'work_type' , 'work_accession_number' , 'file_accession_number' , 'filename' , 'label' , 'description' , 'Capture date' , 'Staff Initials' , 'Container number ex. Box Number' , 'folder number' , 'Width (cm.)' , 'Height (cm.)' , 'Date (Year+Month+Day)' , 'project_job_number' , 'Notes about album page or photo', 'Production Notes', 'Creator' , 'Source' , 'Copyright Notice']
file_path=input("Where do you want to save to?   ")
csv_name=proj_number+'_'+proj_4dig+'_'+'inventory'+'.csv' #assigning the CSV file a name based on the data that the user input
open_CSV='"'+'start EXCEL.exe'+' '+csv_name+'"' #Part of the command to open the CSV file in Excel -- you can swap ' EXCEL.exe' for your preferred CSV editor that is installed on your PC

#defining functions
def save_CSV():
        os.path.join(file_path, open_CSV) #writes the CSV file to the user specified save location

def ask_new_work_bOrf():
        new_work=input('Do you want to add a new work - y for yes, n for no which will open the CSV   ')

        if new_work =='y': #if you want a new work this will run
                file_number=1
                work_info=input("What is the work info?    ")
                number_files=int(input("How many files?   ")) #number to loop by
                while file_number<=number_files: # runs while the file number is less than or equal to the number of files that you need

                        #Leading Zeros
                        file_number=str(file_number).zfill(5)
                        #Leading Zeros
                        
                        #Combines the information that the user has put in to fill out select fields in the CSV file
                        inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+work_info, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'a'+'.tif', 'Container number ex. Box Number':'N/A', 'folder number':'N/A', 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
                        for data in inventory:
                                writer.writerows(inventory)
                                # Below increments the row and file up by one
                                file_number=int(file_number)+1

                                ask_new_work_bOrf()

        elif new_work=='n':
                        save_CSV() #command to save the CSV
                        os.system(open_CSV) #Command to open the CSV in Excel

def ask_new_work_choose():
        new_work=input('Do you want to add a new work - y for yes, n for no which will open the CSV   ')

        if new_work =='y': #if you want a new work this will run
                file_number=1
                work_info=input("What is the work info?    ")
                number_files=int(input("How many files?   ")) #number to loop by
                while file_number<=number_files: # runs while the file number is less than or equal to the number of files that you need


                        #Leading Zeros
                        file_number=str(file_number).zfill(5)
                        #Leading Zeros

                        #Combines the information that the user has put in to fill out select fields in the CSV file
                        inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+work_info, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'a'+'.tif', 'Container number ex. Box Number':'N/A', 'folder number':'N/A', 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
                        for data in inventory:
                                writer.writerows(inventory)
                                # Below increments the row and file up by one
                                file_number=int(file_number)+1

                ask_new_work_choose()
        elif new_work=='n':
                save_CSV() #Saves the CSV File
                os.system(open_CSV) #Opens the CSV file in Excel



def ask_new_bOrf(): #function that will ask if you want to add a box or folder. If you want to add pages, answer 'n' to the question and then 'y' to the following question
        new_bOrf=input('Do you want to add - y for yes, n for no (which will ask about if you want to add a work with page designation) ')

        if new_bOrf =='y': #if you want a new box or folder this will run

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
                    file_number=str(file_number).zfill(4) 
                    #Leading Zeros

                    inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
                    for data in inventory:
                        writer.writerows(inventory)
                        file_number=int(file_number)+1

            ask_new_bOrf()
            
        elif new_bOrf == 'n': #if you do not want to run a new box or folder
                new_pages=input('Do you want to add a work with more than one page - y for Yes and n for No    ') #will ask if you want to add a work that has to have page designation
                if new_pages =='y': #if you want to use page designation this will run
                        page_path()
                elif new_pages=='n': 
                        save_CSV() #Saves the CSV
                        os.system(open_CSV) #Opens the CSV in Excel
                        
def page_path(): #This script runs when you want to add works with page designations
        page_number=1
        box_number=input("What is the box number?    ")
        folder_number=input("What is the folder number?   ")
        
    #Leading Zeros    
        box_number=str(box_number).zfill(3)
        folder_number=str(folder_number).zfill(2)
    #Leading Zeros


        file=input('What is your file number?   ')
        pages=int(input("How many pages in the work?")) #number to loop by
            
        while page_number <= pages: # runs while the file number is less than or equal to the number of files that you need

                    #Leading Zeros
                    page_number=str(page_number).zfill(4)
                    file=str(file).zfill(2)
                    #Leading Zeros

                    inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number +'_'+file+'_', 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file+'_'+page_number+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file+'_'+page_number+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]

                    for data in inventory:
                        writer.writerows(inventory)
                        page_number=int(page_number)+1
        ask_new_bOrf() #will then call the ask_new_bOrf function to see if you want to add a box or folder next. If you want to run another work with page designations, answer 'n' to the first question and the 'y' to the next
                        

#setting variables up to be used


page_number=1
file_number=1
new_bOrf=0




if box_other=='y': # will run box folder version
        pages_yn=input("Does your folder have works with multiple pages? (ex. a letter) y for Yes and n for No    ")
        if pages_yn=='y': #runs if you need to designate page numbers
                with open (csv_name,'a', newline='', encoding='utf-8') as csvfile:
                        writer=csv.DictWriter(csvfile,fieldnames=field_names)
                        writer.writeheader()
                        page_path()

        elif pages_yn =='n':
                box_number=input("What is the box number?    ")
                folder_number=input("What is the folder number?   ")
                
                #Leading Zeros
                box_number=str(box_number).zfill(2)
                folder_number=str(folder_number).zfill(2)
                #Leading Zeros

                folder_files=int(input("How many files?      ")) #number to loop by
                with open (csv_name,'a', newline='', encoding='utf-8') as csvfile:
                        writer=csv.DictWriter(csvfile,fieldnames=field_names)
                        writer.writeheader()
                        
                        while file_number <= folder_files: # runs while the file number is less than or equal to the number of files that you need

                                #Leading Zeros
                                file_number=str(file_number).zfill(4) 
                                #Leading Zeros

                                inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+lz_filenumber, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+'b'+box_number+'_'+'f'+folder_number+'_'+file_number+'_'+'01'+'_'+'a'+'.tif', 'Container number ex. Box Number':box_number, 'folder number':folder_number, 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]

                                for data in inventory:
                                        writer.writerows(inventory)

                        # Below increments the file up by one
                                        file_number=int(file_number)+1
                        ask_new_bOrf()
                                                
                                


elif box_other=='n':  #will run choose your own adventure
    work_info=input("What is your work info ex. v for volume?    ") #takes the place of the Box and Folder # information
    number_files=int(input("How many files?      ")) # number to loop by
    

    with open (csv_name,'a', newline='', encoding='utf-8') as csvfile:
                writer=csv.DictWriter(csvfile,fieldnames=field_names)
                writer.writeheader()
                while file_number <= number_files: # runs while the file number is less than or equal to the number of files that you need

                              #leading zeros
                        file_number=str(file_number).zfill(5)
                                #leading zeros

                        inventory=[{'work_accession_number': proj_number+'_'+proj_4dig+'_'+work_info, 'file_accession_number':proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'a', 'filename': proj_number+'_'+proj_4dig+'_'+work_info+'_'+file_number+'_'+'a'+'.tif', 'Container number ex. Box Number':'N/A', 'folder number':'N/A', 'role':'A', 'work_type':'IMAGE','project_job_number':proj_number}]
                        for data in inventory:
                                writer.writerows(inventory)
                                # Below increments the row and file up by one
                                file_number=int(file_number)+1

                ask_new_work_choose()
        
else:
    print("Try again running the script again with y for YES or n for NO")
