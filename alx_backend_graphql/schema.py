import graphene
from graphene_django import DjangoObjectType
from crm.schema import CRMQuery




class Query(CRMQuery.graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)