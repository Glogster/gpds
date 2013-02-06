====================
 GPDS version 0.4.0
====================

Simple GET-PUT-DELETE service (*GPDS*) to (temporary) store your files as an alternative to NFS shared folders.

It uses Gunicorn_ WSGI server as base and pass through all it's options. So you can simply start it using next command ``gpds WORKING-DIRECTORY``, where *working directory* is path to store and read files (by default, it'll be started on 8000 port).

.. _Gunicorn: http://gunicorn.org/

This server can process only three request types, so try them with ``curl`` from your console::

    curl -i -X PUT -T somefile.jpg http://localhost:8000/

    HTTP/1.1 201 Created
    Server: gpds/0.3.1
    Date: Mon, 04 Feb 2013 16:06:27 GMT
    Connection: close
    Location: /55/1c/551ced9e9d54658155ae8b4197afd32087a1c551.jpg
    Content-Length: 0

So, what can we see here. GPDS created new file on yours file system (201 Created HTTP response) and this file is accessible on next address ``http://localhost:8000/55/1c/551ced9e9d54658155ae8b4197afd32087a1c551.jpg``. This big string *551...551* is SHA1 hash from uploaded file content. So we can do next trick::

    curl -i -X PUT -T somefile.txt http://localhost:8000/

    HTTP/1.1 200 OK
    Server: gpds/0.3.1
    Date: Mon, 04 Feb 2013 16:17:12 GMT
    Connection: close
    Location: /55/1c/551ced9e9d54658155ae8b4197afd32087a1c551.jpg
    Content-Length: 0

As you can see, ``Location`` is the same as in previous request. GPDS won't rewrite uploaded file.

OK, let's try to access this file::

    curl -i http://localhost:8000/55/1c/551ced9e9d54658155ae8b4197afd32087a1c551.jpg

    HTTP/1.1 200 OK
    Server: gpds/0.3.1
    Date: Mon, 04 Feb 2013 16:38:26 GMT
    Connection: close
    Content-Length: 56737
    Content-Type: image/jpeg

    ...file content...

Cool, our service sent our image for us properly. Now we'll delete this file and try to access it one more time::

    curl -i -X DELETE http://localhost:8000/55/1c/551ced9e9d54658155ae8b4197afd32087a1c551.jpg

    HTTP/1.1 204 No Content
    Server: gpds/0.3.1
    Date: Mon, 04 Feb 2013 16:40:49 GMT
    Connection: close
    Content-Length: 0

    curl -i http://localhost:8001/55/1c/551ced9e9d54658155ae8b4197afd32087a1c551.jpg

    HTTP/1.1 404 Not Found
    Server: gpds/0.3.1
    Date: Mon, 04 Feb 2013 16:41:09 GMT
    Connection: close
    Content-Length: 0

As you can see GPDS successfully erased your file from disk and next time sent not found response for you.