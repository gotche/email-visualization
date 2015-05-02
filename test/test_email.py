import os
from emailvis import EmailParser


def test_read_email(messages_directory, output_directory):
    emails = EmailParser(messages_directory, output_directory)
    assert len(emails.id_list) == 1


def test_write_in_disk(messages_directory, output_directory, email_file,
                       email_id):
    emails = EmailParser(messages_directory, output_directory)
    info = emails.write_in_disk(email_file)

    assert email_id == info
    assert os.path.isfile(os.path.join(output_directory, email_id + '.html'))
