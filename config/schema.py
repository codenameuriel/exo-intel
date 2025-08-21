import graphene

import api.schema


# Root Query for entire project
class Query(api.schema.Query, graphene.ObjectType):
    # inherit all fields from api schema query
    pass


schema = graphene.Schema(query=Query)
