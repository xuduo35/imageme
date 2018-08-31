# [imageMe]

imageMe is a super simple image gallery server.

Think `python -m SimpleHTTPServer` for pictures.

## Manual Usage

### Step 1: Get the File `imageme.py`
### Step 2: Run imageMe

Run `python imageme.py generate` to generate imageme.html

```bash
> cd /path/to/my/pics
> python imageme.py generate
Processing .
Creating index file ./imageme.html
Processing ./photos
Creating index file ./photos/imageme.html
Processing ./photos/holiday
Creating index file ./photos/holiday/imageme.html
Processing ./photos/family
Creating index file ./photos/family/imageme.html
Processing ./super_secret_stay_out
Creating index file ./super_secret_stay_out/imageme.html
Your images are at http://127.0.0.1:8000/imageme.html
```

Run `python imageme.py port` to provide images browsing service

```bash
> cd /path/to/my/pics
> python imageme.py 8000
Your images are at http://127.0.0.1:8000/imageme.html
```

Run `python imageme.py cleanup` to clean imageme.html after usage

```bash
> cd /path/to/my/pics
> python imageme.py cleanup
Attempting to import from PIL...
Success! Enjoy your supercharged imageMe.
```

## Browse and Enjoy

Hit the URL imageMe tells you in your browser, and have fun exploring.
