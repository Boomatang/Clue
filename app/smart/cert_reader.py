# imports for pdf reading and converting
import time

import shutil
import uuid
import zipfile
from io import BytesIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

# standard imports
import sys
from pathlib import Path
import os

# imports to work with xml data
import xml.etree.ElementTree as ET
from math import floor
import re  # This is black magic

# data that is used will testing
from threading import Thread

from app import db
from app.models import Certs
from app.utils import count_files

from flask import current_app


LOG_REPORT = "__log_report.tsv"


def get_folder_path(folder):
    print(
        "\n **** Please enter the path to the folder where the certs are held,"
        " This should be a local or mapped drive. ****")

    output = folder
    output = folder_name(output)
    output = Path(output)

    if not output.is_dir():
        print("Please enter a real folder location.. \nSystem is exiting..")
        sys.exit(0)

    return output


def folder_name(folder_path):

    folder = trim_name(folder_path)
    # print(folder)
    return folder


def trim_name(name):
    if name.startswith('"') and name.endswith('"'):
        return name[1:-1]
    else:
        return name


# getting list of pdfs

def get_pdf_paths(path):
    excluded = ["COMBINED"]

    for root, dirs, files in os.walk(path):
        for exclude in excluded:
            if exclude in dirs:
                dirs.remove(exclude)

        for file in files:
            file = Path(os.path.join(root, file))

            if find_file_type(file.suffix):
                yield file


def find_file_type(suffix):
    types = [".pdf"]

    if suffix.lower() in types:
        return True
    else:
        return False


# this is to do with the pdf reading
def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = BytesIO()
    manager = PDFResourceManager()
    converter = XMLConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()
    return text


class PDF:
    def __init__(self, path, testing_state):
        self.file = path
        self.testing = testing_state
        self.xml = convert(self.file)
        self.xml_str = self.xml[:]
        self.pass_id = None
        self.id_name = None
        self.id_line_number = None
        self.description = None
        self.new_name = None

    def convert_to_xml_tree(self):
        self.xml = ET.fromstring(self.xml)

    def do_work(self):
        # print(self.file)
        self.convert_to_xml_tree()
        self.pass_id = int(self.find_pass_value())
        self.guess_id_number()
        self.find_description()
        self.make_new_file_name()
        # testing
        # self.save_as()

    def make_file_changes(self, log):
        with open(log, 'a') as info:
            try:
                name = Path(self.file.parent, self.new_name + ".pdf")
                self.file.replace(name)
                # print(Path(self.file.parent, self.new_name + ".pdf"))
                info.write(name.name + "\n")

            except OSError as err:
                print("Error renaming file ?")
                print(err)

    def make_new_file_name(self):
        self.new_name = self.description + " - " + self.id_name
        pattern = r"[\\\/\:\*\?\"\<\>\|\.\%]"
        self.new_name = re.sub(pattern, "_", self.new_name)
        self.new_name = re.sub(r"^-", "___", self.new_name)

    def find_description(self):
        line = self.id_line_number + 1
        word = None
        while line < self.pass_id:
            word = self.get_current_line(str(line))
            line += 1

        word = re.sub(r"\n", " ", word[:-1])
        self.description = word

    def get_current_line(self, line):
        for page in self.xml:
            for textbox in page.findall('textbox'):
                if textbox.get('id').startswith(line):
                    word = []
                    for textline in textbox:
                        for char in textline:
                            word.append(char.text)
                    return ''.join(word)

    def convert_to_number_test(self, text):
        numbers = 0
        half_length = floor(len(text) / 2) - 2
        for char in text[:-2]:
            if char.isdigit():
                numbers += 1

        if numbers > half_length:
            return text
        else:
            return None

    def guess_id_number(self):
        result_start = self.find_result_start()

        current_line = int(result_start) + 1

        while current_line < int(self.pass_id):

            possible_id = self.get_current_line(str(current_line))
            best_guess = self.convert_to_number_test(possible_id)

            if best_guess is not None:
                self.id_name = best_guess[:-1]
                self.id_line_number = current_line
                break

            current_line += 1

    def find_result_start(self):
        ids = None
        found = False
        test = "Location at which examination was made, if different"
        for page in self.xml:
            for textbox in page.findall('textbox'):
                if not found:
                    word = []
                    for textline in textbox:
                        for char in textline:
                            word.append(char.text)
                    word = ''.join(word)
                    if word.startswith(test):
                        ids = (word[:24], textbox.get('id'))
                        found = True
                        break
        if not found:
            print("Failed finding Test textbox id number")
            sys.exit(0)

        return ids[1]

    def find_pass_value(self):
        ids = []
        found = False

        for page in self.xml:
            for textbox in page.findall('textbox'):

                if not found:
                    word = []
                    for textline in textbox:
                        for char in textline:
                            word.append(char.text)
                    word = ''.join(word)
                    if len(word) == 5:
                        if word.startswith("Pass"):
                            ids.append((word[:4], textbox.get('id')))
                            found = True
                            break

        if not found:
            print("Failed finding pass textbox id number")
            sys.exit(0)

        return ids[0][1]

    def save_as(self):
        if self.testing:
            with open("{}.xml".format(self.file), "wb") as text:
                text.write(self.xml_str)
        else:
            pass

    def test_print(self):
        if self.xml is not None:
            print(self.xml.tag)
            for child in self.xml:
                for more in child:
                    print("tags : {} , att : {}".format(more.tag, more.attrib))


def cert_reader(folder_path):
    # main function for script
    root = get_folder_path(folder_path)
    print("Starting the process")
    print("Working Path : {}".format(root))
    pdf_paths = get_pdf_paths(root)
    x = 0

    log = str(Path(root, LOG_REPORT))

    for pdf in pdf_paths:
        if x < 996:
            work_body = PDF(pdf, False)
            work_body.do_work()
            work_body.make_file_changes(log)
            # work_body.test_print()
            x += 1
    print("Process Finished")


def run_cert_editing(entry_id, app):
    with app.app_context():
        start_time = time.time()
        db_entry: Certs = Certs.query.filter_by(id=entry_id).first_or_404()
        print(f"The db_entry ID = {db_entry.id}")

        # unpack the zip folder
        unzip_folder = os.path.join(os.environ.get('CLUE_UPLOADS', '/home/boomatang/Public'),
                                    'cert_uploads', str(uuid.uuid4()))

        zip_ref = zipfile.ZipFile(db_entry.upload_file, 'r')
        zip_ref.extractall(unzip_folder)
        zip_ref.close()

        # run the cert process
        db_entry.file_count = count_files(unzip_folder)
        cert_reader(unzip_folder)

        # repack the zip folder

        zip_name = unzip_folder
        shutil.make_archive(zip_name, 'zip', unzip_folder)

        db_entry.download_file = zip_name + ".zip"

        # doing some tidy up

        try:
            shutil.rmtree(unzip_folder)
            os.remove(db_entry.upload_file)
        except OSError:
            print("error will doing son house cleaning")

        db_entry.upload_file = None

        # finishing up
        finish_time = round(time.time() - start_time, 3)

        print(finish_time)

        db_entry.run_time = finish_time
        db.session.commit()


def run_cert_editing_async(cert_id, app):

    thr = Thread(target=run_cert_editing, args=[cert_id, app])
    thr.start()
    return thr


def cert_editing(cert_id):
    app = current_app._get_current_object()
    run_cert_editing_async(cert_id, app)

