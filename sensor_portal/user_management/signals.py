from data_models.models import Device
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework.authtoken.models import Token
from utils.email import send_email

from .models import DeviceUser, User


@receiver(pre_save, sender=User)
def on_change(sender, instance: User, **kwargs):
    from utils.email import send_email_to_user, send_email_to_users

    if instance.id is None:  # new object will be created
        # send email confirming registration
        send_email_to_user(instance,
                           f"Thanks for registering with {Site.objects.get_current().name}",
                           f"""You have succesfully registered with {Site.objects.get_current().name} \n
                           A member of staff will activate your account after review. \n
                           You will receive an email when you account is activated.""")
        # send email alerting staff of registration
        send_email_to_users(User.objects.filter(is_staff=True),
                            f"{instance.username} registered with {Site.objects.get_current().name}",
                            f"""{instance.first_name} {instance.last_name} registered with {Site.objects.get_current().name} \n
                           Their account will need to be activated after review. \n
                           """)
    else:
        previous = User.objects.get(id=instance.id)
        if previous.is_active != instance.is_active:  # field will be updated
            if instance.is_active:
                # Send email alerting user to their account
                send_email_to_user(instance,
                                   f"Thanks for registering with {Site.objects.get_current().name}",
                                   f"""Your account at {Site.objects.get_current().name} has been activated \n
                                Note that you may still need to be given additional permissions.""")
            else:
                # send email saying user account is deactivated?
                send_email_to_user(instance,
                                   f"Your account at {Site.objects.get_current().name}",
                                   f"""Your account at {Site.objects.get_current().name} has been deactivated \n
                If you feel this was an error, please contact your system administrator.""")
                pass


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    print("Password reset token created", sender)
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': f"{Site.objects.get_current().domain}/reset-password/confirm/?token={reset_password_token.key}"
    }

    # render email text
    email_html_message = render_to_string(
        'user_reset_password.html', context)

    send_email(reset_password_token.user.email,
               f"Password Reset for {reset_password_token.user.username}",
               email_html_message)


@receiver(post_save, sender=DeviceUser)
def check_device_user_is_manager(sender, instance, created, **kwargs):
    if not instance.device.managers.all().filter(pk=instance.pk).exists():
        instance.device.managers.add(instance)


@receiver(post_save, sender=Device)
def post_save_device(sender, instance, created, **kwargs):
    add_device_user = False
    if created:
        add_device_user = True
    else:
        try:
            device_user = instance.device_user
        except ObjectDoesNotExist:
            add_device_user = True

    if add_device_user:
        user_name = f"{instance.device_ID}_user"
        if (instance.username is not None) and (instance.username != ":"):
            user_name = instance.username
        device_user = DeviceUser(username=user_name,
                                 device=instance,
                                 is_active=True)
        if (instance.password is not None) and (instance.password != ""):
            device_user.password = instance.password
        if instance.owner:
            device_user.email = instance.owner.email
        device_user.save()

    # always make sure device user as a manager
    instance.managers.add(device_user)


@receiver(pre_save, sender=DeviceUser)
@receiver(pre_save, sender=User)
def pre_user_save(sender, instance, **kwargs):
    if isinstance(instance, DeviceUser):
        instance.is_active = True
    elif instance.is_superuser:
        instance.is_active = True


@receiver(post_save, sender=DeviceUser)
@receiver(post_save, sender=User)
def create_user_token(sender, instance, created, **kwargs):
    if created:
        newtoken = Token(user=instance)
        if isinstance(instance, DeviceUser):
            if (instance.device.password is None) or (instance.device.password != ""):
                instance.password = newtoken.key
        newtoken.save()
