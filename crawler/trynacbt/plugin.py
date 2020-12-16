import requests

def sync_threads(url, apikey, goodbye_threads):
    '''Upload threads to a server running the plugin.'''
    threads = []

    for t in goodbye_threads:
        threads.append({
            'title': t.title,
            'uri': t.uri,
            'datetimePosted': t.datetimePosted
        });

    response = requests.post(
        url = url,
        json = threads,
        params = {'apikey': apikey}
    )

    print(response)
    print(response.text)
