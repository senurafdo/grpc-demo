import unittest
import time
import grpc
from concurrent import futures

import hello_pb2
import hello_pb2_grpc
from server import HelloServiceServicer  # Import your servicer implementation here.

# If your generated file does NOT provide this helper, define it yourself:
def add_HelloServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'SayHello': grpc.unary_unary_rpc_method_handler(
            servicer.SayHello,
            request_deserializer=hello_pb2.HelloRequest.FromString,
            response_serializer=hello_pb2.HelloResponse.SerializeToString,
        ),
        'LotsOfReplies': grpc.unary_stream_rpc_method_handler(
            servicer.LotsOfReplies,
            request_deserializer=hello_pb2.HelloRequest.FromString,
            response_serializer=hello_pb2.HelloResponse.SerializeToString,
        ),
        'LotsOfGreetings': grpc.stream_unary_rpc_method_handler(
            servicer.LotsOfGreetings,
            request_deserializer=hello_pb2.HelloRequest.FromString,
            response_serializer=hello_pb2.HelloResponse.SerializeToString,
        ),
        'BidiHello': grpc.stream_stream_rpc_method_handler(
            servicer.BidiHello,
            request_deserializer=hello_pb2.HelloRequest.FromString,
            response_serializer=hello_pb2.HelloResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'hello.HelloService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

class TestHelloService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create and start an in-process gRPC server on a custom port (50052).
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_HelloServiceServicer_to_server(HelloServiceServicer(), cls.server)
        cls.port = 50052
        cls.server.add_insecure_port(f'[::]:{cls.port}')
        cls.server.start()

        # Give the server a moment to start up.
        time.sleep(1)

        # Create a channel and stub to connect to our in-process server.
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.stub = hello_pb2_grpc.HelloServiceStub(cls.channel)

    @classmethod
    def tearDownClass(cls):
        # Stop the server after tests.
        cls.server.stop(0)

    def test_SayHello(self):
        """Test the unary RPC."""
        response = self.stub.SayHello(hello_pb2.HelloRequest(greeting="Test"))
        self.assertEqual(response.reply, "Hello, Test")

    def test_LotsOfReplies(self):
        """Test the server-streaming RPC."""
        request = hello_pb2.HelloRequest(greeting="Stream")
        responses = list(self.stub.LotsOfReplies(request))
        # Suppose your server sends 5 messages
        self.assertEqual(len(responses), 5)
        for i, resp in enumerate(responses, start=1):
            self.assertIn(f"Response {i}", resp.reply)

    def test_LotsOfGreetings(self):
        """Test the client-streaming RPC."""
        def request_stream():
            for name in ["Alice", "Bob", "Charlie"]:
                yield hello_pb2.HelloRequest(greeting=name)

        response = self.stub.LotsOfGreetings(request_stream())
        # Expecting a single response with concatenated names
        self.assertEqual(response.reply, "Hello, Alice, Bob, Charlie")

    def test_BidiHello(self):
        """Test the bidirectional streaming RPC."""
        def request_stream():
            for name in ["X", "Y", "Z"]:
                yield hello_pb2.HelloRequest(greeting=name)

        responses = list(self.stub.BidiHello(request_stream()))
        # We expect exactly 3 responses, one per request
        self.assertEqual(len(responses), 3)
        self.assertEqual(responses[0].reply, "Hello, X")
        self.assertEqual(responses[1].reply, "Hello, Y")
        self.assertEqual(responses[2].reply, "Hello, Z")


if __name__ == '__main__':
    unittest.main()
