from royal.tests.functional import TestBase

expected = (
    ("Resource         Pattern                Collection                      "
     "           Item"),
    ("================ ====================== ================================"
     "========== ================================="),
    ("photos           /photos                example.resources.photos:"
     "Collection        example.resources.photos:Item"),
    ("users            /users                 example.resources.users:"
     "Collection         example.resources.users:Item"),
    ("users.followers  /users/(id)/followers  example.resources.users:"
     "UserFollowers      example.resources.users:Follower"),
    ("users.photos     /users/(id)/photos     example.resources.users_photos:"
     "Collection  "),
    (""),
)


class Test(TestBase):

    def test_presources(self):
        from royal.presources import get_pretty_resource_list
        self.config.commit()
        registry = self.config.registry
        result = get_pretty_resource_list(registry).split('\n')
        for index, line in enumerate(result):
            self.assertEqual(expected[index], line)
