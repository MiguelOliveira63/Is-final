import graphene
from db.connection import execute_query

class ProductType(graphene.ObjectType):
    product_id = graphene.Int()
    category = graphene.String()
    sub_category = graphene.String()
    product_name = graphene.String()
    latitude = graphene.Float()
    longitude = graphene.Float()
    order_id = graphene.String()

class Query(graphene.ObjectType):
    products = graphene.List(ProductType)

    def resolve_products(self, info):
        query = """
            SELECT Product_ID, Category, Sub_Category, Product_Name, Latitude, Longitude, Order_ID
            FROM products
        """
        result = execute_query(query)  
        return [
            ProductType(
                product_id=row[0],
                category=row[1],
                sub_category=row[2],
                product_name=row[3],
                latitude=row[4],
                longitude=row[5],
                order_id=row[6],
            )
            for row in result
        ]

class UpdateProductLocation(graphene.Mutation):
    class Arguments:
        product_id = graphene.Int(required=True)
        order_id = graphene.Int(required=True)
        latitude = graphene.Float(required=True)
        longitude = graphene.Float(required=True)

    product = graphene.Field(lambda: ProductType)

    def mutate(self, info, product_id, latitude, longitude):
        if latitude < -90 or latitude > 90:
            raise ValueError('Invalid latitude value. It must be between -90 and 90.')
        if longitude < -180 or longitude > 180:
            raise ValueError('Invalid longitude value. It must be between -180 and 180.')

        update_query = """
            UPDATE products SET Latitude = %s, Longitude = %s WHERE Product_ID = %s RETURNING *
        """
        params = (latitude, longitude, product_id)
        try:
            result = execute_query(update_query, params)
            if not result:
                raise Exception('Product not found')
            product = result[0]
            return UpdateProductLocation(
                product=ProductType(
                    product_id=product[0],
                    category=product[1],
                    sub_category=product[2],
                    product_name=product[3],
                    latitude=product[4],
                    longitude=product[5],
                    order_id=product[6]
                )
            )
        except Exception as e:
            print("Error in mutate:", str(e))
            raise e

class Mutation(graphene.ObjectType):
    update_product_location = UpdateProductLocation.Field()