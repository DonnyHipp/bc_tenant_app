from .models import *


def check_mes(request):
    res_list = [s.strip() for s in request.POST["mail_list"].split(";")]
    res_list = list(filter(lambda x: x != "", res_list))
    mail_text = request.POST["mail_text"]
    mail_subject = request.POST["subject"]

    mail_res_list = []

    for i in res_list:
        if User.objects.filter(email=i).exists():
            if User.objects.get(email=i) not in mail_res_list:
                mail_res_list.append(User.objects.get(email=i))
        elif MailingList.objects.filter(name=i).exists():
            dl = MailingList.objects.get(name=i)
            if dl.members.all():
                for us in dl.members.all():
                    if us not in mail_res_list:
                        mail_res_list.append(us)
        else:
            return (
                False,
                f"Произошла ошибка, пользователя {i} не существует, или рассылки с данным именем нет.",
            )

    if mail_res_list:
        message = Message(message=mail_text, subject=mail_subject, sender=request.user)
        if "file" in request.FILES:
            message.file = request.FILES["file"]
        message.save()
        message.recipients.set(mail_res_list)
        message.save()
    else:
        return False, "Произошла ошибка!"
    return True, ""
