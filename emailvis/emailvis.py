# -*- coding: utf-8 -*-
import os
import email
import pickle
import mimetypes
from flask import Flask
from flask import render_template


app = Flask(__name__)
app.config.from_object('emailvis.config')


class MessageDoesNotExist(Exception):
    pass


class EmailParser(object):

    def __init__(self,
                 input_directory=app.config['INPUT_DIR'],
                 output_directory=app.config['OUTPUT_DIR']):

        self.input_dir = input_directory
        self.output_dir = output_directory
        self.emails = []

    def extract_data_from_log(self):
        files = os.listdir(self.input_dir)
        self.create_output_directory()

        for f in files:
            try:
                email_id = self.write_in_disk(f)
                self.emails.append(email_id)
            except MessageDoesNotExist:
                pass

    @property
    def id_list(self):
        self.emails = []
        self.extract_data_from_log()
        return self.emails

    def load_email(self, email_id):
        with open(os.path.join(self.ouput_dir, email_id + '.headers')) as f:
            headers = pickle.load(f)

        email = dict(headers)

        content = []
        with open(os.path.join(self.output_dir, email_id + '.html')) as f:
            for line in f.readlines():
                content.append(line.strip())

        email['Content'] = "".join(content).decode('utf-8')
        return email

    def write_in_disk(self, f):
        msg = email.message_from_file(open(os.path.join(self.input_dir, f)))
        aux = msg.get("Message-ID")
        if aux and '@' in aux:
            aux = aux.split('@')[0]
            aux = aux[1:]  # only the id
            msg_id = aux.split('.')[0]
        else:
            raise MessageDoesNotExist

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            filename = part.get_filename()
            if not filename:
                ext = mimetypes.guess_extension(part.get_content_type())
                if not ext:
                    ext = '.bin'
                filename = '%s%s' % (msg_id, ext)
            with open(os.path.join(self.output_dir, filename), 'wb') as fp:
                fp.write(part.get_payload(decode=True))

        # we save the headers also:
        ext = ".headers"
        filename = '%s%s' % (msg_id, ext)
        with open(os.path.join(self.output_dir, filename), 'wb') as fp:
            pickle.dump(msg.items(), fp)

        return msg_id

    def create_output_directory(self):
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)


@app.route('/')
def main_app():
    emails = EmailParser()
    return render_template('visualization.html', emails=sorted(emails.id_list, reverse=True))


@app.route('/email/<email_id>')
def get_email(email_id):
    emails = EmailParser()
    return render_template('email.html', email=emails.load(email_id))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
