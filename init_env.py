import os

import cryptography.fernet


def wizard():
    print('This is osm validator setting initialization wizard.')
    print('Please read and enter a few settings.')
    print('Press ENTER to continue.')
    input()
    print()

    if os.path.exists('.env'):
        print('You already have `.env` file, please move it to another location '
              'if you sure that you want to use this wizard to create new `.env` file.')
        return

    print('You need configure and provide OpenStreetMap OAuth credentials.')
    print('Please check documentation: https://wiki.openstreetmap.org/wiki/OAuth')
    print('and configure new application: '
          'https://www.openstreetmap.org/user/username/oauth_clients/new')
    print()

    OAUTH_OPENSTREETMAP_KEY = input('Enter OSM Consumer Key: ').strip()
    OAUTH_OPENSTREETMAP_SECRET = input('Enter OSM Consumer Secret: ').strip()
    print()

    with open('.env.template') as template_handle, open('.env', 'w') as env_handle:
        env_handle.write(template_handle.read().format(
            SECRET_KEY=cryptography.fernet.Fernet.generate_key().decode(),
            OAUTH_OPENSTREETMAP_KEY=OAUTH_OPENSTREETMAP_KEY,
            OAUTH_OPENSTREETMAP_SECRET=OAUTH_OPENSTREETMAP_SECRET,
        ))

    print('Well done!')
    print('`.env` created, now you can start you application with `docker-compose up` command.')
    print()


if __name__ == '__main__':
    wizard()
