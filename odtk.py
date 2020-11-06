import os
import json
import atexit
import http.client
import json
import sys


class ClientExceptionCodes:
    """Contains codes associated with errors in the client API."""

    INVALID_ATTRIBUTE_PATH = "InvalidAttributePath"
    """The specified attribute path cannot be found."""

    BAD_REQUEST = "BadRequest"
    """The request is malformed or contains invalid information."""

    EXECUTION_ERROR = "ExecutionError"
    """The request was valid, but an error occurred in executing the operation."""

    INTERNAL_ERROR = "InternalError"
    """An unexpected error occurred on the server."""

    SERIALIZATION_ERROR = "SerializationError"
    """There was a problem serializing a request or deserializing a response."""

    INVALID_OPERATION = "InvalidOperation"
    """The operation is not valid for the current state of the object."""


class ClientException(Exception):
    """Represents an exception in the client API."""

    def __init__(self, message, error_code=ClientExceptionCodes.BAD_REQUEST):
        """Initializes an instance.

        :param message: The message associated with the exception.
        :param error_code: The code associated with the exception.
        """
        super().__init__(message)
        self.error_code = error_code

    @staticmethod
    def create_from_http_status(status_code, message):
        """Creates a ClientException related to an HTTP exception.

        :param status_code: The HTTP status code associated with the exception.
        :param message: The message associated with the exception.
        :return:
        """
        return ClientException(message, "HTTP" + status_code)


class AttrRef(object):
    """Represents a reference to an ODTK attribute."""

    def __init__(self, path, temporary=False, transport=None):
        """Initializes an instance.

        :param path: The address of the attribute being referenced.
        :param temporary: Whether this attribute reference is being tracked.
        :param transport: The Transport used for tracking the attribute reference count.
        """
        self.path = path
        self.temporary = temporary
        self.transport = transport
        if transport and temporary:
            transport.increment_ref_count(path)

    def __del__(self):
        if self.transport and self.temporary:
            self.transport.decrement_ref_count(self.path)


