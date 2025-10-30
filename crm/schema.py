import graphene
from graphene_django import DjangoObjectType
from django.db import transaction, IntegrityError
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from decimal import Decimal
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter


from .models import Customer,  Order
from crm.models import Product

# -------------------- TYPES --------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


# -------------------- INPUT TYPES --------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.types.datetime.DateTime(required=False)


# -------------------- MUTATIONS --------------------
# Create single customer
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []

        # Validate email format
        try:
            validate_email(input.email)
        except DjangoValidationError:
            errors.append("Invalid email format.")
            return CreateCustomer(customer=None, message=None, errors=errors)

        # Validate phone
        if input.phone:
            phone_validator = RegexValidator(
                regex=r'^(\+\d{7,15}|\d{3}-\d{3}-\d{4})$',
                message='Phone must be like +1234567890 or 123-456-7890'
            )
            try:
                phone_validator(input.phone)
            except DjangoValidationError:
                errors.append("Invalid phone format. Use +1234567890 or 123-456-7890.")
                return CreateCustomer(customer=None, message=None, errors=errors)

        # Check unique email
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists.")
            return CreateCustomer(customer=None, message=None, errors=errors)

        # Create customer
        try:
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
        except Exception as exc:
            errors.append(f"Failed to create customer: {str(exc)}")
            return CreateCustomer(customer=None, message=None, errors=errors)

        return CreateCustomer(customer=customer, message="Customer created successfully.", errors=None)


# Bulk create customers
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, inputs):
        created = []
        errors = []
        seen_emails = set()
        valid_entries = []

        # Validate data
        for idx, data in enumerate(inputs):
            row = idx + 1

            if not data.name:
                errors.append(f"Row {row}: name is required.")
                continue
            try:
                validate_email(data.email)
            except DjangoValidationError:
                errors.append(f"Row {row}: invalid email format ({data.email}).")
                continue
            if data.email in seen_emails or Customer.objects.filter(email=data.email).exists():
                errors.append(f"Row {row}: email already exists ({data.email}).")
                continue

            if data.phone:
                phone_validator = RegexValidator(
                    regex=r'^(\+\d{7,15}|\d{3}-\d{3}-\d{4})$',
                    message='Phone must be like +1234567890 or 123-456-7890'
                )
                try:
                    phone_validator(data.phone)
                except DjangoValidationError:
                    errors.append(f"Row {row}: invalid phone format ({data.phone}).")
                    continue

            seen_emails.add(data.email)
            valid_entries.append(data)

        # Create valid entries
        try:
            with transaction.atomic():
                for data in valid_entries:
                    c = Customer.objects.create(
                        name=data.name,
                        email=data.email,
                        phone=data.phone
                    )
                    created.append(c)
        except IntegrityError as exc:
            errors.append(f"Database error: {str(exc)}")

        return BulkCreateCustomers(customers=created, errors=errors or None)


# Create product
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []

        try:
            price = Decimal(str(input.price))
        except Exception:
            errors.append("Price must be a valid number.")
            return CreateProduct(product=None, errors=errors)

        if price <= 0:
            errors.append("Price must be positive.")
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            errors.append("Stock cannot be negative.")

        if errors:
            return CreateProduct(product=None, errors=errors)

        try:
            product = Product.objects.create(
                name=input.name,
                price=price,
                stock=stock
            )
        except Exception as exc:
            errors.append(f"Failed to create product: {str(exc)}")
            return CreateProduct(product=None, errors=errors)

        return CreateProduct(product=product, errors=None)


# Create order
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []

        # Validate customer
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID.")
            return CreateOrder(order=None, errors=errors)

        # Validate products
        if not input.product_ids or len(input.product_ids) == 0:
            errors.append("At least one product must be provided.")
            return CreateOrder(order=None, errors=errors)

        products = []
        for pid in input.product_ids:
            try:
                p = Product.objects.get(pk=pid)
                products.append(p)
            except Product.DoesNotExist:
                errors.append(f"Invalid product ID: {pid}")

        if errors:
            return CreateOrder(order=None, errors=errors)

        total = sum((p.price for p in products), Decimal('0.00'))
        order_dt = input.order_date if input.order_date else timezone.now()

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    customer=customer,
                    total_amount=total,
                    order_date=order_dt
                )
                order.products.set(products)
                order.save()
        except Exception as exc:
            errors.append(f"Failed to create order: {str(exc)}")
            return CreateOrder(order=None, errors=errors)

        return CreateOrder(order=order, errors=None)

class UpdateLowStockProducts(graphene.Mutation):
    """
    Finds products with stock < 10, restocks them by +10,
    and returns the updated products.
    """

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info):
        from .models import Product

        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []

        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated.append(product)

        message = f"Updated {len(updated)} low-stock products."
        return UpdateLowStockProducts(updated_products=updated, message=message)


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()  # ✅ add this line








# -------------------- QUERIES --------------------
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello from CRM!")
    # Filterable connections
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.String())
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.String())
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.String())

    # Single item resolvers
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    order = graphene.Field(OrderType, id=graphene.ID(required=True))

    def resolve_customer(root, info, id):
        return Customer.objects.get(pk=id)

    def resolve_product(root, info, id):
        return Product.objects.get(pk=id)

    def resolve_order(root, info, id):
        return Order.objects.get(pk=id)
    
    def resolve_all_customers(root, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs




# -------------------- EXPORT SCHEMA --------------------
schema = graphene.Schema(query=Query, mutation=Mutation)
