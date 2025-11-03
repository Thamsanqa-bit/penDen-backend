from orders.models import Order
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def send_order_email_notification(sender, instance, created, **kwargs):
    """
    Send email notification when an order is created or updated
    """
    try:
        # Safety check: Ensure the order has a user and the user has an email
        if not instance.user or not instance.user.user or not instance.user.user.email:
            logger.warning(f"Cannot send email for order {instance.id}: Missing user or email")
            return

        if created:
            # New order created
            send_order_confirmation_email(instance)
        else:
            # Order updated
            send_order_update_email(instance)
    except Exception as e:
        logger.error(f"Error sending order email notification for order {instance.id}: {str(e)}")


@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance, **kwargs):
    """
    Handle pre-save logic for orders
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            # You can compare old and new values here if needed
            # For example, track status changes
        except Order.DoesNotExist:
            pass


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer
    """
    try:
        subject = f"Order Confirmation - #{order.id}"

        # Get the email with safety checks
        if not order.user.user.email:
            logger.error(f"Cannot send confirmation email: No email for user {order.user.user.username}")
            return

        recipient_email = order.user.user.email

        # HTML email content
        html_message = render_to_string('orders/email/order_confirmation.html', {
            'order': order,
            'user': order.user.user,  # The actual User object
            'user_profile': order.user  # The UserProfile object
        })

        # Plain text fallback
        plain_message = f"""
Thank you for your order!

Order ID: #{order.id}
Total Amount: ${order.total_amount}
Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}

Shipping Address:
{order.address}

We'll notify you when your order ships.

Thank you for shopping with us!
"""

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Order confirmation email sent for order #{order.id} to {recipient_email}")

    except Exception as e:
        logger.error(f"Error sending order confirmation email for order {order.id}: {str(e)}")


def send_order_update_email(order):
    """
    Send order status update email
    """
    try:
        subject = f"Order Update - #{order.id}"

        # Get the email with safety checks
        if not order.user.user.email:
            logger.error(f"Cannot send update email: No email for user {order.user.user.username}")
            return

        recipient_email = order.user.user.email

        html_message = render_to_string('orders/email/order_update.html', {
            'order': order,
            'user': order.user.user,
            'user_profile': order.user
        })

        plain_message = f"""
Your order has been updated!

Order ID: #{order.id}
Status: {order.get_status_display()}
Total Amount: ${order.total_amount}

Please check your account for details.

Thank you,
The Store Team
"""

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Order update email sent for order #{order.id} to {recipient_email}")

    except Exception as e:
        logger.error(f"Error sending order update email for order {order.id}: {str(e)}")


# Optional: Send email to admin for new orders
@receiver(post_save, sender=Order)
def notify_admin_new_order(sender, instance, created, **kwargs):
    """
    Send notification to admin about new order
    """
    if created:
        try:
            send_admin_order_notification(instance)
        except Exception as e:
            logger.error(f"Error sending admin notification for order {instance.id}: {str(e)}")


def send_admin_order_notification(order):
    """
    Send notification to admin about new order
    """
    subject = f"New Order Received - #{order.id}"

    customer_info = f"{order.user.user.username} ({order.user.user.email})" if order.user and order.user.user else "Unknown customer"

    message = f"""
New order received!

Order ID: #{order.id}
Customer: {customer_info}
Total Amount: ${order.total_amount}
Order Date: {order.created_at}

Please process this order promptly.
"""

    # Send to admin email(s)
    admin_emails = [admin[1] for admin in settings.ADMINS] if hasattr(settings, 'ADMINS') else ['admin@example.com']

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=admin_emails,
        fail_silently=False,
    )

    logger.info(f"Admin notification sent for order #{order.id}")