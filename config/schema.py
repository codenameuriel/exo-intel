import graphene
import planets.schema

# Root Query for entire project
class Query(planets.schema.Query, graphene.ObjectType):
    # inherit all fields from planets schema query
    pass

schema = graphene.Schema(query=Query)