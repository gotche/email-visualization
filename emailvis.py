# -*- coding: utf-8 -*-
import os
import email
import pickle
import mimetypes
from flask import Flask
from flask import render_template


app = Flask(__name__)
app.debug = True
directory = '/tmp/email-messages'
output_directory = '/tmp/formatted-emails'


class MessageDoesNotExist(Exception):
    pass


def create_output_directory():
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)


def extract_info(f):
    msg = email.message_from_file(open(os.path.join(directory, f)))
    aux = msg.get("Message-ID")
    if aux and '@' in aux:
        aux = aux.split('@')[0]
        aux = aux[1:]  # only the id
        msg_id = aux.split('.')[0]
    else:
        raise MessageDoesNotExist

    counter = 1
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            if not ext:
                ext = '.bin'
            filename = '%s%s' % (msg_id, ext)
        counter += 1
        fp = open(os.path.join(output_directory, filename), 'wb')
        fp.write(part.get_payload(decode=True))
        fp.close()

    # we save the headers also:
    ext = ".headers"
    filename = '%s%s' % (msg_id, ext)
    fp = open(os.path.join(output_directory, filename), 'wb')
    pickle.dump(msg.items(), fp)
    fp.close()

    return msg_id


def extract_data_from_log(directory):
    emails = []
    files = os.listdir(directory)

    create_output_directory()

    for f in files:
        try:
            email_id = extract_info(f)
            emails.append(email_id)
        except MessageDoesNotExist:
            pass
    return emails


def load_email(email_id):
    with open(os.path.join(output_directory, email_id + '.headers')) as f:
        headers = pickle.load(f)

    email = dict(headers)

    content = []
    with open(os.path.join(output_directory, email_id + '.html')) as f:
        for line in f.readlines():
            content.append(line.strip())

    email['Content'] = "".join(content)

    # this is because the heart :)
    email['Content'] = email['Content'].decode('utf-8')
    return email


@app.route('/')
def main_app():
    emails = extract_data_from_log(directory)
    return render_template('visualization.html', emails=sorted(emails, reverse=True))


@app.route('/email/<email_id>')
def get_email(email_id):
    email = load_email(email_id)
    return render_template('email.html', email=email)


if __name__ == '__main__':
    #app.debug = True
    app.run(host='0.0.0.0')
