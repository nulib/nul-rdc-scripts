Inventory Script

Script for creating inventories.  

Placeholder for documentation



<body>
    <div>
        <h1>Helpful Tips:</h1>
        <ul>
            <li>In order to <strong>change the number of leading zeros</strong>, find zfill and change the number within the parentheses to how many digits you want the number to have</li>
            <ul>
                <li>For example: If you have 4, but you need two zeros before the 4, you would have zfill(3) which would give you 004 </li>
            </ul>
            <li></li>
        </ul>
    </div>
    <div> 
        <h1>Key to Variables:</h1>
        <table>
            <colgroup>
                <col />
                <col />
            </colgroup>
            <tr>
            <th>Variable</th>
            <th>Meaning</th>
            </tr>
                <tr>
                    <td>proj_number</td>
                    <td>Project Number (ex. p0386)</td>
                </tr>
                <tr>
                    <td>proj_4dig</td>
                    <td>Four letter collection identifier (ex. grea -> used for Great Lakes Steamship Pamphlets</td>
                </tr>
                <tr>
                    <td>box_other</td>
                    <td>IDs whether or not you are using box/folder designation or another type</td>
                </tr>
                <tr>
                    <td>field_names, fieldnames</td>
                    <td>Gives the headers for each of the columns</td>
                </tr>
                <tr>
                    <td>row_number</td>
                    <td>Counts the rows. Is incremented by one to add a new row.</td>
                </tr>
                <tr>
                    <td>file_number</td>
                    <td>Counts the number of file that is being written into the script. Is incremented by one so that whole inventory is built out</td>
                </tr>
                <tr>
                    <td>new_bOrf</td>
                    <td>Upcoming variable that will ask whether or not you want to add a new box or folder</td>      
                </tr>
                <tr>
                    <td>box_number</td>
                    <td>Based on user input for the box currently working on</td>
                </tr>
                <tr>
                    <td>folder_number</td>
                    <td>Based on user input for the folder currently working on</td>
                </tr>
                <tr>
                    <td>
                        folder_files
                    </td>
                    <td>
                        The number of total files to write. This provides a loop for 'x' number of times
                    </td>
                </tr>
                <tr>
                    <td>
                        lz_filenumber
                    </td>
                    <td>
                        File number with leading zeros attached
                    </td>
                </tr>
                <tr>
                    <td>page_number</td>
                    <td>Counts number of pages (similar to the file_number). Increments up by one to add a new page each time the loop runs</td>
                </tr>
                <tr>
                    <td>pages_yn</td>
                    <td>Whether or not you want to add a work with page designations</td>
                </tr>
                <tr>
                    <td>pages</td>
                    <td>Based on user input for the pages currently working on. Only will show when pages_yn=y </td>
                </tr>
                <tr>
                    <td>os.system</td>
                    <td>Calls the os.system of the computer -- this is how it knows to open excel</td>
                </tr>
        </table>
    </div>
</body>

<!-- 

<tr>
    <td></td>
    <td></td>
</tr>
    
-->