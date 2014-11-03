#!/usr/bin/python
"""
imageMe is a super simple image gallery server.

Run imageme.py from the top level of an image directory so generate gallery
index HTML and run a SimpleHTTPServer on the localhost.

Imported as a module, use serve_dir(your_path) to do the same for any directory
programmatically.
"""

# Dependencies
import os, re, sys, SimpleHTTPServer, SocketServer

# Constants / configuration
## Filename of the generated index files
INDEX_FILE_NAME = 'imageme.html'
## Regex for matching only image files
IMAGE_FILE_REGEX = '^.+\.(png|jpg|jpeg|tif|tiff|gif|bmp)$'
## Images per row of the gallery tables
IMAGES_PER_ROW = 3

def _create_index_file(root_dir, location, image_files, dirs):
    """
    Create an index file in the given location, supplying known lists of
    present image files and subdirectories.

    @param {String} root_dir - The root directory of the entire crawl. Used to
        ascertain whether the given location is the top level.

    @param {String} location - The current directory of the crawl. The index
        file will be created here.

    @param {[String]} image_files - A list of image file names in the location.
        These will be displayed in the index file's gallery.

    @param {[String]} dirs - The subdirectories of the location directory.
        These will be displayed as links further down the file structure.

    @return {String} The full path (location plus filename) of the newly
        created index file. Intended for usage cleaning up created files.
    """
    # Put together HTML as a list of the lines we'll want to include
    # Issue #2 exists to do this better than HTML in-code
    header_text = \
        'imageMe: ' + location + ' [' + str(len(image_files)) + ' image(s)]'
    html = [
        '<!DOCTYPE html>',
        '<html>',
        '    <head>',
        '        <title>imageMe</title>'
        '        <style>',
        '            html, body {margin: 0;padding: 0;}',
        '            .header {text-align: right;}',
        '            .content {',
        '                padding: 3em;',
        '                padding-left: 4em;',
        '                padding-right: 4em;',
        '            }',
        '            .image {max-width: 100%; border-radius: 0.3em;}',
        '            td {width: ' + str(100.0 / IMAGES_PER_ROW) + '%;}',
        '        </style>',
        '    </head>',
        '    <body>',
        '    <div class="content">',
        '        <h2 class="header">' + header_text + '</h2>',
        '        <hr>'
    ]
    # Populate the present subdirectories - this includes '..' unless we're at
    # the top level
    directories = []
    if root_dir != location:
        directories = ['..']
    directories += dirs
    # For each subdirectory, include a link to its index file
    for directory in directories:
        link = directory + '/' + INDEX_FILE_NAME
        html += [
            '    <h3 class="header">',
            '    <a href="' + link + '">' + directory + '</a>',
            '    </h3>'
        ]
    # Populate the image gallery table
    # Counter to cycle down through table rows
    table_row_count = 1
    html += ['<hr>', '<table>']
    # For each image file, potentially create a new <tr> and create a new <td>
    for image_file in image_files:
        if table_row_count == 1:
            html.append('<tr>')
        html += [
            '    <td>',
            '    <a href="' + image_file + '">',
            '        <img class="image" src="' + image_file + '">',
            '    </a>',
            '    </td>'
        ]
        if table_row_count == IMAGES_PER_ROW:
            table_row_count = 0
            html.append('</tr>')
        table_row_count += 1
    html += ['</tr>', '</table>']
    html += [
        '    </div>',
        '    </body>',
        '</html>'
    ]
    # Actually create the file, now we've put together the HTML content
    index_file_path = _get_index_file_path(location)
    print('Creating index file %s' % index_file_path)
    index_file = open(index_file_path, 'w')
    index_file.write('\n'.join(html))
    index_file.close()
    # Return the path for cleaning up later
    return index_file_path

def _get_index_file_path(location):
    """
    Get the full file path to be used for an index file in the given location.
    Yields location plus the constant INDEX_FILE_NAME.

    @param {String} location - A directory location in which we want to create
        a new index file.

    @return {String} A file path for usage with a new index file.
    """
    return os.path.join(location, INDEX_FILE_NAME)

def _get_server_port():
    """
    Get the port specified for the server to run on. If given as the first
    command line argument, we'll use that. Else we'll default to 8000.

    @return {Integer} The port to run the server on. Default 8000, overridden
        by first command line argument.
    """
    return int(sys.argv[1]) if len(sys.argv) >= 2 else 8000

def clean_up(paths):
    """
    Clean up after ourselves, removing created files.

    @param {[String]} A list of file paths specifying the files we've created
        during run. Will all be deleted.

    @return {None}
    """
    print('Cleaning up')
    # Iterate over the given paths, unlinking them
    for path in paths:
        print('Removing %s' % path)
        os.unlink(path)

def create_index_files(root_dir):
    """
    Crawl the root directory downwards, generating an index HTML file in each
    directory on the way down.

    @param {String} root_dir - The top level directory to crawl down from. In
        normal usage, this will be '.'.

    @return {[String]} Full file paths of all created files.
    """
    # Initialise list of created file paths to build up as we make them
    created_files = []
    # Walk the root dir downwards, creating index files as we go
    for here, dirs, files in os.walk(root_dir):
        print('Processing %s' % here)
        # Sort the subdirectories by name
        dirs = sorted(dirs)
        # Get image files - all files in the directory matching IMAGE_FILE_REGEX
        image_files = [f for f in files if re.match(IMAGE_FILE_REGEX, f)]
        # Sort the image files by name
        image_files = sorted(image_files)
        # Create this directory's index file and add its name to the created
        # files list
        created_files.append(
            _create_index_file(root_dir, here, image_files, dirs)
        )
    # Return the list of created files
    return created_files

def run_server():
    """
    Run the image server. This is blocking. Will handle user KeyboardInterrupt
    and other exceptions appropriately and return control once the server is
    stopped.

    @return {None}
    """
    # Get the port to run on
    port = _get_server_port()
    # Configure allow_reuse_address to make re-runs of the script less painful -
    # if this is not True then waiting for the address to be freed after the
    # last run can block a subsequent run
    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server instance
    server = SocketServer.TCPServer(
        ('', port),
        SimpleHTTPServer.SimpleHTTPRequestHandler
    )
    # Print out before actually running the server (cheeky / optimistic, however
    # you want to look at it)
    print('Your images are at http://127.0.0.1:%d/%s' % (
        port,
        INDEX_FILE_NAME
    ))
    # Try to run the server
    try:
        # Run it - this call blocks until the server is killed
        server.serve_forever()
    except KeyboardInterrupt:
        # This is the expected way of the server being killed, since imageMe is
        # intended for ad-hoc running from command line
        print('User interrupted, stopping')
    except Exception as exptn:
        # Catch everything else - this will handle shutdowns via other signals
        # and faults actually starting the server in the first place
        print(exptn)
        print('Unhandled exception in server, stopping')

def serve_dir(dir_path):
    """
    Generate indexes and run server from the given directory downwards.

    @param {String} dir_path - The directory path (absolute, or relative to CWD)

    @return {None}
    """
    # Create index files, and store the list of their paths for cleanup later
    created_files = create_index_files(dir_path)
    # Run the server in the current location - this blocks until it's stopped
    run_server()
    # Clean up the index files created earlier so we don't make a mess of
    # the image directories
    clean_up(created_files)

if __name__ == '__main__':
    # Generate indices and serve from the current directory downwards when run
    # as the entry point
    serve_dir('.')