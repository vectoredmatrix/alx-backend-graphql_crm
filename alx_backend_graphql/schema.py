import graphene
from graphene_django import DjangoObjectType



# class Query(CRMQuery , graphene.ObjectType)

class Query(graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)