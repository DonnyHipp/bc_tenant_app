from django.core.exceptions import ObjectDoesNotExist

from ..models import (
    User,
    MailingList,
    Message,
)


def get_user_or_mailing_list(email_or_list_name):
    try:
        user = User.objects.get(email=email_or_list_name)
        return [user]
    except ObjectDoesNotExist:
        try:
            mailing_list = MailingList.objects.get(name=email_or_list_name)
            return [mailing_list]
        except ObjectDoesNotExist:
            return None


def add_recipient_to_list(recipient, recipients_list):
    if recipient and recipient not in recipients_list:
        recipients_list.append(recipient)


def check_mes(request):
    mail_list = [s.strip() for s in request.POST.get("mail_list", "").split(";")]
    mail_list = list(filter(lambda x: x != "", mail_list))
    mail_text = request.POST.get("mail_text", "")
    mail_subject = request.POST.get("subject", "")

    mail_res_list = {}

    for email_or_list_name in mail_list:
        user_or_mailing_list = get_user_or_mailing_list(email_or_list_name)
        if user_or_mailing_list not in mail_res_list:
            mail_res_list.append(user_or_mailing_list)

    if mail_res_list:
        message = Message(
            message=mail_text,
            subject=mail_subject,
            sender=request.user
            )
        if "file" in request.FILES:
            message.file = request.FILES["file"]
        message.save()
        message.recipients.set(mail_res_list)
        message.save()
        return True, ""
    else:
        return False, "Произошла ошибка!"
