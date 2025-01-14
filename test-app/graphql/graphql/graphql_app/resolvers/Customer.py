import graphene
from db.connection import execute_query  # Importa a função de execução de queries SQL

class CustomerType(graphene.ObjectType):
    customer_id = graphene.String()
    customer_name = graphene.String()
    segment = graphene.String()
    country = graphene.String()

# Query para listar customers
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)

    def resolve_customers(self, info):
        query = "SELECT Customer_ID, Customer_Name, Segment, Country FROM customers"
        result = execute_query(query)  # Executa a query diretamente no banco
        # Mapeia os resultados para o tipo GraphQL
        return [CustomerType(customer_id=row[0], customer_name=row[1], segment=row[2], country=row[3]) for row in result]

# Mutation para criar um novo customer
class CreateCustomer(graphene.Mutation):
    class Arguments:
        customer_name = graphene.String(required=True)
        segment = graphene.String(required=True)
        country = graphene.String(required=True)

    customer = graphene.Field(lambda: CustomerType)

    def mutate(self, info, customer_name, segment, country):
        query = """
            INSERT INTO customers (Customer_Name, Segment, Country)
            VALUES (%s, %s, %s)
            RETURNING Customer_ID, Customer_Name, Segment, Country
        """
        # Executa a query diretamente com os parâmetros
        result = execute_query(query, (customer_name, segment, country))
        # Retorna o resultado da mutação
        return CreateCustomer(customer=CustomerType(customer_id=result[0][0], customer_name=result[0][1], segment=result[0][2], country=result[0][3]))

# Adiciona a mutation no schema
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()