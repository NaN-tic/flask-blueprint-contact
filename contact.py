#This file is part contact blueprint for Flask.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from flask import Blueprint, request, render_template, flash, current_app
from flask_babel import lazy_gettext
from flask_wtf import Form
from flask_mail import Mail, Message
from wtforms import TextField, TextAreaField, validators
from galatea.tryton import tryton

contact = Blueprint('contact', __name__, template_folder='templates')


class ContactForm(Form):
    "Contact form"
    name = TextField(lazy_gettext('Name'), [validators.Required()])
    email = TextField(lazy_gettext('Email'), [validators.Required(), validators.Email()])
    phone = TextField(lazy_gettext('Phone'))
    description = TextAreaField(lazy_gettext('Description'), [validators.Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        return True

    def reset(self):
        self.description.data = ''

def send_email(data):
    """
    Send an contact email
    :param data: dict
    """
    mail = Mail(current_app)

    subject =  '%s - %s' % (current_app.config.get('TITLE'), _('New request'))
    email = current_app.config.get('DEFAULT_MAIL_SENDER')

    msg = Message(subject,
            body = render_template('emails/contact-text.jinja', data=data),
            html = render_template('emails/contact-html.jinja', data=data),
            sender = email,
            recipients = [email, data.get('email')])
    mail.send(msg)

@contact.route("/", methods=["GET", "POST"], endpoint="contact")
@tryton.transaction()
def contact_details(lang):
    form = ContactForm()
    if form.validate_on_submit():
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'description': request.form.get('description'),
            }
        send_email(data)
        flash(_('Your comment was submitted and will be answered to as soon ' \
            'as possible. Thank you for contacting us.'))
        form.reset()

    return render_template('contact.html', form=form)
