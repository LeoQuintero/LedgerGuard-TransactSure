from sqlalchemy import (
    Column, Integer, String, Numeric,
    DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id         = Column(Integer, primary_key=True, index=True)
    full_name  = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False, index=True)
    country    = Column(String(60),  nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
        # Sirve para que, cuando tengas un objeto customer en tu código, 
        # puedas hacer customer.accounts y Python te devuelva automáticamente una lista con todas sus cuentas
    accounts = relationship("Account", back_populates="customer")
    policies = relationship("Policy",  back_populates="customer")

class Account(Base):
    __tablename__ = "accounts"

    id             = Column(Integer, primary_key=True, index=True)
    customer_id    = Column(Integer, ForeignKey("customers.id"), nullable=False)
    account_number = Column(String(20), unique=True, nullable=False, index=True)
    account_type   = Column(String(20), nullable=False)
    balance        = Column(Numeric(15, 2), nullable=False, default=0.00)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("account_type IN ('checking', 'savings', 'credit')", name="ck_account_type"),
        CheckConstraint("balance >= 0", name="ck_balance_positive"),
    )

    # Relationships
    customer     = relationship("Customer", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")    

class Transaction(Base):
    __tablename__ = "transactions"

    id               = Column(Integer, primary_key=True, index=True)
    account_id       = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount           = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    status           = Column(String(20), nullable=False, default="pending")
    description      = Column(String(255))
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("transaction_type IN ('debit', 'credit', 'transfer')", name="ck_transaction_type"),
        CheckConstraint("status IN ('pending', 'completed', 'failed', 'reversed')", name="ck_transaction_status"),
        CheckConstraint("amount > 0", name="ck_transaction_amount_positive"),
    )

    # Relationships
    account = relationship("Account", back_populates="transactions")

class Policy(Base):
    __tablename__ = "policies"

    id             = Column(Integer, primary_key=True, index=True)
    customer_id    = Column(Integer, ForeignKey("customers.id"), nullable=False)
    policy_number  = Column(String(20), unique=True, nullable=False, index=True)
    policy_type    = Column(String(30), nullable=False)
    premium_amount = Column(Numeric(15, 2), nullable=False)
    start_date     = Column(DateTime(timezone=True), nullable=False)
    end_date       = Column(DateTime(timezone=True), nullable=False)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("policy_type IN ('life', 'health', 'auto', 'home')", name="ck_policy_type"),
        CheckConstraint("premium_amount > 0", name="ck_premium_positive"),
        CheckConstraint("end_date > start_date", name="ck_policy_dates"),
    )

    # Relationships
    customer = relationship("Customer", back_populates="policies")
    claims   = relationship("Claim", back_populates="policy")


class Claim(Base):
    __tablename__ = "claims"

    id            = Column(Integer, primary_key=True, index=True)
    policy_id     = Column(Integer, ForeignKey("policies.id"), nullable=False)
    claim_amount  = Column(Numeric(15, 2), nullable=False)
    claim_status  = Column(String(20), nullable=False, default="submitted")
    incident_date = Column(DateTime(timezone=True), nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("claim_status IN ('submitted', 'under_review', 'approved', 'rejected', 'paid')", name="ck_claim_status"),
        CheckConstraint("claim_amount > 0", name="ck_claim_amount_positive"),
    )

    # Relationships
    policy = relationship("Policy", back_populates="claims")