"""Tests unitarios fase 3 SaaS (sin BD)."""
from __future__ import annotations

import unittest
from datetime import datetime, timedelta

from app.core.tenant import AuthContext, is_platform_superadmin
from app.core.tenant_context import effective_list_tenant_id
from app.core.tenant_resolve import slug_from_host
from app.core.tenant_subscription import (
    subscription_allows_read,
    subscription_allows_write,
)
from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.tenants.models import (
    EstadoSuscripcionTenantEnum,
    EstadoTenantEnum,
    PlanTenantEnum,
    Tenant,
)


def _tenant(**kwargs) -> Tenant:
    now = utc_now_naive()
    base = dict(
        id=1,
        slug="demo-sc",
        nombre="Demo",
        estado=EstadoTenantEnum.ACTIVO,
        plan=PlanTenantEnum.STARTER,
        dominio_custom=None,
        stripe_customer_id=None,
        stripe_subscription_id=None,
        stripe_price_id=None,
        subscription_status=EstadoSuscripcionTenantEnum.TRIAL,
        subscription_ends_at=None,
        created_at=now,
        updated_at=now,
    )
    base.update(kwargs)
    return Tenant(**base)


class TestSlugFromHost(unittest.TestCase):
    def test_localhost_subdomain(self) -> None:
        self.assertEqual(slug_from_host("demo-sc.localhost"), "demo-sc")

    def test_platform_domain(self) -> None:
        self.assertEqual(
            slug_from_host("acme.app.ejemplo.com", "app.ejemplo.com"),
            "acme",
        )

    def test_plain_host(self) -> None:
        self.assertIsNone(slug_from_host("localhost"))


class TestEffectiveListTenantId(unittest.TestCase):
    def test_superadmin_passes_query(self) -> None:
        class U:
            tenant_id = None

        ctx = AuthContext(
            user=U(),
            roles=["ADMIN"],
            tenant_id=None,
            is_platform_superadmin=True,
        )
        self.assertEqual(effective_list_tenant_id(ctx, 99), 99)

    def test_tenant_user_fixed(self) -> None:
        class U:
            tenant_id = 2

        ctx = AuthContext(
            user=U(),
            roles=["ADMIN"],
            tenant_id=2,
            is_platform_superadmin=False,
        )
        self.assertEqual(effective_list_tenant_id(ctx, 99), 2)


class TestSubscriptionRules(unittest.TestCase):
    def test_trial_active(self) -> None:
        t = _tenant(subscription_status=EstadoSuscripcionTenantEnum.TRIAL)
        self.assertTrue(subscription_allows_write(t))

    def test_past_due_no_write(self) -> None:
        t = _tenant(subscription_status=EstadoSuscripcionTenantEnum.PAST_DUE)
        self.assertTrue(subscription_allows_read(t))
        self.assertFalse(subscription_allows_write(t))

    def test_trial_expired(self) -> None:
        t = _tenant(
            subscription_status=EstadoSuscripcionTenantEnum.TRIAL,
            subscription_ends_at=utc_now_naive() - timedelta(days=1),
        )
        self.assertFalse(subscription_allows_read(t))


class TestPlatformSuperadmin(unittest.TestCase):
    def test_admin_without_tenant(self) -> None:
        class U:
            tenant_id = None

        self.assertTrue(is_platform_superadmin(U(), ["ADMIN"]))

    def test_admin_with_tenant_not_super(self) -> None:
        class U:
            tenant_id = 1

        self.assertFalse(is_platform_superadmin(U(), ["ADMIN"]))


if __name__ == "__main__":
    unittest.main()
