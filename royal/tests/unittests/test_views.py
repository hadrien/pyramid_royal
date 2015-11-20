import unittest

import mock
from pyramid import testing, httpexceptions


class TestCollection(unittest.TestCase):

    def test_create_returns_dict(self):
        from royal.views import Collection
        body = {'name': 'value'}
        create_func = mock.Mock()
        create_func.return_value = {'url': 'http://example.com/resource'}
        request = testing.DummyRequest(deserialized_body=body)
        context = testing.DummyResource(create=create_func)

        collection = Collection(context, request)
        result = collection.create()

        create_func.assert_called_once_with(body)
        self.assertEqual(result, create_func.return_value)
        self.assertEqual(request.response.headers['Location'],
                         'http://example.com/resource')
        self.assertEqual(request.response.status_int,
                         httpexceptions.HTTPCreated.code)

    def test_create_returns_obj(self):
        from royal.views import Collection
        body = {'name': 'value'}
        create_func = mock.Mock()
        create_func.return_value.url.return_value = 'http://example.com/yeah'
        request = testing.DummyRequest(deserialized_body=body)
        context = testing.DummyResource(create=create_func)

        collection = Collection(context, request)
        result = collection.create()

        create_func.assert_called_once_with(body)
        self.assertEqual(result, create_func.return_value)
        self.assertEqual(request.response.headers['Location'],
                         'http://example.com/yeah')
        self.assertEqual(request.response.status_int,
                         httpexceptions.HTTPCreated.code)

    def test_create_returns_no_url(self):
        from royal.views import Collection
        body = {'name': 'value'}
        create_func = mock.Mock()
        create_func.return_value = 'response'
        request = testing.DummyRequest(deserialized_body=body)
        context = testing.DummyResource(create=create_func)

        collection = Collection(context, request)
        result = collection.create()

        create_func.assert_called_once_with(body)
        self.assertEqual(result, create_func.return_value)
        self.assertNotIn('Location', request.response.headers)
        self.assertEqual(request.response.status_int,
                         httpexceptions.HTTPOk.code)

    def test_create_returns_url_not_callable(self):
        from royal.views import Collection
        body = {'name': 'value'}
        create_func = mock.Mock()
        create_func.return_value.url = 'http://example.com/resource'
        request = testing.DummyRequest(deserialized_body=body)
        context = testing.DummyResource(create=create_func)

        collection = Collection(context, request)
        result = collection.create()

        create_func.assert_called_once_with(body)
        self.assertEqual(result, create_func.return_value)
        self.assertEqual(request.response.headers['Location'],
                         'http://example.com/resource')
        self.assertEqual(request.response.status_int,
                         httpexceptions.HTTPCreated.code)
