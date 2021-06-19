from django.db import models


class User(models.Model):
    """
    Database model representing a Pothos user.
    """

    id = models.TextField(primary_key=True)
    username = models.CharField(max_length=30, null=False)
    email = models.TextField(unique=True)
    currency = models.CharField(max_length=3, null=False)

    def __str__(self) -> str:
        return f"<Pothos User {self.id} {self.username}>"


class Transaction(models.Model):
    """
    Database model representing a Pothos user's transaction.
    """

    class TransactionType(models.TextChoices):
        """
        Enumeration representing the types of transactions possible.
        """

        INCOME = "income"
        EXPENDITURE = "expenditure"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=11, choices=TransactionType.choices)
    amount = models.FloatField()
    transaction_date = models.DateField(
        auto_now=True
    )  # this default is not actually used anywhere.
    name = models.CharField(max_length=30)
    notes = models.TextField(null=True)
    tags = models.CharField(null=True, max_length=14)

    def __str__(self) -> str:
        return (
            f"<Transaction {self.transaction_date.upper()} by {self.user} - {self.amount} "
            f"at {self.transaction_date}>"
        )
