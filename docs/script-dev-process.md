# Infrastructure for Python Script Development

## Documentation and script management 

All documentation will be on the Git repository and referenced on Sharepoint. 

Documentation will include: 

- Style guideline 

- List of all scripts, their names and functions, list of users 

- Development meeting notes and decisions 

- Tests for scripts

## Development Cycles 
Changes, updates and modifications of scripts will take place from Fall thru Spring quarters 
Summer quarter should be relatively quiet and used for reviewing scripts and thinking about modifications/planning.  
 
## Staging/Production Areas 
  
Production scripts should be on Github and clearly identified as the official versions 
A folder named “Staging” should be used for all scripts that are in development/testing 

## Versioning

Versioning should follow the semantic versioning format (ex. 1.4.10) where numbers correspond to major update, minor update, and patch (left to right).

## Development Process

**Major update**: adds new functionality and breaks old functionality  
**Minor update**: adds new functionality without breaking old functionality  
**Patch**: no new functionality, just a fix or small change  

### Minor and Major Updates

1. Create a new branch with the name of the prerelease version.
    - preminor example : 8.4.1 -> 8.5.0a0
    - premajor example: 8.4.1 -> 9.0.0a0
2. Update the poetry project version with `poetry version preminor`, `poetry version premajor`, or `poetry version prerelease`
3. Merge work into prerelease branch.
    - Note: it may be helpful to move to break up the update into multiple prereleases as work is done.
    - example: 8.5.0a0 -> 8.5.0a1
4. Proceed with testing when ready.
    - If testing fails, go back to step 3 and work on fixes.
5. When testing passes, create a pull request into main and merge when reviews pass.

### Patches
Note: This section is only relevant if no prerelease is currently being worked on.

1. Create a new branch with the name of the patch. Be consise and descriptive, use all lowercase, no special characters except dashes
    - patch example : 8.4.1 -> 8.4.2
2. Update the version in this branch with `poetry version patch`
3. Merge work into patch branch.
4. Proceed with testing when ready.
    - If testing fails, go back to step 3 and work on fixes.
5. When testing passes, create a pull request into main and merge when reviews pass.

### Testing

The development process should involve two types of review: 

1. Review by another person doing scripting 

2. Testing and trial use by a stakeholder (someone who uses the script) 
 
## Feature/Bug reports  

A link will be provided to issue reporting in Github to provide a method for reporting bugs or feature requests. 
The reporter will rank the bug or feature request.  High priority bugs and feature requests will prompt immediate discussion. Lower priority bugs and feature requests will be reviewed at the start of each quarter.  
 
