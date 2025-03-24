import unittest
from unittest.mock import MagicMock

import hello_pb2
import hello_pb2_grpc
from server import HelloServiceServicer  # Import your actual servicer.

class TestHelloServiceServicer(unittest.TestCase):

    def setUp(self):
        # Instantiate your service (servicer) directly.
        self.servicer = HelloServiceServicer()
        # Mock the gRPC context, which normally gRPC passes to service methods.
        self.context = MagicMock()

    def test_SayHello(self):
        # Test the unary RPC logic by calling the servicer method directly.
        request = hello_pb2.HelloRequest(greeting="Test")
        response = self.servicer.SayHello(request, self.context)
        self.assertEqual(response.reply, "Hello, Test")

    def test_LotsOfReplies(self):
        # Test the server-streaming RPC.
        request = hello_pb2.HelloRequest(greeting="Stream")
        responses = list(self.servicer.LotsOfReplies(request, self.context))

        # Suppose your method yields 5 replies
        self.assertEqual(len(responses), 5)
        for i, resp in enumerate(responses, start=1):
            self.assertIn(f"Response {i}", resp.reply)

    def test_LotsOfGreetings(self):
        # Test the client-streaming RPC.
        # We can simulate multiple requests by passing an iterator.
        def request_stream():
            for name in ["Alice", "Bob", "Charlie"]:
                yield hello_pb2.HelloRequest(greeting=name)

        response = self.servicer.LotsOfGreetings(request_stream(), self.context)
        self.assertEqual(response.reply, "Hello, Alice, Bob, Charlie")

    def test_BidiHello(self):
        # Test the bidirectional streaming RPC.
        def request_stream():
            for name in ["X", "Y", "Z"]:
                yield hello_pb2.HelloRequest(greeting=name)

        responses = list(self.servicer.BidiHello(request_stream(), self.context))
        # We expect one response per request
        self.assertEqual(len(responses), 3)
        self.assertEqual(responses[0].reply, "Hello, X")
        self.assertEqual(responses[1].reply, "Hello, Y")
        self.assertEqual(responses[2].reply, "Hello, Z")

if __name__ == '__main__':
    unittest.main()