class Transport(object):
    """Provides a mechanism to communicate with the server."""
    DEFAULT_HOST = u"127.0.0.1"
    """The default server host name used by the Transport."""
    DEFAULT_PORT = 9393
    """The default server port used by the Transport."""

    def __init__(self,
                 host=None,
                 port=None):
        """Initializes an instance.

        :param host: The host name of the server.
        :param port: The port on which the server is listening.
        """
        self.host = Transport.DEFAULT_HOST if host is None else host
        self.port = Transport.DEFAULT_PORT if port is None else port
        self.baseUrl = f'http://{self.host}:{self.port}/v1.0/'
        self.connection = None
        self._reset_connection()
        self.temporary_references = {}
        self.disposed = False
        atexit.register(self.close)

    def close(self):
        """Performs the object's cleanup procedure."""
        if not self.disposed:
            self.release_refs(list(self.temporary_references.keys()))
            self.connection.close()
            self.disposed = True

    def get(self, attribute_path):
        """Gets the value associated with an attribute.

        :param attribute_path: The identifier used to address the attribute.
        :return: The value associated with the attribute.
        """
        url = self.baseUrl + attribute_path
        return self._http_get(url)

    def set(self, attribute_path, value):
        """Sets the value associated with an attribute.

        :param attribute_path: The identifier used to address the attribute.
        :param value: The value to which the attribute should be associated.
        """
        url = self.baseUrl + attribute_path + '/set'
        body = self._encode(value)
        self._http_post(url, body)

    def invoke(self, attribute_path, arguments=[]):
        """Invokes a functional attribute.

        :param attribute_path: The identifier used to address the attribute.
        :param arguments: The arguments to pass to the function.
        :return: The value returned by the function.
        """
        url = self.baseUrl + attribute_path + '/invoke'
        body = '[' + ','.join(self._encode(arg) for arg in arguments) + ']'
        return self._http_post(url, body)

    def release_refs(self, attribute_paths):
        """Releases attribute references on the server.

        :param attribute_paths: The set of identifiers associated with the attribute references to release.
        """
        if not self.disposed:
            if len(attribute_paths) == 0:
                return
            for attribute_path in attribute_paths:
                del self.temporary_references[attribute_path]
            body = '[' + ', '.join(f'"{a}"' for a in attribute_paths) + ']'
            url = self.baseUrl + 'workspace/references/release'
            self._http_post(url, body)

    def get_ref_count(self):
        """Gets the number of attribute references currently being maintained on the server.

        :return: The number of attribute references currently being maintained on the server.
        """
        url = self.baseUrl + 'workspace/references/count'
        return self._http_get(url)

    def increment_ref_count(self, ref):
        """Increases, by one, the reference count to a specific attribute being tracked by this object.

        :param ref: The identifier associated with the attribute.
        """
        self._update_ref_count(ref, True)

    def decrement_ref_count(self, ref):
        """Decreases, by one, the reference count to a specific attribute being tracked by this object.

        A request is sent to the server to release the atttribute reference if the count reaches zero.

        :param ref: The identifier associated with the attribute.
        """
        self._update_ref_count(ref, False)

    def _update_ref_count(self, ref, increment):
        if self.disposed:
            return
        if ref not in self.temporary_references:
            if not increment:
                raise ClientException(
                    'Cannot decrement count for ' + ref + ' because it was not found in the reference map.',
                    ClientExceptionCodes.INVALID_OPERATION)
            self.temporary_references[ref] = 1
            return
        self.temporary_references[ref] += 1 if increment else -1
        if self.temporary_references[ref] == 0:
            self.release_refs([ref])

    @staticmethod
    def _encode(value):
        value_type = type(value)
        if value_type is AttrRef:
            return json.dumps({'type': 'ref', 'path': value.path})
        if value_type is bool or value_type is float or value_type is int or value_type is str:
            return json.dumps(value)
        if value is None:
            return 'null'
        raise ClientException('Value of type ' + value_type.__name__ + ' cannot be encoded for a request.',
                              ClientExceptionCodes.SERIALIZATION_ERROR)

    def _decode(self, message):
        if message == "":
            return message
        spec = json.loads(message)
        spec_type = type(spec)
        if spec_type is bool or spec_type is float or spec_type is int or spec_type is str:
            return spec
        # we expect a structure with a 'type' property
        data_type = spec['type']
        if data_type == 'ref':
            temp_ref_path = spec['path']
            temp_ref = AttrRef(temp_ref_path, True, self)
            return temp_ref
        if data_type == 'error':
            error_code = spec['code']
            error_message = spec['message']
            raise ClientException(error_message, error_code)
        raise ClientException("Unable to deserialize response '" + message + "'.",
                              ClientExceptionCodes.SERIALIZATION_ERROR)

    def _decode_http_response(self, response):
        response_content = response.read()
        if response.status == 200:
            return self._decode(response_content.decode('utf-8'))
        raise ClientException.create_from_http_status(response.status,
                                                      'Failed to execute request: ' + response.reason)

    @staticmethod
    def _create_http_headers():
        return {'connection': 'keep-alive'}

    def _http_get(self, url):
        return self._send_http_request("GET", url, None, self._create_http_headers())

    def _http_post(self, url, body):
        return self._send_http_request("POST", url, body, self._create_http_headers())

    def _send_http_request(self, method, url, body, headers):
        try:
            self.connection.request(
                method,
                url,
                body,
                headers=headers)
        # A ConnectionAbortedError is raised
        # when debugging in PyCharm and staying on a line for a long time.
        # We will just retry the request.
        except ConnectionAbortedError:
            self._reset_connection()
            self.connection.request(
                method,
                url,
                body,
                headers=headers)
        response = self.connection.getresponse()
        return self._decode_http_response(response)

    def _reset_connection(self):
        if self.connection:
            self.connection.close()
        self.connection = http.client.HTTPConnection(self.host, self.port)


