import graphene
from graphene_django.types import DjangoObjectType
from crm.models import Product
from django.db.models import F

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'stock')

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        # Query products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        
        # Increment stock by 10 for each product
        updated_products = []
        for product in low_stock_products:
            product.stock = F('stock') + 10
            product.save()
            updated_products.append(product)
        
        # Refresh objects to get updated stock values
        updated_products = Product.objects.filter(id__in=[p.id for p in updated_products])
        
        return UpdateLowStockProducts(
            products=updated_products,
            message=f"Successfully updated {len(updated_products)} low-stock products"
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")  # For log_crm_heartbeat

schema = graphene.Schema(query=Query, mutation=Mutation)