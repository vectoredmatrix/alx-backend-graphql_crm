import graphene


class CRMQuery (graphene.ObjectType):
    hello = graphene.String(defautl_value = "hello")