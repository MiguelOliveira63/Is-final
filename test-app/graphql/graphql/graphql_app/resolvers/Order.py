import graphene
from db.connection import execute_query  # Função de execução de queries SQL

class OrderType(graphene.ObjectType):
    order_id = graphene.String()
    customer_id = graphene.String()
    order_date = graphene.Date()
    quantity = graphene.Int()
    sales = graphene.Float()
    profit = graphene.Float()

# Query para listar pedidos
class Query(graphene.ObjectType):
    orders = graphene.List(OrderType)

    def resolve_orders(self, info):
        query = """
            SELECT Order_ID, Customer_ID, Order_Date, Quantity, Sales, Profit
            FROM orders
        """
        result = execute_query(query)  # Executa a query SQL diretamente
        return [
            OrderType(
                order_id=row[0],
                customer_id=row[1],
                order_date=row[2],
                quantity=row[3],
                sales=row[4],
                profit=row[5],
            )
            for row in result
        ]

# Mutation para criar um novo pedido
class CreateOrder(graphene.Mutation):
    class Arguments:
        order_id = graphene.String(required=True)
        customer_id = graphene.String(required=True)
        order_date = graphene.Date(required=True)
        quantity = graphene.Int(required=True)
        sales = graphene.Float(required=True)
        profit = graphene.Float(required=True)

    order = graphene.Field(lambda: OrderType)

    def mutate(self, info, order_id, customer_id, order_date, quantity, sales, profit):
        query = """
            INSERT INTO orders (Order_ID, Customer_ID, Order_Date, Quantity, Sales, Profit)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING Order_ID, Customer_ID, Order_Date, Quantity, Sales, Profit
        """
        params = (order_id, customer_id, order_date, quantity, sales, profit)
        result = execute_query(query, params)  # Executa a query SQL diretamente
        return CreateOrder(
            order=OrderType(
                order_id=result[0][0],
                customer_id=result[0][1],
                order_date=result[0][2],
                quantity=result[0][3],
                sales=result[0][4],
                profit=result[0][5],
            )
        )

# Adiciona a mutation ao schema
class Mutation(graphene.ObjectType):
    create_order = CreateOrder.Field()