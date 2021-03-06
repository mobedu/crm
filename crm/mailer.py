import os
import base64
import os.path
from collections import namedtuple

import email.utils
import email
from pyblake2 import blake2b
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail, Attachment as SendGridAttachment
from crm.settings import ATTACHMENTS_DIR, STATIC_URL_PATH, SENDGRID_API_KEY, SUPPORT_EMAIL
from flask_misaka import markdown


Attachment = namedtuple(
    'Attachment', [
        'hashedfilename',
        'hashedfilepath',
        'hashedfileurl',
        'originalfilename',
        'binarycontent',
        'type'
    ]
)


def build_attachment(attachment):
    """
    Returns a valid sendgrid attachment from typical attachment object.
    """
    sendgridattachment = SendGridAttachment()

    sendgridattachment.content = base64.b64encode(
        attachment.binarycontent
    ).decode()

    sendgridattachment.type = attachment.type
    sendgridattachment.filename = attachment.originalfilename
    sendgridattachment.disposition = "attachment"
    sendgridattachment.content_id = attachment.originalfilename
    return sendgridattachment


def parse_email_body(body):
    """
    Parses email body and searches for the attachements
    :return: (body, attachments)
    :rtype: tuple
    """

    message = email.message_from_string(body)

    if not message.is_multipart():
        return message.get_payload(decode=True).decode(), []

    body = ''
    attachments = []

    g = message.walk()

    next(g)  # SKIP THE ROOT ONE.
    for part in g:
        part_content_type = part.get_content_type()
        part_body = part.get_payload()

        part_filename = part.get_param(
            "filename",
            None,
            "content-disposition"
        )

        # make sure to check if gmail sends 2 versions always
        if part_content_type == "text/plain":
            body += part_body

        # part_content_type = "application/octet-stream" or application/json or whatever file
        elif part_filename is not None:
            bhash = blake2b()
            part_binary_content = part.get_payload(decode=True)
            bhash.update(part_binary_content)
            part_extension = os.path.splitext(part_filename)[1]
            hashedfilename = bhash.hexdigest() + part_extension

            hashedfilepath = os.path.join(
                ATTACHMENTS_DIR,
                hashedfilename
            )

            hashedfileurl = os.path.join(
                STATIC_URL_PATH,
                "uploads",
                "attachments",
                hashedfilename
            )

            attachments.append(
                Attachment(
                    hashedfilename=hashedfilename,
                    hashedfilepath=hashedfilepath,
                    hashedfileurl=hashedfileurl,
                    originalfilename=part_filename,
                    binarycontent=part_binary_content,
                    type=part_content_type)
            )

    return body, attachments


def sendemail(to=None, from_=None, subject=None, body=None, attachments=None, reply_to=None):
    """
    Send email

    :param to: receiver
    :param from_: sender
    :param subject: subject
    :param body: Email body
    :param attachments: Attachments
    """

    if to is None:
        to = []
    if attachments is None:
        attachments = []

    if not subject:
        subject = "User not recognized"

    if not body:
        body = "Please email support at %s" % SUPPORT_EMAIL

    to = list(set(to))  # no duplicates.
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    from_email = Email(from_ or SUPPORT_EMAIL)

    if reply_to is not None:
        from_email = Email(reply_to)

    to_email = Email(to[0])
    content = Content("text/html", markdown(body))

    mail = Mail(from_email, subject, to_email, content)
    if reply_to is not None:
        mail.reply_to = Email(reply_to)

    if len(to) > 1:
        for receiver in to[1:]:
            mail.personalizations[0].add_to(Email(receiver))

    for attachment in attachments:
        mail.add_attachment(build_attachment(attachment))
    try:
        print('Now trying to send an email')
        response = sg.client.mail.send.post(request_body=mail.get())
        print("Email sent.. %s" % response.status_code)
        return response.status_code, response.body
    except Exception as e:
        print(e)
        raise e
