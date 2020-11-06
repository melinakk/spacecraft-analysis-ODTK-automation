import datetime
import unittest

from odtk import Client, AttrProxy, ClientException, ClientExceptionCodes


class AttrProxyTests(unittest.TestCase):
    DEFAULT_SATELLITE_NAME = 'DefaultSatellite'
    APP_VERSION = '6.5.3'

    @classmethod
    def setUpClass(cls):
        client = Client()
        odtk = client.get_root()
        # ensure new scenario
        if odtk.children.count > 0:
            # close scenario
            odtk.application.deleteObject('', odtk.scenario[0])
        odtk.application.createObj(odtk, 'Scenario', 'TestScenario')
        # create default objects
        odtk.application.createObj(odtk.scenario[0],
                                   'Satellite',
                                   AttrProxyTests.DEFAULT_SATELLITE_NAME)
        odtk.application.createObj(odtk.scenario[0],
                                   'Satellite',
                                   'AnotherSatellite')
        cls.odtk = odtk

    def testGetValue(self):
        self.assertEqual(self.odtk.application.appVersion.eval(), AttrProxyTests.APP_VERSION)

    def testGetUsingAttrProxyReturnsTheSameResultAsInlineVersion(self):
        application_proxy = self.odtk.application.eval()
        self.assertIsInstance(application_proxy, AttrProxy)
        # verify that the proxy was created as a result of a response from the server (i.e., temporary == True)
        self.assertTrue(application_proxy.temporary)
        attr_proxy_version = application_proxy.appVersion.eval()  # this uses a path like 'WS._1.appVersion'
        inline_path_version = self.odtk.application.appVersion.eval()  # this uses 'odtk.application.appVersion' path
        self.assertEqual(attr_proxy_version, inline_path_version)

    def testGetInvalidPathThrowsException(self):
        with self.assertRaises(ClientException) as context:
            self.odtk.non_existent.eval()
        client_exception = context.exception
        self.assertEqual(client_exception.error_code, ClientExceptionCodes.INVALID_ATTRIBUTE_PATH)
        self.assertIn('Undefined symbol', str(client_exception))

    def testSet(self):
        odtk = self.odtk

        # ensure that current scenario description is not equal to what it will be set to
        description = datetime.datetime.now().strftime('%c')
        actual_description = odtk.scenario[0].description.eval()
        self.assertNotEqual(actual_description, description,
                            'Precondition failed: Scenario description cannot be equal to the test value.')

        # set
        odtk.scenario[0].description = description

        # verify
        actual_description = odtk.scenario[0].description.eval()
        self.assertEqual(actual_description, description)

    def testSetInvalidPathThrowsException(self):
        with self.assertRaises(ClientException) as context:
            self.odtk.non_existent = 1
        client_exception = context.exception
        self.assertEqual(client_exception.error_code, ClientExceptionCodes.INVALID_ATTRIBUTE_PATH)
        self.assertIn('Undefined symbol', str(client_exception))

    def testInvoke(self):
        odtk = self.odtk

        # ensure that satellite does not exist
        satellite_name = 'testSatellite'
        scenario_children = odtk.scenario[0].children
        for scenarioChild in scenario_children:
            if scenarioChild.name.eval() == 'Satellite':
                for satellite in scenarioChild:
                    self.assertNotEqual(satellite_name, satellite.name.eval(),
                                        'Precondition failed: A satellite with the name \'' + satellite_name
                                        + '\' exists in the scenario.')
                break

        # invoke by creating a satellite
        odtk.application.createObj(odtk.scenario[0], 'Satellite', satellite_name)

        # verify
        satellite = odtk.scenario[0].Satellite[satellite_name]
        self.assertEqual(satellite.name.eval(), satellite_name)

    def testInvokeInvalidPathThrowsException(self):
        with self.assertRaises(ClientException) as context:
            self.odtk.non_existent()
        client_exception = context.exception
        self.assertEqual(client_exception.error_code, ClientExceptionCodes.INVALID_ATTRIBUTE_PATH)
        self.assertIn('Undefined symbol', str(client_exception))

    def testInvokeNonFunctionalAttributePathThrowsException(self):
        with self.assertRaises(ClientException) as context:
            self.odtk.application.appVersion()
        client_exception = context.exception
        self.assertEqual(client_exception.error_code, ClientExceptionCodes.INVALID_ATTRIBUTE_PATH)
        self.assertIn('Attribute path does not specify a functional attribute.', str(client_exception))

    def testGetCount(self):
        satellite_count = self.odtk.scenario[0].children["Satellite"].count
        self.assertIsInstance(satellite_count, int)
        self.assertTrue(satellite_count > 0)
        # verify that we can get the items
        for i in range(satellite_count):
            class_name = self.odtk.scenario[0].children["Satellite"][i].ClassName.eval()
            self.assertEqual('Satellite', class_name)

    def testGetItemUsingNameIndex(self):
        item = self.odtk.Scenario[0].Children["Satellite"].Item[AttrProxyTests.DEFAULT_SATELLITE_NAME].eval()
        self.assertIsInstance(item, AttrProxy)
        self.assertEqual(item.name.eval(), AttrProxyTests.DEFAULT_SATELLITE_NAME)

    def testGetItemUsingNonExistentNameThrowsException(self):
        with self.assertRaises(ClientException) as context:
            # noinspection PyUnusedLocal
            unused = self.odtk.Scenario[0].Children["Satellite"].Item["Non-Existent-Name"].eval()
        client_exception = context.exception
        self.assertEqual(client_exception.error_code, ClientExceptionCodes.INVALID_ATTRIBUTE_PATH)
        self.assertIn('Undefined symbol', str(client_exception))

    def testGetItemUsingNumericIndex(self):
        # assume default satellite index == 0
        item = self.odtk.scenario[0].children["Satellite"].Item[0]
        self.assertIsInstance(item, AttrProxy)
        self.assertEqual(item.name.eval(), AttrProxyTests.DEFAULT_SATELLITE_NAME)

    def testGetItemUsingInvalidNumericIndexThrowsException(self):
        with self.assertRaises(ClientException) as context:
            # noinspection PyUnusedLocal
            unused = self.odtk.scenario[0].children["Satellite"].Item[999].eval()
        client_exception = context.exception
        self.assertEqual(client_exception.error_code, ClientExceptionCodes.INVALID_ATTRIBUTE_PATH)
        self.assertIn('Index Out of Range', str(client_exception))

    def testGetItemByName(self):
        item = self.odtk.scenario[0].Children["Satellite"].ItemByName[AttrProxyTests.DEFAULT_SATELLITE_NAME].eval()
        self.assertIsInstance(item, AttrProxy)
        self.assertEqual(item.name.eval(), AttrProxyTests.DEFAULT_SATELLITE_NAME)

    def testGetItemByNameUsingNonExistentNameThrowsException(self):
        with self.assertRaises(ClientException) as context:
            # noinspection PyUnusedLocal
            unused = self.odtk.scenario[0].children["Satellite"].ItemByName["Non-Existent-Name"].eval()
        client_exception = context.exception
        self.assertEqual(client_exception.error_code, ClientExceptionCodes.INVALID_ATTRIBUTE_PATH)
        self.assertIn('Undefined symbol', str(client_exception))

    def testInvokeItemExists(self):
        exists = self.odtk.scenario[0].children['Satellite'].ItemExists(AttrProxyTests.DEFAULT_SATELLITE_NAME)
        self.assertTrue(exists)

    def testInvokeItemExistsReturnsFalseOnNonExistentItem(self):
        exists = self.odtk.scenario[0].children['Satellite'].ItemExists('Non-Existent-Name')
        self.assertFalse(exists)

    def testInvokeItemExistsWithNumericIndexThrowsException(self):
        with self.assertRaises(ClientException) as context:
            self.odtk.scenario[0].children["Satellite"].ItemExists(0)
        client_exception = context.exception
        self.assertEqual(client_exception.error_code, ClientExceptionCodes.EXECUTION_ERROR)
        self.assertIn('A name index argument was expected', str(client_exception))

    def testStringResponse(self):
        response = self.odtk.application.appVersion.eval()
        self.assertIsInstance(response, str)

    def testIntResponse(self):
        response = self.odtk.children.count
        self.assertIsInstance(response, int)

    def testFloatResponse(self):
        response = self.odtk.scenario[0].OrbitClassifications.LEO.EccentricityMax.eval()
        self.assertIsInstance(response, float)

    def testBoolResponse(self):
        response = self.odtk.scenario[0].children["Satellite"].ItemExists(AttrProxyTests.DEFAULT_SATELLITE_NAME)
        self.assertIsInstance(response, bool)

    def testAttrProxyResponse(self):
        response = self.odtk.application.eval()
        self.assertIsInstance(response, AttrProxy)

    def testIterator(self):
        odtk = self.odtk

        satellite_count = self.odtk.scenario[0].children["Satellite"].count
        self.assertTrue(satellite_count > 0)
        # verify that we can get the items
        for i in range(satellite_count):
            class_name = self.odtk.scenario[0].children["Satellite"][i].ClassName.eval()
            self.assertEqual('Satellite', class_name)

        for scenarioProperty in odtk.scenario[0].properties:
            self.assertIsInstance(scenarioProperty, AttrProxy)
            name = scenarioProperty.name.eval()
            self.assertIsInstance(name, str)
            print(name)


if __name__ == '__main__':
    unittest.main()
