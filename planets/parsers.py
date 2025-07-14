from rest_framework.parsers import JSONParser


class GraphQLParser(JSONParser):
    """
    A custom parser for GraphQL requests.

    This parser correctly identifies the 'application/json' media type,
    but its `parse` method simply returns the raw request stream, leaving it
    intact for the Graphene view to handle. This is the definitive solution
    to the "cannot access body after reading" error.
    """

    media_type = "application/json"

    def parse(self, stream, media_type=None, parser_context=None):
        """
        This method overrides the default JSONParser's behavior.
        Instead of parsing and consuming the stream, it returns it as is.
        """
        return stream
