"""
Tenant Subscription Model
Tracks billing and subscription details for tenants
"""
from app.database import db
from app.models.base import BaseModel
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime


class SubscriptionStatus:
    """Subscription status constants"""
    ACTIVE = 'active'
    PAST_DUE = 'past_due'
    CANCELLED = 'cancelled'
    PAUSED = 'paused'


class BillingCycle:
    """Billing cycle constants"""
    MONTHLY = 'monthly'
    ANNUAL = 'annual'


class TenantSubscription(BaseModel):
    """
    Tenant Subscription Model

    Tracks subscription details, billing cycles, and payment status
    Will integrate with Stripe or other payment processors
    """
    __tablename__ = 'tenant_subscriptions'

    # Relationships
    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    tenant = relationship('Tenant', backref='subscriptions')

    # Subscription Details
    plan = Column(String(50), nullable=False)  # free, basic, premium, enterprise
    status = Column(String(50), default=SubscriptionStatus.ACTIVE, nullable=False)
    billing_cycle = Column(String(20), default=BillingCycle.MONTHLY)

    # Pricing
    price = Column(Numeric(10, 2))  # Amount in USD
    currency = Column(String(3), default='USD')

    # Payment Provider Integration
    stripe_subscription_id = Column(String(255), unique=True)
    stripe_customer_id = Column(String(255))
    stripe_payment_method_id = Column(String(255))

    # Billing Period
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    trial_start = Column(DateTime)
    trial_end = Column(DateTime)

    # Cancellation
    cancel_at = Column(DateTime)  # Scheduled cancellation date
    cancelled_at = Column(DateTime)  # Actual cancellation date

    # Additional Data
    additional_data = Column(db.JSON, default={})  # Store additional info (renamed from metadata to avoid SQLAlchemy conflict)

    def __init__(self, **kwargs):
        """Initialize subscription"""
        super().__init__(**kwargs)

        # Set billing period if not provided
        if not self.current_period_start:
            self.current_period_start = datetime.utcnow()

        if not self.current_period_end and self.current_period_start:
            if self.billing_cycle == BillingCycle.MONTHLY:
                from dateutil.relativedelta import relativedelta
                self.current_period_end = self.current_period_start + relativedelta(months=1)
            elif self.billing_cycle == BillingCycle.ANNUAL:
                from dateutil.relativedelta import relativedelta
                self.current_period_end = self.current_period_start + relativedelta(years=1)

    def to_dict(self):
        """Convert subscription to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'plan': self.plan,
            'status': self.status,
            'billing_cycle': self.billing_cycle,
            'price': float(self.price) if self.price else 0,
            'currency': self.currency,
            'stripe_subscription_id': self.stripe_subscription_id,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'trial_start': self.trial_start.isoformat() if self.trial_start else None,
            'trial_end': self.trial_end.isoformat() if self.trial_end else None,
            'cancel_at': self.cancel_at.isoformat() if self.cancel_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'is_active': self.is_active(),
            'is_in_trial': self.is_in_trial(),
            'days_until_renewal': self.days_until_renewal(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != SubscriptionStatus.ACTIVE:
            return False

        # Check if period is current
        now = datetime.utcnow()
        if self.current_period_end and now > self.current_period_end:
            return False

        return True

    def is_in_trial(self):
        """Check if subscription is in trial period"""
        if not self.trial_start or not self.trial_end:
            return False

        now = datetime.utcnow()
        return self.trial_start <= now <= self.trial_end

    def days_until_renewal(self):
        """Get days until next renewal"""
        if not self.current_period_end:
            return None

        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)

    def schedule_cancellation(self):
        """Schedule cancellation at end of current period"""
        if self.current_period_end:
            self.cancel_at = self.current_period_end

    def cancel_immediately(self):
        """Cancel subscription immediately"""
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
        self.cancel_at = None

    def renew(self):
        """Renew subscription for next billing period"""
        from dateutil.relativedelta import relativedelta

        if not self.current_period_end:
            raise ValueError("Cannot renew: no current period end date")

        # Move period forward
        self.current_period_start = self.current_period_end

        if self.billing_cycle == BillingCycle.MONTHLY:
            self.current_period_end = self.current_period_start + relativedelta(months=1)
        elif self.billing_cycle == BillingCycle.ANNUAL:
            self.current_period_end = self.current_period_start + relativedelta(years=1)

        # Clear cancellation if was scheduled
        if self.cancel_at:
            self.cancel_at = None

        # Reactivate if was cancelled
        if self.status == SubscriptionStatus.CANCELLED:
            self.status = SubscriptionStatus.ACTIVE

    def __repr__(self):
        return f'<TenantSubscription tenant_id={self.tenant_id} plan={self.plan} status={self.status}>'
