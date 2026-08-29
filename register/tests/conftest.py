from __future__ import annotations

import sqlite3
from dataclasses import dataclass

import pytest

from register.db import open_register
from register.entities import create_person, create_tenant

TENANT = "tn_carbonproject"
OTHER_TENANT = "tn_other"


@dataclass
class World:
    """A small, fully populated tenant zero to test against."""

    conn: sqlite3.Connection
    tenant: str
    principal: str
    ea: str
    henderson: str  # counterparty A
    veldt: str  # counterparty B


@pytest.fixture
def conn(tmp_path) -> sqlite3.Connection:
    connection = open_register(tmp_path / "register.sqlite3")
    yield connection
    connection.close()


@pytest.fixture
def world(conn: sqlite3.Connection) -> World:
    create_tenant(conn, "The Carbon Project", is_zero=True, tenant_id=TENANT)
    create_tenant(conn, "Another Client", tenant_id=OTHER_TENANT)

    principal = create_person(
        conn,
        tenant_id=TENANT,
        display_name="Aaron",
        email="aaron@carbonproject.com.au",
        is_principal=True,
        relationship="principal",
        produced_by="human:manual",
    )
    ea = create_person(
        conn,
        tenant_id=TENANT,
        display_name="EA",
        email="ea@carbonproject.com.au",
        relationship="executive assistant",
        produced_by="human:manual",
    )
    henderson = create_person(
        conn,
        tenant_id=TENANT,
        display_name="Ruth Henderson",
        email="ruth@henderson.example",
        relationship="supplier",
        produced_by="human:manual",
    )
    veldt = create_person(
        conn,
        tenant_id=TENANT,
        display_name="Veldt Capital",
        email="deals@veldt.example",
        kind="org",
        relationship="prospective investor",
        produced_by="human:manual",
    )
    return World(conn, TENANT, principal, ea, henderson, veldt)
