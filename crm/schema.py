import graphene


class Query (graphene.ObjectType):
    hello = graphene.String(defautl_value = "hello")