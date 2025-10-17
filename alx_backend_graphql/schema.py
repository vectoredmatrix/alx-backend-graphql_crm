import graphene
from graphene_django import DjangoObjectType
from crm.schema import Query as CRMQuery




class Query(CRMQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)


#class Query(CRMQuery, graphene.ObjectType)