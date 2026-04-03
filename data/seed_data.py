import os
from dotenv import load_dotenv

"""
seed_data.py — Generación de datos sintéticos para LedgerGuard-TransactSure
Genera ~11K registros realistas usando Faker para poblar las 5 tablas del modelo.

Orden de inserción (respeta foreign keys):
  customers → accounts  → transactions
                        ↑
              policies  → claims
"""

import random
import sys
import os
from datetime import datetime, timezone
from decimal import Decimal

from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

# ── PATH: permite importar app.database y app.models desde la raíz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Base, Customer, Account, Transaction, Policy, Claim

# ── CONFIG ────────────────────────────────────────────────────────────────────
fake = Faker()           # instancia global de Faker
random.seed(42)          # reproducibilidad: los mismos datos cada ejecución
Faker.seed(42)

NUM_CUSTOMERS    = 1_000
NUM_ACCOUNTS     = 3_000   # ~3 por cliente
NUM_TRANSACTIONS = 5_000   # ~1.6 por cuenta
NUM_POLICIES     = 800     # ~0.8 por cliente
NUM_CLAIMS       = 1_200   # ~1.5 por póliza


# ── HELPERS ───────────────────────────────────────────────────────────────────

def random_account_number() -> str:
    """Genera un número de cuenta único tipo ACC-XXXXXXXX."""
    return f"ACC-{random.randint(10_000_000, 99_999_999)}"


def random_policy_number() -> str:
    """Genera un número de póliza único tipo POL-XXXXXXXX."""
    return f"POL-{random.randint(10_000_000, 99_999_999)}"


def utc_now() -> datetime:
    """Retorna el timestamp actual en UTC (con timezone)."""
    return datetime.now(timezone.utc)


def random_past_datetime(days_back: int = 730) -> datetime:
    """Retorna una fecha aleatoria entre hoy y `days_back` días atrás."""
    return fake.date_time_between(
        start_date=f"-{days_back}d",
        end_date="now",
        tzinfo=timezone.utc
    )


# ── GENERADORES ───────────────────────────────────────────────────────────────

def generate_customers(n: int) -> list[Customer]:
    """
    Crea `n` objetos Customer con datos sintéticos.
    Nota: emails se validan como únicos aquí para no fallar en la BD.
    """
    customers = []
    emails_used = set()

    while len(customers) < n:
        email = fake.unique.email()
        if email in emails_used:       # doble guardia, por si acaso
            continue
        emails_used.add(email)

        customers.append(Customer(
            full_name  = fake.name(),
            email      = email,
            country    = fake.country(),
            created_at = random_past_datetime(days_back=1095),  # hasta 3 años atrás
        ))

    return customers


def generate_accounts(customers: list[Customer], n: int) -> list[Account]:
    """
    Crea `n` objetos Account distribuidos aleatoriamente entre los clientes.
    Garantiza que cada cliente tenga al menos 1 cuenta.
    """
    account_types = ["checking", "savings", "credit"]
    accounts = []
    account_numbers_used = set()

    # Primero: 1 cuenta garantizada por cliente
    for customer in customers:
        acc_number = random_account_number()
        while acc_number in account_numbers_used:
            acc_number = random_account_number()
        account_numbers_used.add(acc_number)

        accounts.append(Account(
            customer_id    = customer.id,
            account_number = acc_number,
            account_type   = random.choice(account_types),
            balance        = Decimal(str(round(random.uniform(0, 50_000), 2))),
            created_at     = random_past_datetime(days_back=730),
        ))

    # Segundo: cuentas extra hasta llegar a `n`
    remaining = n - len(customers)
    for _ in range(remaining):
        acc_number = random_account_number()
        while acc_number in account_numbers_used:
            acc_number = random_account_number()
        account_numbers_used.add(acc_number)

        accounts.append(Account(
            customer_id    = random.choice(customers).id,
            account_number = acc_number,
            account_type   = random.choice(account_types),
            balance        = Decimal(str(round(random.uniform(0, 50_000), 2))),
            created_at     = random_past_datetime(days_back=730),
        ))

    return accounts


def generate_transactions(accounts: list[Account], n: int) -> list[Transaction]:
    """
    Crea `n` objetos Transaction distribuidos entre las cuentas.
    Los tipos y estados siguen los CHECK CONSTRAINTS del modelo.
    """
    tx_types   = ["debit", "credit", "transfer"]
    tx_statuses = ["pending", "completed", "failed", "reversed"]

    # Pesos para que "completed" sea el estado más común (realista)
    status_weights = [0.10, 0.75, 0.10, 0.05]

    descriptions = [
        "Utility payment", "Salary deposit", "Online purchase",
        "ATM withdrawal", "Insurance premium", "Rent payment",
        "Investment transfer", "Refund received", "Loan installment",
        "Service fee", "Grocery store", "Fuel station",
    ]

    transactions = []
    for _ in range(n):
        transactions.append(Transaction(
            account_id       = random.choice(accounts).id,
            amount           = Decimal(str(round(random.uniform(1, 10_000), 2))),
            transaction_type = random.choice(tx_types),
            status           = random.choices(tx_statuses, weights=status_weights)[0],
            description      = random.choice(descriptions),
            created_at       = random_past_datetime(days_back=365),
        ))

    return transactions


