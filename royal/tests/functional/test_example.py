import pkg_resources

from royal.tests.functional import TestBase


class Test(TestBase):

    def _add_users(self):
        from example.model import User
        for i in range(50):
            name = u'user%s' % i
            user = User.create(self.db, name, name + '@email.com')
            setattr(self, 'user%s' % i, user)
        self.addCleanup(self._delete_users)

    def _delete_users(self):
        for i in range(50):
            user = getattr(self, 'user%s' % i)
            user.delete()

    def test_root(self):
        self.app.get('/')

    def test_users_index(self):
        self._add_users()
        response = self.app.get('/users?offset=20&limit=20')

        result = response.json

        url_first = 'http://localhost/users/?limit=20&offset=0'
        url_previous = 'http://localhost/users/?limit=20&offset=0'
        url_next = 'http://localhost/users/?limit=20&offset=40'
        url_href = 'http://localhost/users/?limit=20&offset=20'

        self.assertEqual(url_first, result['first'])
        self.assertEqual(url_next, result['next'])
        self.assertEqual(url_previous, result['previous'])
        self.assertEqual(url_href, result['href'])

        self.assertEqual(20, len(result['users']))

        for user in result['users']:
            username = user['username']
            self.assertIn('_id', user)
            self.assertIn('href', user)
            self.assertIn('email', user)
            self.assertIn('photos', user)
            self.assertEqual('http://localhost/users/%s/photos/' % username,
                             user['photos']['href'])

    def test_post_photo(self):
        from example.model import Photo
        image_gif = pkg_resources.resource_stream('royal.tests.functional',
                                                  'image.gif')
        result = self.app.post(
            '/users/hadrien/photos',
            upload_files=[(u'image', u'image.gif', image_gif.read())]
        )

        photo = Photo.get_one(self.db, author='hadrien')
        location = 'http://localhost/photos/%s/' % str(photo._id)

        headers = result.headers
        self.assertIn('Content-Type', headers)
        self.assertIn('Location', headers)

        self.assertEqual('application/json; charset=UTF-8',
                         headers['Content-Type'])
        self.assertEqual(location,
                         headers['Location'])

        expected = {
            'href': location,
            '_id': str(photo._id),
            'author': {
                'href': 'http://localhost/users/hadrien/'
            }
        }
        self.assertEqual(expected, result.json)
