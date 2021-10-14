"""A collection of useful functions used by different components."""

import base64
import pickle


def serialize(data) -> str:
    return base64.b64encode(pickle.dumps(data)).decode('ascii')


def deserialize(data):
    return pickle.loads(base64.b64decode(data))


def node_from_identifier(identifier: str, nodes: list):

    for nc in nodes:
        if nc.identifier == identifier:
            return nc
    else:  # couldn't find a node with this identifier => search for identifier_comp
        for nc in nodes:
            if identifier in nc.identifier_comp:
                return nc
        else:
            raise Exception(
                f'could not find node class with identifier \'{identifier}\'. '
                f'if you changed your node\'s class name, make sure to add the old '
                f'identifier to the identifier_comp list attribute to provide '
                f'backwards compatibility.'
            )
