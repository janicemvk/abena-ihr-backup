import React, { useState } from 'react';
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const PaymentForm = ({ onPaymentSuccess, onPaymentError, amount, clientSecret }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    console.log('🔍 PaymentForm: handleSubmit called');
    console.log('🔍 PaymentForm: stripe available:', !!stripe);
    console.log('🔍 PaymentForm: elements available:', !!elements);
    console.log('🔍 PaymentForm: clientSecret:', clientSecret);
    
    if (!stripe || !elements) {
      console.log('❌ PaymentForm: Stripe or Elements not available');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('🔍 PaymentForm: Calling stripe.confirmCardPayment...');
      const { error: submitError, paymentIntent } = await stripe.confirmCardPayment(
        clientSecret,
        {
          payment_method: {
            card: elements.getElement(CardElement),
          },
        }
      );

      console.log('🔍 PaymentForm: Payment result:', { submitError, paymentIntent });

      if (submitError) {
        console.log('❌ PaymentForm: Payment error:', submitError);
        setError(submitError.message);
        setLoading(false);
        onPaymentError(submitError.message);
      } else {
        console.log('✅ PaymentForm: Payment successful, calling onPaymentSuccess');
        setLoading(false);
        onPaymentSuccess();
      }
    } catch (error) {
      console.log('❌ PaymentForm: Exception during payment:', error);
      setError(error.message);
      setLoading(false);
      onPaymentError(error.message);
    }
  };

  const cardElementOptions = {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4',
        },
      },
      invalid: {
        color: '#9e2146',
      },
    },
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="p-4 border border-gray-300 rounded-lg">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Card Details
        </label>
        <CardElement options={cardElementOptions} />
      </div>
      
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
      
      <button
        type="submit"
        disabled={!stripe || loading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
      >
        {loading ? 'Processing Payment...' : `Pay $${(amount / 100).toFixed(2)}`}
      </button>
    </form>
  );
};

export default PaymentForm;
