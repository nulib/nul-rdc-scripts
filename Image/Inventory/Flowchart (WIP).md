```mermaid
---
title: Initial Questions
---
flowchart TD
    A[What is your project name? <br> What is your project four letter id? <br> Does your work have boxes and folders?]
    B[Yes]
    C[No]
    A-->B 
    A-->C
    D[What is the box number? <br> What is the folder number? <br> What is the number of files?]

    B---D
    E[Fills out <br> work_accession_number, file_accession_number, <br> filename, proj-number, Container, and Folder columns]
    D-->E
    F[Do you want to add a box or folder?]
    G[Yes - Runs from box question]
    H[No]
    E-->F
    F-->G
    F-->H
    I[Do you want to add a work with page designations?]
    H-->I
    J[Yes]
    K[No - terminates script opens CSV]
    I-->J
    I-->K

