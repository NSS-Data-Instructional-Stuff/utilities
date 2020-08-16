### [slackcleaner](https://github.com/sgratzl/slack_cleaner2) deletes files and messages from a slack channel to which you have rights

#### To install the slackcleaner package:  

`pip install slack-cleaner2`


#### To create a token:  

1. From the Slack app, go to `Settings & administration` --> `Manage apps`
2. From the top menu, select `Build`
3. Choose `Create New App` and give it a name
4. Select `Oauth & Permissions` from the sidebar menu
5. Scroll down to `User Token Scope` and select the following:
    - users:read
    - channels:read
    - channels:history
    - chat:write

6. `Install App to Workspace` review permissions and then `Authorize`