def generate_policies(customers: list[Customer], n: int) -> list[Policy]:
    """
    Crea `n` objetos Policy distribuidos entre los clientes.
    start_date siempre es anterior a end_date (CHECK CONSTRAINT del modelo).
    """
    policy_types = ["life", "health", "auto", "home"]
    policies = []
    policy_numbers_used = set()

    for _ in range(n):
        pol_number = random_policy_number()
        while pol_number in policy_numbers_used:
            pol_number = random_policy_number()
        policy_numbers_used.add(pol_number)

        start = random_past_datetime(days_back=730)
        # end_date: entre 1 y 3 años después del start (póliza activa o vencida)
        end = fake.date_time_between(
            start_date=start,
            end_date="+3y",
            tzinfo=timezone.utc
        )

        policies.append(Policy(
            customer_id    = random.choice(customers).id,
            policy_number  = pol_number,
            policy_type    = random.choice(policy_types),
            premium_amount = Decimal(str(round(random.uniform(50, 2_000), 2))),
            start_date     = start,
            end_date       = end,
            created_at     = start,
        ))

    return policies


def generate_claims(policies: list[Policy], n: int) -> list[Claim]:
    """
    Crea `n` objetos Claim distribuidos entre las pólizas.
    incident_date siempre está entre start_date y end_date de la póliza.
    """
    claim_statuses = ["submitted", "under_review", "approved", "rejected", "paid"]
    status_weights = [0.20, 0.20, 0.25, 0.15, 0.20]

    claims = []
    for _ in range(n):
        policy = random.choice(policies)

        # incident_date debe estar dentro del período de vigencia de la póliza
        incident = fake.date_time_between(
            start_date=policy.start_date,
            end_date=policy.end_date,
            tzinfo=timezone.utc,
        )

        claims.append(Claim(
            policy_id     = policy.id,
            claim_amount  = Decimal(str(round(random.uniform(100, 50_000), 2))),
            claim_status  = random.choices(claim_statuses, weights=status_weights)[0],
            incident_date = incident,
            created_at    = utc_now(),
        ))

    return claims


# ── ORQUESTADOR PRINCIPAL ─────────────────────────────────────────────────────

def seed_database() -> None:
    """
    Orquesta la generación e inserción de todos los datos en orden correcto.
    Usa una sola transacción: si algo falla, hace rollback completo.
    """
    print("🌱 Iniciando seed de LedgerGuard-TransactSure...")
    print(f"   Objetivo: ~{NUM_CUSTOMERS + NUM_ACCOUNTS + NUM_TRANSACTIONS + NUM_POLICIES + NUM_CLAIMS:,} registros\n")

    db = SessionLocal()

    try:
        # ── 1. CUSTOMERS ──────────────────────────────────────────────────────
        print(f"👤 Generando {NUM_CUSTOMERS:,} clientes...", end=" ", flush=True)
        customers = generate_customers(NUM_CUSTOMERS)
        db.add_all(customers)
        db.flush()   # asigna IDs sin hacer commit → los podemos usar abajo
        print("✅")

        # ── 2. ACCOUNTS ───────────────────────────────────────────────────────
        print(f"🏦 Generando {NUM_ACCOUNTS:,} cuentas...", end=" ", flush=True)
        accounts = generate_accounts(customers, NUM_ACCOUNTS)
        db.add_all(accounts)
        db.flush()
        print("✅")

        # ── 3. TRANSACTIONS ───────────────────────────────────────────────────
        print(f"💸 Generando {NUM_TRANSACTIONS:,} transacciones...", end=" ", flush=True)
        transactions = generate_transactions(accounts, NUM_TRANSACTIONS)
        db.add_all(transactions)
        db.flush()
        print("✅")

        # ── 4. POLICIES ───────────────────────────────────────────────────────
        print(f"📋 Generando {NUM_POLICIES:,} pólizas...", end=" ", flush=True)
        policies = generate_policies(customers, NUM_POLICIES)
        db.add_all(policies)
        db.flush()
        print("✅")

        # ── 5. CLAIMS ─────────────────────────────────────────────────────────
        print(f"📝 Generando {NUM_CLAIMS:,} reclamaciones...", end=" ", flush=True)
        claims = generate_claims(policies, NUM_CLAIMS)
        db.add_all(claims)
        db.flush()
        print("✅")

        # ── COMMIT FINAL ──────────────────────────────────────────────────────
        print("\n💾 Guardando en PostgreSQL...", end=" ", flush=True)
        db.commit()
        print("✅")

        # ── RESUMEN ───────────────────────────────────────────────────────────
        print("\n" + "─" * 45)
        print("🎉 Seed completado exitosamente!")
        print(f"   Customers    : {len(customers):>6,}")
        print(f"   Accounts     : {len(accounts):>6,}")
        print(f"   Transactions : {len(transactions):>6,}")
        print(f"   Policies     : {len(policies):>6,}")
        print(f"   Claims       : {len(claims):>6,}")
        print(f"   TOTAL        : {len(customers)+len(accounts)+len(transactions)+len(policies)+len(claims):>6,}")
        print("─" * 45)

    except SQLAlchemyError as e:
        db.rollback()
        print(f"\n❌ Error durante el seed — rollback ejecutado.")
        print(f"   Detalle: {e}")
        sys.exit(1)

    finally:
        db.close()


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    seed_database()