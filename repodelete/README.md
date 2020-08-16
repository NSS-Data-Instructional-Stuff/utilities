### This utility does a bulk delete of repositories in a Github organization

To use it you must 
 - have rights to the organization you're cleaning up  
 - create a [Personal Access Token](https://github.com/settings/tokens/new) in your github account with  `delete_repo` and `public_repo` scopes
 - create a `config.ini` file which will remain in your local copy of this repository by adding your token to `config.ini.example` and removing `.example` from the file name 

When you run the repodelete.py script, you will be presented with a list of repos to delete and given the option to omit one or more from the deletion.