import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from datetime import datetime

# -----------------------
# GraphQL Types
# -----------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

# -----------------------
# Mutations
# -----------------------
class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    def mutate(self, info, name, email, phone=None):
        # Email uniqueness validation
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")

        # Phone number validation
        if phone:
            pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
            if not re.match(pattern, phone):
                raise ValidationError("Invalid phone format")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    class Arguments:
        input = graphene.List(
            graphene.InputObjectType(
                name="CustomerInput",
                fields={
                    "name": graphene.String(required=True),
                    "email": graphene.String(required=True),
                    "phone": graphene.String()
                }
            ),
            required=True
        )

    def mutate(self, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for data in input:
                try:
                    # Email uniqueness check
                    if Customer.objects.filter(email=data.email).exists():
                        raise ValidationError("Email already exists")

                    # Phone validation
                    if data.phone:
                        pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
                        if not re.match(pattern, data.phone):
                            raise ValidationError("Invalid phone format")

                    customer = Customer.objects.create(
                        name=data.name,
                        email=data.email,
                        phone=data.phone
                    )
                    created.append(customer)
                except Exception as e:
                    errors.append(f"{data.email if hasattr(data,'email') else 'unknown'} - {str(e)}")
        return BulkCreateCustomers(customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int()

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise ValidationError("Price must be positive")
        if stock < 0:
            raise ValidationError("Stock cannot be negative")
        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.String()  # optional

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")

        products = Product.objects.filter(pk__in=product_ids)
        if not products.exists():
            raise ValidationError("At least one valid product must be selected")

        order = Order.objects.create(customer=customer)

        # Set products
        order.products.set(products)

        # Calculate total_amount
        order.total_amount = sum([p.price for p in products])

        # Optional order date
        if order_date:
            try:
                order.order_date = datetime.fromisoformat(order_date)
            except ValueError:
                raise ValidationError("Invalid date format, must be ISO8601")

        order.save()
        return CreateOrder(order=order)


# -----------------------
# Root Mutation Class
# -----------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# -----------------------
# Query Class (Optional)
# -----------------------
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()
