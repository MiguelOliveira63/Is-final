import graphene
from graphql_app.resolvers.Customer import Query as CustomerQuery, Mutation as CustomerMutation
from graphql_app.resolvers.Product import Query as ProductQuery, UpdateProductLocation as ProductMutation
from graphql_app.resolvers.Order import Query as OrderQuery, Mutation as OrderMutation

class Query(CustomerQuery, ProductQuery, OrderQuery, graphene.ObjectType):
    pass

class Mutation(CustomerMutation, OrderMutation, graphene.ObjectType):
    update_product_location = ProductMutation.Field()  

schema = graphene.Schema(query=Query, mutation=Mutation)