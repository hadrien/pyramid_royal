from royal.tests.functional import TestBase

expected_lines = {
    'photos': ('/photos', 'example.resources.photos:Collection',
               'example.resources.photos:Item'),
    'projects': ('/projects', 'example.ext.sqla.resources.projects:Collection',
                 'example.ext.sqla.resources.projects:Item'),
    'users': ('/users', 'example.resources.users:Collection',
              'example.resources.users:Item'),
    'users.followers': ('/users/(id)/followers',
                        'example.resources.users:UserFollowers',
                        'example.resources.users:Follower'),
    'users.photos': ('/users/(id)/photos',
                     'example.resources.users_photos:Collection'),
    }


class Test(TestBase):

    def test_presources(self):
        from royal.presources import get_pretty_resource_list
        self.config.commit()
        registry = self.config.registry
        result = get_pretty_resource_list(registry).splitlines()
        result.pop(1)  # header underline

        expected = expected_lines.copy()
        for line in result:
            terms = line.split()

            if terms[0] not in expected_lines:
                continue

            columns = expected_lines[terms[0]]

            for term in columns:
                self.assertIn(term, term)

            expected.pop(terms[0])

        self.assertEqual(expected, {})