class AttrProxy(object):
    """Provides a mechanism to interact with an ODTK attribute."""

    def __init__(self,
                 transport,
                 path,
                 temporary=False):
        """Initializes an instance.

        :param transport: The transport to use for communicating with the server.
        :param path: The identifier used to address the attribute.
        :param temporary: Indicates whether the attribute reference associated with this object should be tracked for cleanup.
        """
        # Do not use direct member assignment to avoid
        # infinite recursion in __setattr__
        # So instead of
        #     self.transport = transport
        #     self.path = path
        # set the fields using the parent
        # object.__setattr__ method
        object.__setattr__(self, 'transport', transport)
        object.__setattr__(self, 'path', path)
        object.__setattr__(self, 'temporary', temporary)
        if temporary:
            transport.increment_ref_count(path)

    def __del__(self):
        if self.temporary:
            self.transport.decrement_ref_count(self.path)

    def __getattr__(self, name):
        """Gets the value associated with a specified name.

        This special method enables a dynamic getter (of value or child ODTK attribute).

        If the specified name is 'value' or 'count', the corresponding value associated with the ODTK attribute
        represented by this object is retrieved from the server and returned; otherwise, an AttrProxy that represents
        the child ODTK attribute with the specified name is created and returned.

        :param name: The name of the ODTK attribute being accessed.
        :return: The value associated with the ODTK attribute being accessed.
        """
        if name.lower() == 'count':
            path = self.path + '.' + name
            response = self.transport.get(path)
            return self._value_from_transport_response(response)
        return AttrProxy(self.transport, self.path + '.' + name)

    def __setattr__(self, name, value):
        """Sets the value associated with the child ODTK attribute with a given name.

        This special method enables setting the value associated with a child ODTK attribute on the server.

        :param name: The name of the child ODTK attribute.
        :param value: The value to associate with the child ODTK attribute.
        """
        value_for_request = self._value_for_transport_request(value)
        self.transport.set(self.path + '.' + name, value_for_request)

    def __call__(self, *args, **kwargs):
        """Invokes the ODTK attribute represented by this object as a function.

        This special method enables invoking a child ODTK functional attribute on the server.

        :param args: The arguments to pass to the function.
        :param kwargs: Not used.
        :return: The value returned by the server.
        """
        transport_args = []
        for arg in args:
            transport_args.append(self._value_for_transport_request(arg))
        response = self.transport.invoke(self.path, transport_args)
        return self._value_from_transport_response(response)

    def __getitem__(self, key):
        """Creates an AttrProxy that represents an item contained by the ODTK attribute represented by this object.

        :param key: The ordinal position or name of the item.
        :return: An AttrProxy that represents the item.
        """
        if isinstance(key, str):
            ref = '"' + key + '"'
        else:
            ref = str(key)
        return AttrProxy(self.transport, self.path + '(' + ref + ')')

    def eval(self):
        response = self.transport.get(self.path)
        return self._value_from_transport_response(response)

    def __iter__(self):
        for i in range(0, self.count):
            yield self[i]

    def __repr__(self):
        return self.path

    @staticmethod
    def _value_for_transport_request(value):
        if isinstance(value, AttrProxy):
            return AttrRef(value.path)
        return value

    def _value_from_transport_response(self, response):
        if isinstance(response, AttrRef):
            return AttrProxy(self.transport, response.path, response.temporary)
        return response


class Client:
    """Provides a mechanism to interact with the ODTK API."""

    def __init__(self,
                 host=Transport.DEFAULT_HOST,
                 port=Transport.DEFAULT_PORT):
        """Initializes an instance.

        :param host: The host name of the server.
        :param port: The port on which the server is listening.
        """
        self._transport = Transport(host, port)
        self._root = AttrProxy(self._transport, "ODTK", False)

    def get_root(self):
        """Gets the AttrProxy that represents the ODTK application root attribute.

        :return: The AttrProxy that represents the ODTK application root attribute.
        """
        return self._root
