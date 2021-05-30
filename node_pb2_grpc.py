# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import node_pb2 as node__pb2


class NodeStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.search = channel.unary_unary(
                '/node.Node/search',
                request_serializer=node__pb2.SearchRequest.SerializeToString,
                response_deserializer=node__pb2.SearchResponse.FromString,
                )
        self.insert = channel.unary_unary(
                '/node.Node/insert',
                request_serializer=node__pb2.InsertRequest.SerializeToString,
                response_deserializer=node__pb2.InsertResponse.FromString,
                )
        self.retrieveValue = channel.unary_unary(
                '/node.Node/retrieveValue',
                request_serializer=node__pb2.RetrieveRequest.SerializeToString,
                response_deserializer=node__pb2.Value.FromString,
                )
        self.storeValue = channel.unary_unary(
                '/node.Node/storeValue',
                request_serializer=node__pb2.Value.SerializeToString,
                response_deserializer=node__pb2.StoreResponse.FromString,
                )


class NodeServicer(object):
    """Missing associated documentation comment in .proto file."""

    def search(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def insert(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def retrieveValue(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def storeValue(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NodeServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'search': grpc.unary_unary_rpc_method_handler(
                    servicer.search,
                    request_deserializer=node__pb2.SearchRequest.FromString,
                    response_serializer=node__pb2.SearchResponse.SerializeToString,
            ),
            'insert': grpc.unary_unary_rpc_method_handler(
                    servicer.insert,
                    request_deserializer=node__pb2.InsertRequest.FromString,
                    response_serializer=node__pb2.InsertResponse.SerializeToString,
            ),
            'retrieveValue': grpc.unary_unary_rpc_method_handler(
                    servicer.retrieveValue,
                    request_deserializer=node__pb2.RetrieveRequest.FromString,
                    response_serializer=node__pb2.Value.SerializeToString,
            ),
            'storeValue': grpc.unary_unary_rpc_method_handler(
                    servicer.storeValue,
                    request_deserializer=node__pb2.Value.FromString,
                    response_serializer=node__pb2.StoreResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'node.Node', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Node(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def search(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Node/search',
            node__pb2.SearchRequest.SerializeToString,
            node__pb2.SearchResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def insert(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Node/insert',
            node__pb2.InsertRequest.SerializeToString,
            node__pb2.InsertResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def retrieveValue(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Node/retrieveValue',
            node__pb2.RetrieveRequest.SerializeToString,
            node__pb2.Value.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def storeValue(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Node/storeValue',
            node__pb2.Value.SerializeToString,
            node__pb2.StoreResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
