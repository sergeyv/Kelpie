import unittest
from repoze.bfg import testing

def _initTestingDB():
    from kelpie.models import initialize_sql
    session = initialize_sql('sqlite://')
    return session

class TestMyView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        _initTestingDB()
        
    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, request):
        from kelpie.views import my_view
        return my_view(request)

    def test_it(self):
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/mytemplate.pt')
        response = self._callFUT(request)
        self.assertEqual(renderer.root.name, 'root')
        self.assertEqual(renderer.request, request)
        self.assertEqual(renderer.project, 'kelpie')
