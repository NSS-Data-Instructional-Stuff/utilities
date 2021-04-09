## DC

Basic CLI for creating DataCamp reports (best used for classroom settings).

### Some pre-requisites
You need an email, password, and org to run these scripts.
Some things, you can set ahead of time.

```bash
export DATACAMP_ORG_NAME=new-nss-data-analytics-cohort-2
export DATACAMP_EMAIL=<your email>
```

We'll safely ask you for the password in the CLI.

You will need python3 to run this.

You will also need chromedriver. 
You can install it from [here](https://chromedriver.chromium.org/downloads).
Check which version of chrome you are using, and download the relative version. 

Then, move it somewhere your path can see it. 
```bash
mv ~/Downloads/<chromedriver> /usr/local/bin
```
That is just an example. May need to restart your terminal

### Installation
From your terminal of choice..
```bash
python3.7 -m pip install --user -e .
```

### Running

Okeedoke, now we can use it.
The basic is:

```bash
dc-reports
```

For help on how to run it.. 
```bash
dc-reports -h
```

To specify an output directory
```bash
dc-reports --out ./data
```

To specify a DC org
```bash
dc-reports --org-name <org>
```
**NOTE**:
This org name has to be the computer-based org.. 
So, the value you find in the url if you go to the org page.
Not the literal name of the org.

And finally, if you want to see Chrome running..
```bash
dc-reports --show
```

