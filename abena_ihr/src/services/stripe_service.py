import requests
import os
import uuid
from typing import Dict, Optional
from datetime import datetime

# Stripe API configuration
STRIPE_SECRET_KEY = "sk_test_eiCaYL3stP6RbLzRvLoqE59P00J1T0mzsM"
STRIPE_API_BASE = "https://api.stripe.com/v1"

class StripeService:
    def __init__(self):
        self.appointment_fee = 20000  # $200.00 in cents
        self.payment_intents = {}  # Store payment intents in memory
        
    def create_payment_intent(self, appointment_id: str, patient_name: str, provider_name: str) -> Dict:
        """Create a real payment intent for appointment booking"""
        try:
            print(f"DEBUG: About to create payment intent with amount: {self.appointment_fee}")
            print(f"DEBUG: Using direct Stripe API call")
            
            # Make direct API call to Stripe
            headers = {
                "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "amount": str(self.appointment_fee),
                "currency": "usd",
                "automatic_payment_methods[enabled]": "true",
                "metadata[appointment_id]": appointment_id,
                "metadata[patient_name]": patient_name,
                "metadata[provider_name]": provider_name,
                "metadata[appointment_date]": datetime.now().strftime("%Y-%m-%d"),
                "description": f"Appointment booking - {patient_name} with {provider_name}"
            }
            
            response = requests.post(
                f"{STRIPE_API_BASE}/payment_intents",
                headers=headers,
                data=data
            )
            
            print(f"DEBUG: Stripe API response status: {response.status_code}")
            print(f"DEBUG: Stripe API response: {response.text[:200]}")
            
            if response.status_code != 200:
                raise Exception(f"Stripe API error: {response.status_code} - {response.text}")
            
            payment_intent_data = response.json()
            print(f"DEBUG: Payment intent data: {payment_intent_data}")
            
            return {
                "client_secret": payment_intent_data["client_secret"],
                "payment_intent_id": payment_intent_data["id"],
                "amount": payment_intent_data["amount"],
                "currency": payment_intent_data["currency"]
            }
        except Exception as e:
            raise Exception(f"Failed to create payment intent: {str(e)}")
    
    def confirm_payment(self, payment_intent_id: str) -> Dict:
        """Confirm a real payment intent using direct API call"""
        try:
            print(f"DEBUG: Confirming payment intent: {payment_intent_id}")
            
            headers = {
                "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{STRIPE_API_BASE}/payment_intents/{payment_intent_id}",
                headers=headers
            )
            
            print(f"DEBUG: Stripe API response status: {response.status_code}")
            print(f"DEBUG: Stripe API response: {response.text[:200]}")
            
            if response.status_code != 200:
                raise Exception(f"Stripe API error: {response.status_code} - {response.text}")
            
            payment_intent_data = response.json()
            print(f"DEBUG: Payment intent data: {payment_intent_data}")
            
            return {
                "status": payment_intent_data["status"],
                "amount": payment_intent_data["amount"],
                "currency": payment_intent_data["currency"],
                "metadata": payment_intent_data.get("metadata", {})
            }
        except Exception as e:
            raise Exception(f"Failed to confirm payment: {str(e)}")
    
    def get_payment_history(self, provider_id: str = None, patient_id: str = None) -> list:
        """Get real payment history from Stripe"""
        try:
            filters = {}
            if provider_id:
                filters["metadata.provider_id"] = provider_id
            if patient_id:
                filters["metadata.patient_id"] = patient_id
                
            payments = stripe.PaymentIntent.list(
                limit=100,
                **filters
            )
            
            return [
                {
                    "payment_intent_id": payment.id,
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "status": payment.status,
                    "created": datetime.fromtimestamp(payment.created),
                    "metadata": payment.metadata
                }
                for payment in payments.data
            ]
        except Exception as e:
            raise Exception(f"Failed to get payment history: {str(e)}")

# Global instance
stripe_service = StripeService()
